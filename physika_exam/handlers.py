from aiogram import types
# from aiogram.dispatcher.filters import Command
from utility import check_init, delete_button, answer_kb
from main import dp, tesseract_reader

@dp.message_handler(commands='info', commands_prefix='!/')
async def info(message):
    await bot.send_message(chat_id=message.chat.id,
                           text=tesseract_reader.return_info(),
                           parse_mode='HTML',
                           reply_markup=delete_button())


@dp.message_handler(commands='add', commands_prefix='!/')
async def add(message):
    if not check_init():
        return
    if str(message.from_user.username) in tesseract_reader.admins:
        print('admin')
        pass
    else:
        print('not_admin')
        return

    print(message.__dict__)
    if message.reply_to_message.from_user.username not in tesseract_reader.users.keys():
        tesseract_reader.users[message.reply_to_message.from_user.username].update({
            "id": message.reply_to_message.from_user.id,
            "role": "user"
        })
        txt = f"Added @{message.reply_to_message.from_user.username}"
    else:
        txt = f"@{message.reply_to_message.from_user.username} is already on the list"
    await bot.send_message(chat_id=message.chat.id,
                           text=txt,
                           reply_markup=delete_button())


@dp.message_handler(commands='start', commands_prefix='!/')
async def init(message):
    if not check_init():
        tesseract_reader = tesseract_reader(read_config('config.txt'))

    print('Reader initialized succesfully!')
    await bot.send_message(chat_id=message.chat.id,
                           text='hi',
                           parse_mode='HTML',
                           reply_markup=delete_button())


@dp.message_handler(commands='stop', commands_prefix='!/')
async def stop(message):
    if not check_init():
        return
    if str(message.from_user.username) in tesseract_reader.admins:
        pass
    else:
        return
    tesseract_reader.save_config()
    await bot.send_message(chat_id=message.chat.id,
                           text="Stopped")
    ExitProcess(GetCurrentProcess())


@dp.message_handler(commands='restart', commands_prefix='!/')
async def restart(message):
    if not check_init():
        return
    if str(message.from_user.username) in tesseract_reader.admins:
        pass
    else:
        return
    tesseract_reader.save_config()
    await bot.send_message(chat_id=message.chat.id,
                           text="Restarting..")
    os.execv(sys.executable, ['python', __file__])


@dp.message_handler(content_types=['photo', 'document'])
async def handle_photo(message):
    if not check_init():
        return
    if str(message.from_user.username) not in tesseract_reader.users.keys() and str(message.from_user.username) not in tesseract_reader.admins:
        await bot.send_message(chat_id=message.chat.id,
                               text="You're not on the list",
                               reply_markup=delete_button())
        return
    else:
        if 'photo' in message.__dict__['_values'].keys():
            print(f'Received an image from @{message.from_user.username}')
            file_name = message.__dict__[
                '_values']['photo'][-1].__dict__["_values"]["file_unique_id"]
            await message.photo[-1].download(f'{os.path.dirname(os.path.realpath(__file__))}\\img_processing\\{file_name}.jpg')

        elif 'document' in message.__dict__['_values'].keys():
            print(f'Received a document from @{message.from_user.username}')
            file_name = message.__dict__['_values']['document'].__dict__[
                "_values"]["file_unique_id"]
            await message.document.download(f'{os.path.dirname(os.path.realpath(__file__))}\\img_processing\\{file_name}.jpg')

        diff_dict = await tesseract_reader.compare(file_name)
        first_file = list(diff_dict.keys())[list(
            diff_dict.values()).index(min(list(diff_dict.values())))]

        await bot.send_photo(chat_id=message.chat.id,
                             photo=types.InputFile(f"{STORED_IMAGES_FOLDER}\\{first_file}"),
                             reply_markup=answer_kb(diff_dict, first_file))


@dp.callback_query_handler()
async def callback(call):
    if call.data == 'correct':
        await bot.answer_callback_query(callback_query_id=call.id,
                                        show_alert=False,
                                        text="Супер!")

        await bot.edit_message_reply_markup(chat_id=call.message.chat.id,
                                            message_id=call.message.message_id,
                                            reply_markup=None)
    elif 'not_correct' in call.data:
        next_img = call.data.split('#')[1]
        if next_img != "last":
            await bot.delete_message(chat_id=call.message.chat.id,
                                     message_id=call.message.message_id)
            await bot.send_photo(chat_id=call.message.chat.id,
                                 photo=types.InputFile(f"{STORED_IMAGES_FOLDER}\\{next_img}"),
                                 reply_markup=answer_kb(diff_dict, next_img))
        elif next_img == "last":
            await bot.delete_message(chat_id=call.message.chat.id,
                                     message_id=call.message.message_id)
            await bot.send_message(chat_id=call.message.chat.id,
                                   text="Твоей задачи нет в базе((",
                                   reply_markup=delete_button())

    elif call.data == 'delete':
        await bot.delete_message(chat_id=call.message.chat.id,
                                 message_id=call.message.message_id)