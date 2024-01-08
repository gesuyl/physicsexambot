

class ImageReader:
    def __init__(self, ls):
        self.img_count: int = ls[0]
        self.admins: list = get_admins(ls[1])
        self.users: dict = ls[1]
        self.processor: object = pytesseract

        if os.path.exists(IMG_PATH):
            self.img_directory = IMG_PATH
        else:
            os.mkdir(IMG_PATH)
            self.img_directory = IMG_PATH
        with codecs.open('photo_text_dict.txt', 'r', 'utf-8') as f:
            # {"file_name":"text"}
            self.photo_text_dict: dict = literal_eval(f.read())

    def __str__(self):
        return 'ok'

    def recognize(self, image_path):
        self.img_count += 1
        return self.processor.image_to_string(Image.open(image_path), lang='ukr+eng')

    def return_info(self):
        admins = '\n'.join(self.admins)
        usars = '\n'.join([x for x in (self.users) if x not in self.admins])
        txt = "------------\n"
        txt += f"Images processed: <b>{self.img_count}</b>\n"
        txt += f"Admins:\n<b>{admins}</b>\n"
        txt += f"Allowed Users:\n<b>{usars}</b>"
        txt += "\n------------"
        return txt

    def save_config(self):
        # {"admins": ["0"], "info" : {"img_proc_count": 0}, "allowed_users": []}
        conf = {
            "reader_info": {"img_proc_count": self.img_count},
            "users": self.users
        }

        with open('config.txt', 'w')as f:
            f.write(dumps(conf))
        print('Saved config successfully')

    async def compare(self, file):
        recog_text = self.recognize(f"{os.path.dirname(os.path.realpath(__file__))}\\img_processing\\{file}.jpg")
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