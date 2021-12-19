import sqlite3

from aiogram import Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor

from config import TOKEN

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

b1 = KeyboardButton("/start")
b2 = KeyboardButton("/help")
b3 = KeyboardButton("/project")

kb_client = ReplyKeyboardMarkup()

kb_client.add(b1).add(b2).add(b3)

connect = sqlite3.connect('./users.db')


class Form(StatesGroup):
    name = State()


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    cursor = connect.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS Users(
    Id INTEGER, TelegramUsername TEXT, Name TEXT, Rate INTEGER )""")
    connect.commit()
    user_id = message.chat.id
    telegram_username = message.chat.username
    cursor.execute(f'SELECT Id FROM Users WHERE Id = {user_id}')
    data = cursor.fetchone()
    print(data)
    print(user_id, telegram_username)

    if data is None:
        await message.answer(f"Ваш Telegram ID - {message.chat.id}")
        await message.answer(f"Ваше имя пользователя - {message.chat.username}")
        cursor.execute("INSERT INTO Users (Id, TelegramUsername, Rate) VALUES(?, ?, ?);", (user_id,
                                                                                           telegram_username, 0))
        connect.commit()
        await message.reply("Ты зарегистрирован, напиши 'Привет'")
    else:
        cursor.execute(f'SELECT Rate, Name FROM Users WHERE Id = {user_id}')
        user_data = cursor.fetchone()
        await message.answer(f"Ваш Telegram ID - {message.chat.id}")
        await message.answer(f"Ваше имя пользователя - {message.chat.username}")
        await message.answer(f"Твой рейтинг: {user_data[0]}")
        await message.reply(
            f"Приветствую тебя {user_data[1]}! Для изменения рейтинга напиши 'Поднять рейтинг' или 'Уменьшить рейтинг'")


@dp.message_handler(text='Привет')
async def process_help_command(message: types.Message):
    user_id = message.chat.id
    cursor = connect.cursor()
    cursor.execute(f'SELECT Name FROM Users WHERE Id = {user_id}')
    data = cursor.fetchone()
    if data[0] is None:
        await Form.name.set()
        await message.answer("Привет, как тебя зовут?")
    else:
        answer = "Привет " + data[0]
        await message.answer(answer)
        await message.answer("Для изменения рейтинга напиши 'Поднять рейтинг' или 'Уменьшить рейтинг'")

    @dp.message_handler(state=Form.name)
    async def process_name(msg: types.Message, state: FSMContext):
        if data[0] is None:
            us_id = msg.chat.id
            user_name = msg.text
            query = f"UPDATE Users SET Name = '{user_name}' WHERE Id = '{us_id}'"
            cursor.execute(query)
            connect.commit()
            start_hello = "Привет, " + user_name
            await state.finish()
            await bot.send_message(msg.from_user.id, start_hello)
            await message.answer("Для изменения рейтинга напиши 'Поднять рейтинг' или 'Уменьшить рейтинг'")
        else:
            await state.finish()
            await message.answer("У тебя уже заполнено имя!")
            await message.answer("Для изменения рейтинга напиши 'Поднять рейтинг' или 'Уменьшить рейтинг'")


@dp.message_handler(commands=['deleteme'])
async def process_help_command(message: types.Message):
    cursor = connect.cursor()
    user_id = message.chat.id
    cursor.execute(f'DELETE FROM Users WHERE Id = {user_id}')
    connect.commit()


@dp.message_handler(text='Поднять рейтинг')
async def process_help_command(message: types.Message):
    cursor = connect.cursor()
    user_id = message.chat.id
    cursor.execute(f'SELECT Rate FROM Users WHERE Id = {user_id}')
    r1 = cursor.fetchone()
    print(r1)
    cursor.execute(f'UPDATE Users SET Rate= {r1[0] + 1} WHERE Id = {user_id}')
    connect.commit()
    await message.reply(f"Твой рейтинг увеличен! теперь он равен {r1[0] + 1}")


@dp.message_handler(text='Уменьшить рейтинг')
async def process_help_command(message: types.Message):
    cursor = connect.cursor()
    user_id = message.chat.id
    cursor.execute(f'SELECT Rate FROM Users WHERE Id = {user_id}')
    r1 = cursor.fetchone()
    print(r1)
    cursor.execute(f'UPDATE Users SET Rate= {r1[0] - 1} WHERE Id = {user_id}')
    connect.commit()
    await message.reply(f"Твой рейтинг уменьшен! теперь он равен {r1[0] - 1}")


@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.reply(
        "/start - начало проекта, /help - инфо о командах, /project - инфо о создателе. Изменение рейтинга - 'Поднять "
        "рейтинг' или 'Уменьшить рейтинг'",
        reply_markup=kb_client)


@dp.message_handler(commands=['project'])
async def process_help_command(message: types.Message):
    await message.reply("Создатель проекта - Лужнов Алексей aka GOSHANSKY")
    await message.reply("Помогал в разработке CountNeuroman")


if __name__ == '__main__':
    executor.start_polling(dp)
