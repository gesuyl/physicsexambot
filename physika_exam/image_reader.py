import os
import time
from copy import copy
import itertools
import pytesseract
import cv2
import numpy as np
from PIL import Image
from tabulate import tabulate
from const import ImgProcConstants
from utils import remove_control_chars
from database import ImageData



class ImageReader:
    def __init__(self, dbase):
        self.processor: object = ImgProcConstants.TESSERACT_CMD
        self.db = dbase
        # pytesseract.pytesseract.tesseract_cmd = ImgProcConstants.TESSERACT_CMD
        if os.path.exists(ImgProcConstants.IMG_PATH):
            self.working_img_dir: str = ImgProcConstants.IMG_PATH
        else:
            os.mkdir(ImgProcConstants.IMG_PATH)
            self.working_img_dir: str = ImgProcConstants.IMG_PATH


    def update_info(self):
        self.users: dict = {user.username: {
                                    "id": user.id,
                                    "role": user.role
                                    }
                            for user in self.db.get_users()
                            }
        self.admins: list = [user for user in self.users.values() if user["role"] == "Admin"]
        self.img_count: int = self.db.get_image_processing_count()
        self.precision: float = self.db.get_precision()
        self.photo_text_dict: dict = self.db.get_image_data()


    def fill_db(self):
        image_data_list = []
        tabulate_data = []
        tabulate_headers = ["Filename", "Confidence", "Recognized Text"]
        first_iter = True

        for file_name in os.listdir(ImgProcConstants.STORED_IMAGES_FOLDER):
            if file_name.endswith('.jpg'):
                image_path = os.path.join(ImgProcConstants.STORED_IMAGES_FOLDER, file_name)

                if first_iter:
                    first_iter = False
                    
                    print("Evaluating OCR parameters")
                    
                    conf, param, time = self.evaluate_ocr_confidence(image_path)
                    
                    print("Evaluation complete")
                    print(f"Best confidence: {conf}\nBest parameters: {param}\nTotal time: {time}s\n")
                
                result = pytesseract.image_to_string(Image.open(image_path), lang="ukr+eng", output_type='dict')

                recognized_text = result['text']
                confidence = result['conf']

                image_data_list.append(ImageData(file_name=file_name, recog_text=recognized_text))

                max_text_length = 30  
                cropped_text = recognized_text[:max_text_length] + '...' if len(recognized_text) > max_text_length else recognized_text

                tabulate_data.append([file_name, confidence, cropped_text])

                self.photo_text_dict[file_name] = recognized_text
                self.img_count += 1

        print(tabulate(tabulate_data, headers=tabulate_headers, tablefmt="fancy_grid", showindex="always"))

        self.db.save_image_data_batch(image_data_list)
        self.db.update_attr(count=self.img_count)


    def preprocess_image(self, image_path):
        #enhance
        enhanced_image = cv2.convertScaleAbs(Image.open(image_path), alpha=1.5, beta=30)

        #binarize
        gray_image = cv2.cvtColor(enhanced_image, cv2.COLOR_BGR2GRAY)
        binary_image = cv2.adaptiveThreshold(gray_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        
        #denoise
        kernel = np.ones((3, 3), np.uint8)
        denoised_image = cv2.morphologyEx(binary_image, cv2.MORPH_OPEN, kernel)

        return denoised_image


    def evaluate_ocr_confidence(self, image_path):
        start_total_time = time.time()
        
        alpha_values = (round(x, 1) for x in itertools.chain(range(10, 21), range(11, 21, 2)))
        beta_values = range(21)
        kernel_sizes = itertools.product(range(3, 10, 2), repeat=2)
        best_confidence = 0
        best_parameters = {}

        for alpha in alpha_values:
            for beta in beta_values:
                for kernel_size in kernel_sizes:
                    preprocessed_image = self.preprocess_image(image_path, alpha, beta, kernel_size)

                    result = self.recognize_text(preprocessed_image)
                    confidence = result['conf']

                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_parameters = {'alpha': alpha, 'beta': beta, 'kernel_size': kernel_size}

        total_time = time.time() - start_total_time

        return best_confidence, best_parameters, total_time
    

    def recognize_text(self, image):
        return pytesseract.image_to_string(image, lang='ukr+eng', output_type='dict')


    def return_info(self):
        admins_info = f"Admins:\n<b>{''.join(self.admins)}</b>\n" if self.admins else ""

        users_info = [user for user in self.users.keys() if user not in self.admins]
        users_to_print = f"Allowed Users:\n<b>{''.join(users_info)}</b>" if users_info else ""
        
        return f"------------\nImages processed: <b>{self.img_count}</b>\n{admins_info}{users_to_print}\n------------"


    async def compare(self, file):
        recog_text = self.recognize_text(Image.open(f"{os.path.dirname(os.path.realpath(__file__))}\\img_processing\\{file}.jpg"))['text']
        recog_text_no_spaces = recog_text.replace(' ', '')
        chars_recog_text_no_spaces = [
            char for char in remove_control_chars(recog_text_no_spaces)]
        diff_dict = {}
        work_with_dict = self.photo_text_dict
        for file_name in copy(work_with_dict).keys():
            if work_with_dict[file_name] == "":
                work_with_dict.pop(file_name, None)
        for file_name, txt in work_with_dict.items():
            txt_no_spaces = txt.replace(' ', '')
            chars_txt_no_spaces = [char for char in txt_no_spaces]
            len1 = len(chars_recog_text_no_spaces)
            len2 = len(chars_txt_no_spaces)
            diff = abs(len1 - len2)
            if len1 > len2:
                chars_recog_text_no_spaces = chars_recog_text_no_spaces[:len1-diff]
            elif len2 > len1:
                chars_txt_no_spaces = chars_txt_no_spaces[:len2-diff]
            num = 0
            for i, char in enumerate(chars_recog_text_no_spaces):
                if char != chars_txt_no_spaces[i]:
                    num += 1
            if (len(recog_text_no_spaces)-num-diff)/len(recog_text_no_spaces) > 0.8:
                print(f"File {file_name} is very likely to be the answer, the difference is {round(1 - (len(recog_text_no_spaces)-num-diff)/len(recog_text_no_spaces), 4)*100}%")
            diff_dict.update({
                file_name: int(num+diff)
            })

        return diff_dict