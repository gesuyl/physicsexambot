#!/usr/bin/python3

import pytesseract
from aiogram import Bot, Dispatcher, executor, types
from ast import literal_eval
from json import dumps
from copy import copy
import sys
from _winapi import ExitProcess, GetCurrentProcess
from PIL import Image
import os
import codecs
from time import time


def main_vars():
    STORED_IMAGES_FOLDER = f"{os.path.dirname(os.path.realpath(__file__))}\\img_processing\\stored_images"
    IMG_PATH = f"{os.path.dirname(os.path.realpath(__file__))}\\img_processing"
    pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

    token = os.getenv('TGBOT_API_TOKEN')
    if token:
        bot = Bot(token=token)
        dp = Dispatcher(bot)
    else:
        print("Token not found in the environment variable.")


def check_init():
    try:
        v = str(TesseractReader)
        return True
    except NameError as ERROR:
        return False


def answer_kb(dd, current_file_name):
    dd.pop(current_file_name, None)
    if len(list(dd.values())) != 0:
        next_file_name = list(dd.keys())[list(
            dd.values()).index(min(list(dd.values())))]
    else:
        next_file_name = 'last'

    msg = types.InlineKeyboardButton(text='Правильно?', callback_data='None')
    up = types.InlineKeyboardButton(text='✅', callback_data='correct')
    down = types.InlineKeyboardButton(text='❌', callback_data=f'not_correct#{next_file_name}')

    return types.InlineKeyboardMarkup(row_width=4).add(msg).add(up, down)


def delete_button(kb=None):
    if kb == None:
        kb = types.InlineKeyboardMarkup(row_width=4).add(
            types.InlineKeyboardButton(text='❌', callback_data='delete'))
    else:
        kb.add(types.InlineKeyboardButton(text='❌', callback_data='delete'))
    return kb


def read_config(file):
    with open(file, 'r') as f:
        conf = literal_eval(f.read())
    return [
        conf["reader_info"]["img_proc_count"],
        conf["users"]
    ]


def remove_control_chars(s):
    escapes = ''.join([chr(char) for char in range(1, 32)])
    translator = str.maketrans('', '', escapes)
    return s.translate(translator)


def get_admins(mydict):
    admins = []
    for user in list(mydict.keys()):
        if mydict[user]["role"] == "admin":
            print(''.join(user))
            admins.append(''.join(user))
    return admins


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


@dp.message_handler(commands='info', commands_prefix='!/')
async def info(message):
    await bot.send_message(chat_id=message.chat.id,
                           text=TesseractReader.return_info(),
                           parse_mode='HTML',
                           reply_markup=delete_button())


@dp.message_handler(commands='add', commands_prefix='!/')
async def add(message):
    if not check_init():
        return
    if str(message.from_user.username) in TesseractReader.admins:
        print('admin')
        pass
    else:
        print('not_admin')
        return

    print(message.__dict__)
    if message.reply_to_message.from_user.username not in TesseractReader.users.keys():
        TesseractReader.users[message.reply_to_message.from_user.username].update({
            "id": message.reply_to_message.from_user.id,
            "role": "user"
        })
        txt = f"Added @{message.reply_to_message.from_user.username}"
    else:
        txt = f"@{message.reply_to_message.from_user.username} is already on the list"
    await bot.send_message(chat_id=message.chat.id,
                           text=txt,
                           reply_markup=delete_button())


@dp.message_handler(commands='start', commands_prefix='!/')
async def init(message):
    if not check_init():
        TesseractReader = ImageReader(read_config('config.txt'))

    print('Reader initialized succesfully!')
    await bot.send_message(chat_id=message.chat.id,
                           text='hi',
                           parse_mode='HTML',
                           reply_markup=delete_button())


@dp.message_handler(commands='stop', commands_prefix='!/')
async def stop(message):
    if not check_init():
        return
    if str(message.from_user.username) in TesseractReader.admins:
        pass
    else:
        return
    TesseractReader.save_config()
    await bot.send_message(chat_id=message.chat.id,
                           text="Stopped")
    ExitProcess(GetCurrentProcess())


@dp.message_handler(commands='restart', commands_prefix='!/')
async def restart(message):
    if not check_init():
        return
    if str(message.from_user.username) in TesseractReader.admins:
        pass
    else:
        return
    TesseractReader.save_config()
    await bot.send_message(chat_id=message.chat.id,
                           text="Restarting..")
    os.execv(sys.executable, ['python', __file__])


@dp.message_handler(content_types=['photo', 'document'])
async def handle_photo(message):
    if not check_init():
        return
    if str(message.from_user.username) not in TesseractReader.users.keys() and str(message.from_user.username) not in TesseractReader.admins:
        await bot.send_message(chat_id=message.chat.id,
                               text="You're not on the list",
                               reply_markup=delete_button())
        return
    else:
        if 'photo' in message.__dict__['_values'].keys():
            print(f'Received an image from @{message.from_user.username}')
            file_name = message.__dict__[
                '_values']['photo'][-1].__dict__["_values"]["file_unique_id"]
            await message.photo[-1].download(f'{os.path.dirname(os.path.realpath(__file__))}\\img_processing\\{file_name}.jpg')

        elif 'document' in message.__dict__['_values'].keys():
            print(f'Received a document from @{message.from_user.username}')
            file_name = message.__dict__['_values']['document'].__dict__[
                "_values"]["file_unique_id"]
            await message.document.download(f'{os.path.dirname(os.path.realpath(__file__))}\\img_processing\\{file_name}.jpg')

        diff_dict = await TesseractReader.compare(file_name)
        first_file = list(diff_dict.keys())[list(
            diff_dict.values()).index(min(list(diff_dict.values())))]

        await bot.send_photo(chat_id=message.chat.id,
                             photo=types.InputFile(f"{STORED_IMAGES_FOLDER}\\{first_file}"),
                             reply_markup=answer_kb(diff_dict, first_file))


@dp.callback_query_handler()
async def callback(call):
    if call.data == 'correct':
        await bot.answer_callback_query(callback_query_id=call.id,
                                        show_alert=False,
                                        text="Супер!")

        await bot.edit_message_reply_markup(chat_id=call.message.chat.id,
                                            message_id=call.message.message_id,
                                            reply_markup=None)
    elif 'not_correct' in call.data:
        next_img = call.data.split('#')[1]
        if next_img != "last":
            await bot.delete_message(chat_id=call.message.chat.id,
                                     message_id=call.message.message_id)
            await bot.send_photo(chat_id=call.message.chat.id,
                                 photo=types.InputFile(f"{STORED_IMAGES_FOLDER}\\{next_img}"),
                                 reply_markup=answer_kb(diff_dict, next_img))
        elif next_img == "last":
            await bot.delete_message(chat_id=call.message.chat.id,
                                     message_id=call.message.message_id)
            await bot.send_message(chat_id=call.message.chat.id,
                                   text="Твоей задачи нет в базе((",
                                   reply_markup=delete_button())

    elif call.data == 'delete':
        await bot.delete_message(chat_id=call.message.chat.id,
                                 message_id=call.message.message_id)


if __name__ == '__main__':
    print('All good!')
    executor.start_polling(dp, skip_updates=True)

    try:
        TesseractReader.save_config()

    except NameError as ERROR:
        print("Reader not initialized, can't save config")
