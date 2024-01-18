import os
import time
from datetime import datetime
from copy import copy
import pytesseract
import cv2
import numpy as np
from PIL import Image
#
from app.config.config import settings
from app.utils.utils import remove_control_chars, progress_bar
from app.database import Images



class ImageReader:
    def __init__(self, dbase) -> None:
        # self.processor: object = settings.TESSERACT_BIN
        self.db = dbase
        self.users: dict = {}
        self.admins: list = []
        self.super_admin: str = None
        self.photo_text_dict: dict = {}
        self.img_count: int = 0
        self.precision: float = 0

        # pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_BIN
        if os.path.exists(settings.PROC_IMAGES_FOLDER):
            self.proc_image_folder: str = settings.PROC_IMAGES_FOLDER
        else:
            os.mkdir(settings.PROC_IMAGES_FOLDER)
            self.proc_image_folder: str = settings.PROC_IMAGES_FOLDER


    def update_info(self) -> None:
        self.users = {
            user.username: {"id": user.id, "role": user.role}
            for user in self.db.get_users()
        }
        self.admins = [user for user in self.users.values() if user["role"] == "admin"]

        if (
            any(user["role"] == "superadmin" for user in self.users.values())
            and not self.super_admin
        ):
            self.super_admin = [
                username
                for username, user_data in self.users.items()
                if user_data.get("role") == "superadmin"
            ][0]
            self.admins.append(self.super_admin)

        attributes = [attributes.to_dict() for attributes in self.db.get_main_conf()]
        self.img_count, self.precision = attributes[0]["img_proc_count"], attributes[0]["precision"]
        images = [image_instance.to_dict() for image_instance in self.db.get_images()]
        self.photo_text_dict = {image["file_name"]: image["recog_text"] for image in images}

        print("[#] ImageReader info updated")


    def add_superadmin(self, username) -> None:
        self.super_admin = username
        self.admins.append(self.super_admin)


    def fill_table(self, verbose=False) -> None:
        files_to_work = os.listdir(settings.STORED_IMAGES_FOLDER)
        approx_time = round(len(files_to_work)*3, 2)
        print(
            f"+{'='*72}+\n"
            "[*] Filling database with OCR data...\n"
            f"[#] Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"[#] Verbose: {'Yes' if verbose else 'No'}\n"
            f"[#] Number of images to process: {len(files_to_work)}\n"
            f"[#] Approximate time: {approx_time} s (~{round(approx_time / 60.0)} mins)"
        )

        image_data_list = []

        for idx, file_name in enumerate(files_to_work):
            if not verbose:
                print(
                    f"[*] Processed images: {idx}/{len(files_to_work)} ",
                    f"{progress_bar(idx, len(files_to_work))}",
                    end="\r"
                )
            if file_name.endswith(".jpg"):
                image_path = os.path.join(settings.STORED_IMAGES_FOLDER, file_name)

                if verbose:
                    print(
                        f"+{'-'*72}+\n"
                        f"[*] Processing {file_name}...")

                conf, best_scale_factor, tot_time = self.evaluate_ocr_parameters(image_path)

                if verbose:
                    print(
                        f"[#] \t{'Best confidence':<23}: {conf}\n"
                        f"[#] \t{'Best scale factor':<23}: {best_scale_factor}\n"
                        f"[#] \t{'Evaluation time':<23}: {tot_time} s"
                    )

                preprocessed_image = self.preprocess_image(
                    image_path,
                    fxfy=best_scale_factor
                )

                result = self.recognize_text(preprocessed_image)
                recognized_text = " ".join(result["text"])

                image_data_list.append(
                    Images(file_name=file_name, recog_text=recognized_text)
                )

                self.photo_text_dict[file_name] = recognized_text
                self.img_count += 1

        self.db.save_image_data_batch(image_data_list)
        self.db.update_attr(count=self.img_count)

        print(
            f"[#] Filling complete, processed {len(files_to_work)} images\n"
            f"+{'='*72}+"
        )


    def preprocess_image(self, image_path, fxfy=2) -> np.ndarray:
        try:
            img = cv2.imread(image_path)

        except (IOError, SyntaxError):
            print(f"[!] Bad file '{image_path}', skipping...")
            return

        #resize
        img = cv2.resize(
            src=img,
            dsize=None,
            fx=fxfy,
            fy=fxfy
        )

        #grayscale
        gray_image = cv2.cvtColor(
            src=img,
            code=cv2.COLOR_BGR2GRAY
        )

        # denoise
        kernel = np.ones((3,5), np.uint8)
        denoised_image = cv2.morphologyEx(
            src=gray_image,
            op=cv2.MORPH_OPEN,
            kernel=kernel
        )

        return denoised_image


    def evaluate_ocr_parameters(self, image_path) -> tuple:
        start_total_time = time.time()
        best_confidence = 0

        fxfy_values = list(range(1, 6))

        for fxfy in fxfy_values:
            preprocessed_image = self.preprocess_image(
                image_path=image_path,
                fxfy=fxfy
            )

            result = self.recognize_text(preprocessed_image)
            confidence = round(sum(result["conf"]) / len(result["conf"]), 4)

            if confidence > best_confidence:
                best_confidence = confidence
                best_scale_factor = fxfy

        total_time = round(time.time() - start_total_time, 4)

        return best_confidence, best_scale_factor, total_time


    def recognize_text(self, image) -> dict:
        config = f'--oem 3 --psm 12'

        return pytesseract.image_to_data(
            image,
            lang="ukr+eng",
            config=config,
            output_type="dict"
        )


    def return_info(self) -> str:
        admins_info = f"Admins:\n<b>{''.join(self.admins)}</b>\n" if self.admins else ""

        users_info = [user for user in self.users.keys() if user not in self.admins]
        users_to_print = (
            f"Allowed Users:\n<b>{''.join(users_info)}</b>" if users_info else ""
        )

        return f"------------\nImages processed: <b>{self.img_count}</b>\nPrecision: <b>{self.precision}</b>\n{admins_info}{users_to_print}\n------------"


    async def compare(self, file) -> dict:
        recog_text = self.recognize_text(
            Image.open(
                f"{os.path.dirname(os.path.realpath(__file__))}\\img_processing\\{file}.jpg"
            )
        )["text"]
        recog_text_no_spaces = recog_text.replace(" ", "")
        chars_recog_text_no_spaces = [
            char for char in remove_control_chars(recog_text_no_spaces)
        ]
        diff_dict = {}
        work_with_dict = self.photo_text_dict
        for file_name in copy(work_with_dict).keys():
            if work_with_dict[file_name] == "":
                work_with_dict.pop(file_name, None)
        for file_name, txt in work_with_dict.items():
            txt_no_spaces = txt.replace(" ", "")
            chars_txt_no_spaces = [char for char in txt_no_spaces]
            len1 = len(chars_recog_text_no_spaces)
            len2 = len(chars_txt_no_spaces)
            diff = abs(len1 - len2)
            if len1 > len2:
                chars_recog_text_no_spaces = chars_recog_text_no_spaces[: len1 - diff]
            elif len2 > len1:
                chars_txt_no_spaces = chars_txt_no_spaces[: len2 - diff]
            num = 0
            for i, char in enumerate(chars_recog_text_no_spaces):
                if char != chars_txt_no_spaces[i]:
                    num += 1
            if (len(recog_text_no_spaces) - num - diff) / len(
                recog_text_no_spaces
            ) > 0.8:
                print(
                    f"File {file_name} is very likely to be the answer, the difference is {round(1 - (len(recog_text_no_spaces)-num-diff)/len(recog_text_no_spaces), 4)*100}%"
                )
            diff_dict.update({file_name: int(num + diff)})

        return diff_dict
