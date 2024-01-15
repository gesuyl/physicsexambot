from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


class Keyboard:

    @staticmethod
    def answer_kb(dd, current_file_name):
        dd.pop(current_file_name, None)
        next_file_name = min(dd, key=dd.get, default='last')

        buttons = [
            [InlineKeyboardButton(text='Правильно?', callback_data='None')],
            [
                InlineKeyboardButton(text='✅', callback_data='correct'),
                InlineKeyboardButton(text='❌', callback_data=f'not_correct#{next_file_name}')
            ]
        ]

        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

        return keyboard
    

    @staticmethod
    def add_delete_button(keyboard: InlineKeyboardMarkup = None):
        buttons = [[InlineKeyboardButton(text='❌', callback_data='delete')]]
        if keyboard is None:
            keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        else:
            keyboard.add(*buttons)
        return keyboard