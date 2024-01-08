from ast import literal_eval
from json import dumps
from copy import copy
from image_reader import ImageReader

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
            admins.append(''.join(user))
    return admins

def check_init():
    try:
        v = str(ImageReader)
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