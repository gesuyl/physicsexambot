#!/usr/bin/python3
from datetime import datetime
from asyncio import run as asyncio_run
#
from aiogram import Dispatcher
from app.config.app_context import app_context
from app.handlers import superadmin_commands, admin_commands, commands, images



def setup_routes() -> Dispatcher:
    dispatcher = app_context.dispatcher
    dispatcher.include_routers(
        superadmin_commands.router,
        admin_commands.router,
        commands.router,
        images.router
    )

    return dispatcher


async def poll(dp, bot) -> None:
    print("[*] Starting polling...")

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    dp = setup_routes()
    dp["started_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")

    asyncio_run(poll(dp, app_context.bot))
