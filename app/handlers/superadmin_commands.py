from aiogram import types, Router, F
from aiogram.filters.command import Command
#
from app.config.app_context import app_context
from app.utils.wrappers import check_superadmin_access
from app.utils.keyboard import Keyboard


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
        await message.answer(text="Invalid subcommand. Use 'users' or 'images'.")

        return

    msg = f"{header}\n"

    if len(records) == 0:
        msg += "No records found."
        await message.answer(text=msg)

        return

    if len(records) > 50:
        await message.answer(text="Too many records to show. Showing first <b>50</b>")
        records_to_show = records[:50]
    else:
        records_to_show = records

    for record in records_to_show:
        record_desc = "\n".join(
            [
                f"<b>{key}</b>: {value}"
                for key, value in record.to_dict().items()
            ]
        )
        msg += f"{record_desc}\n"

    await message.answer(text=msg)


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
        text="Filling DB with pre-processed OCR data.\nDo you want the output to be verbose? <b>(Y/N)</b>",
        reply_markup=Keyboard.yes_no_keyboard('fill_db_verbose')
    )


@router.message(Command("empty_table"))
@check_superadmin_access
async def drop_db(message: types.Message):
    table_to_drop = message.text.split(" ")[1]
    app_context.tesseract_reader.db.empty_table(table_name=table_to_drop)

    await message.answer(text=f"Emptied '{table_to_drop}' table.")

    app_context.tesseract_reader.update_info()


@router.callback_query(F.data == "fill_db_verbose_yes")
async def fill_db_verbose(callback: types.CallbackQuery):
    await callback.message.answer(
        text="Filling DB with pre-processed OCR data.\n"
             "Console verbosity: <b>Yes</b>\n\n"
             "<b>This can take a long time!</b> (20 images/min)\n"
             "\nFor more info, check the console."
    )

    app_context.tesseract_reader.fill_db(verbose=True)
    app_context.tesseract_reader.update_info()

    await callback.answer(
        text="Done!",
        show_alert=True
    )


@router.callback_query(F.data == "fill_db_verbose_no")
async def fill_db_nonverbose(callback: types.CallbackQuery):
    await callback.message.answer(
        text="Filling DB with pre-processed OCR data.\n"
             "Console verbosity: <b>No</b>\n\n"
             "<b>This can take a long time!</b> (20 images/min)\n"
             "\nFor more info, check the console."
    )

    app_context.tesseract_reader.fill_db(verbose=False)
    app_context.tesseract_reader.update_info()

    await callback.answer(
        text="Done!",
        show_alert=True
    )
