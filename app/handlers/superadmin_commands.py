from aiogram import types, Router, F
from aiogram.filters.command import Command
#
from app.config.config import settings
from app.config.app_context import app_context
from app.utils.wrappers import check_superadmin_access
from app.utils.keyboard import Keyboard


router = Router()


@router.message(Command("read_table"))
@check_superadmin_access
async def read_table(message: types.Message) -> None:
    """
    Read chosen table from database

    :param message: aiogram.types.Message
    """
    subcommand = message.text.split(" ")[1].lower()

    if subcommand == "users":
        records = app_context.tesseract_reader.db.get_users()
        header = "|======= USERS =======|"
    elif subcommand == "images":
        records = app_context.tesseract_reader.db.get_images()
        header = "|======= IMAGES =======|"
    elif subcommand == "main_conf":
        records = app_context.tesseract_reader.db.get_main_conf()
        header = "|======= MAIN_CONF =======|"
    else:
        await message.answer(text="Invalid table name. Use 'users', 'images', or 'main_conf'.")

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
async def delete(message: types.Message) -> None:
    """
    Delete user from database
    
    :param message: aiogram.types.Message
    """
    user_to_delete = message.text.split(" ")[1].lower()

    app_context.tesseract_reader.db.delete_user(username=user_to_delete)

    await message.answer(
        text=f"Deleted @{user_to_delete}"
    )

    app_context.tesseract_reader.update_info()


@router.message(Command("fill_images"))
@check_superadmin_access
async def fill_table(message: types.Message) -> None:
    """
    Fill 'images' table with pre-processed OCR data

    :param message: aiogram.types.Message
    """
    await message.answer(
        text=f"Filling 'images' table with pre-processed OCR data.\n"
             f"Source folder: <i>{settings.STORED_IMAGES_FOLDER}</i>\n"
             f"Do you want the output to be verbose?",
        reply_markup=Keyboard.yes_no_keyboard('fill_table_verbose')
    )


@router.message(Command("empty_table"))
@check_superadmin_access
async def drop_table(message: types.Message) -> None:
    """
    Empty chosen table

    :param message: aiogram.types.Message
    """
    table_to_drop = message.text.split(" ")[1]

    if not app_context.tesseract_reader.db.table_exists(table_name=table_to_drop):
        await message.answer(text=f"The table '{table_to_drop}' does not exist.")
    else:
        rows_in_table = app_context.tesseract_reader.db.get_row_count(table_name=table_to_drop)
        await message.answer(
            text=f"Are you sure you want to empty '{table_to_drop}' table? It has {rows_in_table} rows of data.\n<b>(Y/N)</b>",
            reply_markup=Keyboard.yes_no_keyboard('empty_table')
        )


@router.callback_query(F.data == "fill_table_verbose_yes")
async def fill_table_verbose(callback: types.CallbackQuery) -> None:
    """
    Callback handler, fills 'images' table with pre-processed OCR data (verbose)
    
    :param callback: aiogram.types.CallbackQuery
    """
    await callback.message.answer(
        text="Filling DB with pre-processed OCR data.\n"
             "Console verbosity: <b>Yes</b>\n\n"
             "<b>This can take a long time!</b> (20 images/min)\n"
             "\nFor more info, check the console."
    )

    app_context.tesseract_reader.fill_table(verbose=True)
    app_context.tesseract_reader.update_info()

    await callback.answer(
        text="Done!",
        show_alert=True
    )


@router.callback_query(F.data == "fill_table_verbose_no")
async def fill_table_nonverbose(callback: types.CallbackQuery) -> None:
    """
    Callback handler, fills 'images' table with pre-processed OCR data (non-verbose)

    :param message: aiogram.types.Message
    """
    await callback.message.answer(
        text="Filling DB with pre-processed OCR data.\n"
             "Console verbosity: <b>No</b>\n\n"
             "<b>This can take a long time!</b> (20 images/min)\n"
             "\nFor more info, check the console."
    )

    app_context.tesseract_reader.fill_table(verbose=False)
    app_context.tesseract_reader.update_info()

    await callback.answer(
        text="Done!",
        show_alert=True
    )


@router.callback_query(F.data == "empty_table_yes")
async def empty_table_yes(callback: types.CallbackQuery) -> None:
    """
    Callback handler, empties chosen table

    :param callback: aiogram.types.CallbackQuery
    """
    table_to_drop = callback.message.text.split(" ")[7].strip("'")

    if app_context.tesseract_reader.db.table_exists(table_name=table_to_drop):
        app_context.tesseract_reader.db.empty_table(table_name=table_to_drop)
    
        app_context.tesseract_reader.update_info()
    else:
        await callback.message.answer(
            text=f"The table '{table_to_drop}' does not exist."
        )

        return

    await callback.message.answer(
        text=f"Table '{table_to_drop}' emptied."
    )



@router.callback_query(F.data == "empty_table_no")
async def empty_table_no(callback: types.CallbackQuery) -> None:
    """
    Callback handler, does not empty chosen table

    :param callback: aiogram.types.CallbackQuery
    """
    table_to_drop = callback.message.text.split(" ")[-3]
    await callback.message.answer(
        text=f"Table {table_to_drop} not emptied."
    )
