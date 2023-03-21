import sqlite3
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from config import token

bot = Bot(token)  # объявление бота
dp = Dispatcher(bot)


async def on_startup(_):  # вывод текста в коносль при успешном запуске
    print("Бот запущен")


@dp.message_handler(commands="start")  # приветствие и вывод панели кнопок
async def cmd_start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Руслан пидор?", "Курс Доллара", "Курс Евро", "Курс мочи", "2 + 2"]
    keyboard.add(*buttons)
    await message.answer("Добро пожаловать в Хейтера Руслана", reply_markup=keyboard)


@dp.message_handler()  # подключение сукуэль
async def sql_request(message: types.Message):
    reply1 = message.text  # присваивание значение к переменной
    connection = sqlite3.connect("db1.db")  # создание подключения к таблице
    cursor = connection.cursor()
    [answer] = cursor.execute("Select answer_user from question where question_user = ?",
                              (reply1,))  # получение данных из таблицы ориентируясь на ячейку question_user
    # и забирая значение ячейки answer_user(таблица question)
    connection.commit()  # закрытие таблицы
    await bot.send_message(chat_id=message.from_user.id,
                           text=answer[0],
                           parse_mode="HTML")  # отправка значений с нашим значением


if __name__ == "__main__":
    executor.start_polling(dp, on_startup=on_startup,
                           skip_updates=True)
