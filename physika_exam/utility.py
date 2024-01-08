from ast import literal_eval
from json import dumps
from copy import copy
from image_reader import ImageReader
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def remove_control_chars(s):
    escapes = ''.join([chr(char) for char in range(1, 32)])
    translator = str.maketrans('', '', escapes)
    return s.translate(translator)


class Keyboard:
    @staticmethod
    def answer_kb(dd, current_file_name):
        dd.pop(current_file_name, None)
        next_file_name = min(dd, key=dd.get, default='last')

        buttons = [
            InlineKeyboardButton(text='Правильно?', callback_data='None'),
            InlineKeyboardButton(text='✅', callback_data='correct'),
            InlineKeyboardButton(text='❌', callback_data=f'not_correct#{next_file_name}')
        ]

        return InlineKeyboardMarkup(row_width=4).add(*buttons)

    @staticmethod
    def delete_button(kb=None):
        if kb is None:
            kb = InlineKeyboardMarkup(row_width=4)

        kb.add(InlineKeyboardButton(text='❌', callback_data='delete'))
        return kb