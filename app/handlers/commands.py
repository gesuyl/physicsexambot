from datetime import datetime
from aiogram import types
from aiogram import Router
from aiogram.filters.command import Command
#
from app.utils.keyboard import Keyboard
from app.config.app_context import app_context
from app.utils.wrappers import check_admin_access



router = Router()


@router.message(Command('init'))
async def init(message: types.Message):
    app_context.tesseract_reader.update_info()

    if app_context.tesseract_reader.super_admin:
        await message.answer(
            text=f"Already initialized! Superadmin set: @{app_context.tesseract_reader.super_admin}"
        )

    else:
        app_context.tesseract_reader.db.add_user(
            id=message.from_user.id,
            username=message.from_user.username,
            role="superadmin"
        )

        app_context.tesseract_reader.add_superadmin(username=message.from_user.username)

        await message.answer(
            text=f"Initialized! Superadmin set: @{app_context.tesseract_reader.super_admin}"
        )

        