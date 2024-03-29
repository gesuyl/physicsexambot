from datetime import datetime

from aiogram import Router, types
from aiogram.filters.command import Command

from app.config.app_context import app_context
from app.utils.keyboard import Keyboard
from app.utils.wrappers import check_admin_access

router = Router()


@router.message(Command('info'))
@check_admin_access
async def info(message: types.Message) -> None:
    """
    Show bot info
    
    :param message: aiogram.types.Message
    """
    await message.answer(
        text=app_context.tesseract_reader.return_info(),
        reply_markup=Keyboard.add_delete_button()
    )


@router.message(Command('time'))
@check_admin_access
async def time(message: types.Message, started_at: str) -> None:
    """
    Show bot start time and current server time

    :param message: aiogram.types.Message
    :param started_at: str
    """
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    await message.answer(text=f"Bot started: <b>{started_at}</b>"
                              f"\nCurrent server time: <b>{current_time}</b>")


@router.message(Command("users"))
@check_admin_access
async def users(message: types.Message) -> None:
    """
    Show users and admins
    
    :param message: aiogram.types.Message
    """
    users_message = f"""
Users: {app_context.tesseract_reader.users}\n
Admins: {app_context.tesseract_reader.admins}
"""

    await message.answer(text=users_message)


@router.message(Command('add'))
@check_admin_access
async def add(message: types.Message) -> None:
    """
    Add replied-to user to the list of users
    
    :param message: aiogram.types.Message
    """
    if message.reply_to_message.from_user.username not in app_context.tesseract_reader.users.keys():
        app_context.tesseract_reader.db.add_user(
            id=message.reply_to_message.from_user.id,
            username=message.reply_to_message.from_user.username,
            role="user"
        )
        txt = f"Added @{message.reply_to_message.from_user.username}"
    else:
        txt = f"@{message.reply_to_message.from_user.username} is already on the list"

    await message.answer(
        text=txt,
        reply_markup=Keyboard.add_delete_button()
    )

    app_context.tesseract_reader.update_info()
