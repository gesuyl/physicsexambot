from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup



class Keyboard:

    @staticmethod
    def answer_kb(dd: dict, current_file_name: str) -> InlineKeyboardMarkup:
        """
        TBD

        :param dd: dict
        :param current_file_name: str
        
        :return: InlineKeyboardMarkup
        FIXME: This method is not working properly
        """
        dd.pop(current_file_name, None)
        next_file_name = min(dd, key=dd.get, default='last')

        buttons = [
            [
                InlineKeyboardButton(text='Правильно?', callback_data='None')
            ],
            [
                InlineKeyboardButton(text='✅', callback_data='correct'),
                InlineKeyboardButton(text='❌', callback_data=f'not_correct#{next_file_name}')
            ]
        ]

        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

        return keyboard


    @staticmethod
    def add_delete_button(keyboard: InlineKeyboardMarkup = None) -> InlineKeyboardMarkup:
        """
        Create keyboard with button '❌' or add button to existing keyboard
        
        :param keyboard: InlineKeyboardMarkup
        
        :return: InlineKeyboardMarkup
        """
        buttons = [
            [
                InlineKeyboardButton(text='❌', callback_data='delete')
            ]
        ]

        if keyboard is None:
            keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        else:
            keyboard.add(*buttons)
        return keyboard


    @staticmethod
    def yes_no_keyboard(command: str) -> InlineKeyboardMarkup:
        """
        Create keyboard with buttons 'Yes' and 'No'

        :param command: str

        :return: InlineKeyboardMarkup
        """
        buttons = [
            [
                InlineKeyboardButton(text='Yes', callback_data=f'{command}_yes'),
                InlineKeyboardButton(text='No', callback_data=f'{command}_no')
            ]
        ]

        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        return keyboard
