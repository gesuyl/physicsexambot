from aiogram import types
#
from app.config.app_context import app_context



def check_superadmin_access(func) -> bool:
    async def wrapper(message: types.Message):
        if message.from_user.username != app_context.tesseract_reader.super_admin:
            await message.answer(
                text="This function is only available to the superadmin."
            )
            return
        await func(message)
    return wrapper


def check_admin_access(func) -> bool:
    async def wrapper(message: types.Message):
        if message.from_user.username not in app_context.tesseract_reader.admins:
            await message.answer(
                text="You're not an admin"
            )
            return
        await func(message)
    return wrapper


def check_access(func) -> bool:
    async def wrapper(message: types.Message):
        if message.from_user.username not in app_context.tesseract_reader.users.keys:
            await message.answer(
                text="You don't have access to the bot"
            )
            return
        await func(message)
    return wrapper
