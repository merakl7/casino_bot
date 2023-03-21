import asyncio
from aiogram import Bot, Dispatcher, executor, types
from config import token
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters import Text
import random
import time
import sqlite3

bot = Bot(token)
dp = Dispatcher(bot)


async def on_startup(_):
    print("Запуск успешен")


@dp.message_handler(commands="help")
async def start_command(message: types.message):
    await message.answer(
"""/start - для регистрации
/cards - для открытия пака
/results - кол-во полученных карт
/balance - внутриигровой баланс
Стоимость открытия одного пака = 100 монет.
За каждую карту вы получается определенное кол-во монет:
Обычная - 5 монет, редкая - 20, эпическая - 100, 
легендарная - 400""")


@dp.message_handler(commands="start")
async def start_command(message: types.message):
    conn = sqlite3.connect('db4.db')
    cur = conn.cursor()
    user_id = message.from_user.id
    [len_user] = cur.execute('SELECT COUNT(user_id) from cards_user where user_id=?', (user_id,))
    len_user = len_user[0]
    if len_user == 0:
        cur.execute("INSERT INTO cards_user VALUES(?, ?, ?, ?, ?)", (user_id, 0, 0, 0, 0))
        await message.answer(text="Вы зарегистрировались в ебаном казино! Нажмите /cards для открытия пака")
    else:
        await message.answer(text="Ваши данные уже внесены данные, открывайте паки с помощью /cards")
    conn.commit()


@dp.message_handler(commands="cards")
async def cards_command(message: types.message):
    cards = []
    common = "Обычная"
    rare = "Редкая"
    epic = "Эпическая"
    legendary = "Легендарная"
    conn = sqlite3.connect('db4.db')
    cur = conn.cursor()
    user_id = message.from_user.id
    print(user_id)
    [coin] = cur.execute('select coin from cards_user where user_id = ?', (user_id,)) #достаем значение монет из базы
    coin = coin[0]
    if coin >= 100:  #первый иф проверяет есть ли деньги у мешка с костями
        cur.execute("UPDATE cards_user SET coin = coin - 100 WHERE user_id = ?", (user_id,)) #если есть пускает играть в казино
        for _ in range(5):
            card_pool = random.randint(1, 1000)
            if card_pool < 750:
                cards.append(common)
                cur.execute("UPDATE cards_user SET common = common + 1 WHERE user_id = ?", (user_id,))
                cur.execute("UPDATE cards_user SET coin = coin + 5 WHERE user_id = ?", (user_id,)) # добавление монет за полученную карту, далее по такому же принципу
            elif 750 <= card_pool < 900:
                cards.append(rare)
                cur.execute("UPDATE cards_user SET rare = rare + 1 WHERE user_id = ?", (user_id,))
                cur.execute("UPDATE cards_user SET coin = coin + 20 WHERE user_id = ?", (user_id,))
            elif 900 <= card_pool < 990:
                cards.append(epic)
                cur.execute("UPDATE cards_user SET epic = epic + 1 WHERE user_id = ?", (user_id,))
                cur.execute("UPDATE cards_user SET coin = coin + 100 WHERE user_id = ?", (user_id,))
            elif card_pool >= 990:
                cards.append(legendary)
                cur.execute("UPDATE cards_user SET legendary = legendary + 1 WHERE user_id = ?", (user_id,))
                cur.execute("UPDATE cards_user SET coin = coin + 400 WHERE user_id = ?", (user_id,))
                anekdot = random.randint(1, 43)
                [lega] = cur.execute("select anekdot from joke_hs where id_anek = ?", (anekdot,))
                lega = lega[0]
                await message.answer(lega)
        #print(cards)
        for i in range(len(cards)): #получаем список из 5 карт
            gold_test = random.randint(1, 1000) #задаем тест на попытку получить золотую
            if cards[i] == "Обычная" and gold_test > 960: #проверяем есть ли обычная карта в списке и если есть,пытаемся ролять золотую
                cur.execute("UPDATE cards_user SET gold_common = gold_common + 1 WHERE user_id = ?", (user_id,)) #обновление записей для результата
                cur.execute("UPDATE cards_user SET coin = coin + 50 WHERE user_id = ?", (user_id,)) #обновление записей для монет
                cards[i] = "Золотая обычная карта" #если рольнуло,то меняем в списке обычную на золотую, далее такой же принцип для более редких карт
            elif cards[i] == "Редкая" and gold_test > 960:
                cur.execute("UPDATE cards_user SET gold_rare = gold_rare + 1 WHERE user_id = ?", (user_id,))
                cur.execute("UPDATE cards_user SET coin = coin + 100 WHERE user_id = ?", (user_id,))
                cards[i] = "Золотая редкая карта"
            elif cards[i] == "Эпическая" and gold_test > 960:
                cur.execute("UPDATE cards_user SET gold_epic = gold_epic + 1 WHERE user_id = ?", (user_id,))
                cur.execute("UPDATE cards_user SET coin = coin + 400 WHERE user_id = ?", (user_id,))
                cards[i] = "Золотая Эпическая карта"
            elif cards[i] == "Легендарная" and gold_test > 960:
                cur.execute("UPDATE cards_user SET gold_legendary = gold_legendary + 1 WHERE user_id = ?", (user_id,))
                cur.execute("UPDATE cards_user SET coin = coin + 1600 WHERE user_id = ?", (user_id,))
                cards[i] = "Золотая легендарная карта"

        if cards == ['Обычная', 'Обычная', 'Обычная', 'Обычная', 'Обычная']: #защита бен броуда
            cards = ['Обычная', 'Обычная', 'Обычная', 'Обычная', 'Редкая']
        conn.commit()
        print(cards)
        await bot.send_animation(message.chat.id,
                                 animation="https://vk.com/doc146713895_657548202?hash=nxqA6qNAlvL4lU6XfJ4iRjFU5CSH7DQhUoH1QYbWPZg&dl=Xm2IAjLQPvmvm1e7viJMzEdWGyRkeOyjfUASZt0ZvB8&wnd=1&module=im",
                                 caption='\n'.join(cards))
        if "Золотая легендарная карта" in cards:
            await message.answer("Ваша мать продана на черном рынке") #ФАКТ ФАКТ ФАКТ
    else:
        await message.reply("нет денек") #здесь надо написано красиво что вы нищий и заплатите шекелей нам


@dp.message_handler(commands="balance")
async def balance_cmd(message: types.message):  #хендлер на баланс,хз че писать все понятно
    conn = sqlite3.connect('db4.db')
    cur = conn.cursor()
    balance = ''
    user_id = message.from_user.id
    [coin] = cur.execute('select coin from cards_user where user_id = ?', (user_id,))
    coin = coin[0]
    await message.reply(f"Ваш баланс - {coin}")


@dp.message_handler(commands="results")
async def answer_command(message: types.message):
    conn = sqlite3.connect('db4.db')
    cur = conn.cursor()
    result1 = ''
    user_id = message.from_user.id
    [common] = cur.execute('select common from cards_user where user_id = ?', (user_id,))
    common = common[0]
    [rare] = cur.execute('select rare from cards_user where user_id = ?', (user_id,))
    rare = rare[0]
    [epic] = cur.execute('select epic from cards_user where user_id = ?', (user_id,))
    epic = epic[0]
    [legendary] = cur.execute('select legendary from cards_user where user_id = ?', (user_id,))
    legendary = legendary[0]
    [gold_common] = cur.execute('select gold_common from cards_user where user_id = ?', (user_id,))
    gold_common = gold_common[0]
    [gold_rare] = cur.execute('select gold_rare from cards_user where user_id = ?', (user_id,))
    gold_rare = gold_rare[0]
    [gold_epic] = cur.execute('select gold_epic from cards_user where user_id = ?', (user_id,))
    gold_epic = gold_epic[0]
    [gold_legendary] = cur.execute('select gold_legendary from cards_user where user_id = ?', (user_id,))
    gold_legendary = gold_legendary[0]

    await message.reply(f"Ваше количество карт:\n"
                        f"Обычных - {common}\n"
                        f"Редких - {rare}\n"
                        f"Эпических - {epic}\n"
                        f"Легендарных - {legendary}\n"
                        f"Золотых обычных - {gold_common}\n"
                        f"Золотых редких - {gold_rare}\n"
                        f"Золотых эпических - {gold_epic}\n"
                        f"Золотых легендарных - {gold_legendary}")


if __name__ == "__main__":
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
