#!/usr/bin/python3
from aiogram import Bot, Dispatcher
from os import getenv
import asyncio
from image_reader import ImageReader
from database import Database
from config_reader import config


def main():
    db_url = "sqlite:///physexambot.db"
    db = Database(db_url)

    tesseract_reader = ImageReader(db)
    tesseract_reader.update_info()

    bot = Bot(token=config.BOT_TOKEN.get_secret_value(), parse_mode='HTML')
    dispatcher = Dispatcher()

    return dispatcher, bot

async def poll(dp, bot):
    print("Starting polling...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    dp, bot = main()
    asyncio.run(poll(dp, bot))
