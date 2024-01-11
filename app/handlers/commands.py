import os
from aiogram import types
from aiogram import Router, F
from aiogram.filters.command import Command
#
from app.config_reader import settings
from app.utils.keyboard import Keyboard
from app.utils.utils import access_check, admin_check, Keyboard



router = Router()

from main import tesseract_reader, db, bot

@router.message(Command('info'))
async def info(message: types.Message):
    await message.answer(text=tesseract_reader.return_info(),
                         reply_markup=Keyboard.add_delete_button())


@router.message(Command('time'))
async def info(message: types.Message, started_at: str):
    await message.answer("Bot started at " + started_at)


@router.message(Command("hello"))
async def cmd_hello(message: types.Message):
    await message.answer(f"Hello, <b>{message.from_user.full_name}</b>")


@router.message_handler(Command('fill_db'))
async def fill_db(message: types.Message):
    if not admin_check(message.from_user.username, tesseract_reader):
        await message.answer("You're not an admin")
        return

    await message.answer(
        text="Processing... (check the console)",
        reply_markup=Keyboard.add_delete_button()
    )
    
    tesseract_reader.fill_db()

    await bot.send_message(
        text="Done!",
        reply_markup=Keyboard.add_delete_button()
    )

    tesseract_reader.update_info()


@router.message_handler(Command('add'))
async def add_user(message):
    if not admin_check(message.from_user.username, tesseract_reader):
        await bot.send_message(chat_id=message.chat.id,
                               text="You're not an admin")
        return
    
    if message.reply_to_message.from_user.username not in tesseract_reader.users.keys():
        db.add_user(id=message.reply_to_message.from_user.id,
                    username=message.reply_to_message.from_user.username,
                    role="user")
        txt = f"Added @{message.reply_to_message.from_user.username}"
    else:
        txt = f"@{message.reply_to_message.from_user.username} is already on the list"
    
    await bot.send_message(chat_id=message.chat.id,
                           text=txt,
                           reply_markup=Keyboard.add_delete_button())
    
    tesseract_reader.update_info()