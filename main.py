#!/usr/bin/python3
from asyncio import run as asyncio_run
from datetime import datetime

from aiogram import Dispatcher

from app.utils.utils import name_ascii_art

print(name_ascii_art())

from app.config.app_context import app_context
from app.handlers import admin_commands, commands, images, superadmin_commands


def setup_routes() -> Dispatcher:
    """
    Setup routes for the bot
    
    :return: aiogram.Dispatcher
    """
    dispatcher = app_context.dispatcher
    dispatcher.include_routers(
        superadmin_commands.router,
        admin_commands.router,
        commands.router,
        images.router
    )

    return dispatcher


async def poll(dp: Dispatcher, bot: object) -> None:
    """
    Start polling for updates from Telegram

    :param dp: aiogram.Dispatcher
    :param bot: aiogram.Bot
    """

    print("[*] Starting polling...")

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    dp = setup_routes()
    dp["started_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    asyncio_run(poll(dp, app_context.bot))
