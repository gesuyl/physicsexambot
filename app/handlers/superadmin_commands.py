from aiogram import types
from aiogram import Router
from aiogram.filters.command import Command
#
from app.config.app_context import app_context
from app.utils.wrappers import check_superadmin_access



router = Router()


@router.message(Command("read_db"))
@check_superadmin_access
async def read_db(message: types.Message):
    subcommand = message.text.split(" ")[1].lower()

    if subcommand == "users":
        records = app_context.tesseract_reader.db.get_users()
        header = "====DB_USERS===="
    elif subcommand == "images":
        records = app_context.tesseract_reader.db.get_images()
        header = "====DB_IMAGES===="
    else:
        await message.answer(
            text="Invalid subcommand. Use 'users' or 'images'."
        )
        return

    msg = f"{header}\n"

    for record in records:
        record_desc = "\n".join(
            [f"<b>{key}</b>: {value}" for key, value in record.to_dict().items()]
        )
        msg += f"{record_desc}\n"
        msg += "---\n"

    await message.answer(
        text=msg
    )


@router.message(Command("delete"))
@check_superadmin_access
async def delete(message: types.Message):
    user_to_delete = message.text.split(" ")[1].lower()

    app_context.tesseract_reader.db.delete_user(username=user_to_delete)

    await message.answer(
        text=f"Deleted @{user_to_delete}"
    )

    app_context.tesseract_reader.update_info()


@router.message(Command("fill_db"))
@check_superadmin_access
async def fill_db(message: types.Message):
    await message.answer(
        text="Processing... (check the console)"
    )

    app_context.tesseract_reader.fill_db()

    await message.answer(
        text="Done!"
    )

    app_context.tesseract_reader.update_info()


@router.message(Command("drop_table"))
@check_superadmin_access
async def drop_db(message: types.Message):
    table_to_drop = message.text.split(" ")[1]
    app_context.tesseract_reader.db.drop_table(table_name=table_to_drop)

    await message.answer(
        text=f"Dropped {table_to_drop}"
    )

    app_context.tesseract_reader.update_info()
