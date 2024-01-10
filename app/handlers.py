from aiogram import types
from aiogram.filters.command import Command
import os
from utils import access_check, admin_check, Keyboard
from main import dp, tesseract_reader, db, bot
from config_reader import config



@dp.message(Command('info'))
async def info(message):
    await message.answer(text=tesseract_reader.return_info(),
                         parse_mode='HTML',
                         reply_markup=Keyboard.delete_button())


@dp.message_handler(Command('fill_db'))
async def fill_db(message):
    if not admin_check(message.from_user.username, tesseract_reader):
        await bot.send_message(chat_id=message.chat.id,
                               text="You're not an admin")
        return

    await bot.send_message(chat_id=message.chat.id,
                           text="Processing... (check the console)",
                           reply_markup=Keyboard.delete_button())
    
    tesseract_reader.fill_db()

    await bot.send_message(chat_id=message.chat.id,
                           text="Done!",
                           reply_markup=Keyboard.delete_button())

    tesseract_reader.update_info()


@dp.message_handler(commands='add', commands_prefix='!/')
async def add(message):
    if not admin_check(message.from_user.username, tesseract_reader):
        await bot.send_message(chat_id=message.chat.id,
                               text="You're not an admin")
        return
    
    if message.reply_to_message.from_user.username not in tesseract_reader.users.keys():
        db.add_user(id=message.reply_to_message.from_user.id,
                    username=message.reply_to_message.from_user.username,
                    role="user")
        txt = f"Added @{message.reply_to_message.from_user.username}"
    else:
        txt = f"@{message.reply_to_message.from_user.username} is already on the list"
    
    await bot.send_message(chat_id=message.chat.id,
                           text=txt,
                           reply_markup=Keyboard.delete_button())
    
    tesseract_reader.update_info()
    



@dp.message_handler(content_types=['photo', 'document'])
async def handle_photo(message):
    if not access_check(message.from_user.username, tesseract_reader):
        await bot.send_message(chat_id=message.chat.id,
                               text="You don't have access to this bot.")
        return
    
    if 'photo' in message.__dict__['_values'].keys():
        print(f'Received an image from @{message.from_user.username}')
        file_name = message.__dict__['_values']['photo'][-1].__dict__["_values"]["file_unique_id"]
        await message.photo[-1].download(f'{os.path.dirname(os.path.realpath(__file__))}\\img_processing\\{file_name}.jpg')

    elif 'document' in message.__dict__['_values'].keys():
        print(f'Received a document from @{message.from_user.username}')
        file_name = message.__dict__['_values']['document'].__dict__["_values"]["file_unique_id"]
        await message.document.download(f'{os.path.dirname(os.path.realpath(__file__))}\\img_processing\\{file_name}.jpg')

    diff_dict = await tesseract_reader.compare(file_name)
    first_file = list(diff_dict.keys())[list(
        diff_dict.values()).index(min(list(diff_dict.values())))]

    await bot.send_photo(chat_id=message.chat.id,
                            photo=types.InputFile(f"{STORED_IMAGES_FOLDER}\\{first_file}"),
                            reply_markup=Keyboard.answer_kb(diff_dict, first_file))


@dp.callback_query_handler()
async def callback(call):
    if 'correct' in call.data:
        await bot.answer_callback_query(callback_query_id=call.id,
                                        show_alert=False,
                                        text="Супер!")

        await bot.edit_message_reply_markup(chat_id=call.message.chat.id,
                                            message_id=call.message.message_id,
                                            reply_markup=None)
        
    elif 'not_correct' in call.data:
        next_img = call.data.split('#')[1]
        if next_img != "last":
            file_name = call.message.__dict__['_values']['document'].__dict__["_values"]["file_unique_id"]
            diff_dict = await tesseract_reader.compare(file_name)
            
            await bot.delete_message(chat_id=call.message.chat.id,
                                     message_id=call.message.message_id)
            await bot.send_photo(chat_id=call.message.chat.id,
                                 photo=types.InputFile(f"{STORED_IMAGES_FOLDER}\\{next_img}"),
                                 reply_markup=Keyboard.answer_kb(diff_dict, next_img))
        elif next_img == "last":
            await bot.delete_message(chat_id=call.message.chat.id,
                                     message_id=call.message.message_id)
            await bot.send_message(chat_id=call.message.chat.id,
                                   text="Твоей задачи нет в базе((",
                                   reply_markup=Keyboard.delete_button())

    elif call.data == 'delete':
        await bot.delete_message(chat_id=call.message.chat.id,
                                 message_id=call.message.message_id)