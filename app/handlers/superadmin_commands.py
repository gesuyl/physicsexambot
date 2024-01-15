from aiogram import types
from aiogram import Router
from aiogram.filters.command import Command
#
from app.config.app_context import app_context
from app.utils.wrappers import check_superadmin_access


router = Router()




@router.message(Command('read_db_users'))
@check_superadmin_access
async def read_db_users(message: types.Message):
    users = app_context.tesseract_reader.db.get_users()
    msg = "==USERS==\n"

    for user in users:
        user_desc = "\n".join([f"<b>{key}</b>: {value}" for key, value in user.to_dict().items()])
        msg += f"{user_desc}\n"
        msg += "---\n"

    await message.answer(text=msg)


@router.message(Command('delete'))
@check_superadmin_access
async def delete(message: types.Message):
    user_to_delete = message.text.split(" ")[1]

    app_context.tesseract_reader.db.delete_user(username=user_to_delete)

    await message.answer(
        text=f"Deleted @{user_to_delete}"
    )

    app_context.tesseract_reader.update_info()


@router.message(Command('fill_db'))
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


@router.message(Command('drop_table'))
@check_superadmin_access
async def drop_db(message: types.Message):
    table_to_drop = message.text.split(" ")[1]
    app_context.tesseract_reader.db.drop_table(table_name=table_to_drop)

    await message.answer(
        text=f"Dropped {table_to_drop}"
    )

    app_context.tesseract_reader.update_info()
