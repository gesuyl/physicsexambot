#!/usr/bin/python3
from aiogram import Bot, Dispatcher, executor
from handlers import dp
from time import time
from os import getenv
from image_reader import ImageReader

if __name__ == '__main__':
    token = getenv('TGBOT_API_TOKEN')
    if token:
        bot = Bot(token=token)
        dp = Dispatcher(bot)
    else:
        print("Token not found in the environment variable.")
        exit()
    
    tesseract_reader = ImageReader(read_config('config.txt'))

    try:
        tesseract_reader.save_config()
        executor.start_polling(dp, skip_updates=True)


    except NameError as ERROR:
        print("Reader not initialized, can't save config")
