#!/usr/bin/python3
from aiogram import Bot, Dispatcher, executor
from os import getenv
from image_reader import ImageReader
from database import Database
from handlers import dp


def main():
    db_url = "sqlite:///physexambot.db"
    db = Database(db_url)
    api_token = getenv('TGBOT_API_TOKEN')
    if api_token:
        bot = Bot(token=api_token)
        dp = Dispatcher(bot)
    else:
        print("Token not found in the environment variable.")
        exit()
    
    tesseract_reader = ImageReader()
    executor.start_polling(dp, skip_updates=True)

if __name__ == '__main__':
    main()
