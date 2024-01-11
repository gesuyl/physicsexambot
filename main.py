#!/usr/bin/python3
from datetime import datetime
from asyncio import run as asyncio_run
#
from app.config.app_context import app_context
from app.handlers import commands, images



def main() -> tuple:
    db = app_context.db
    tesseract_reader = app_context.tesseract_reader
    bot = app_context.bot
    dispatcher = app_context.dispatcher

    dispatcher.include_routers(commands.router, images.router)

    return dispatcher, bot


async def poll(dp, bot):
    print("Starting polling...")

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    dp, bot = main()
    dp["started_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")

    asyncio_run(poll(dp, bot))
