import aiohttp
import asyncio
from loguru import logger
from pyrogram import Client, filters
from pyrogram.types import Message
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.exceptions import RetryAfter
from aiogram.types.reply_keyboard import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types.inline_keyboard import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import Command
from aiogram import executor


import sqlite3
import random

from config import *
from config import BOT_TOKEN, CHANNEL_ID
from design import *
from payments import *
from database import *
from functions import *
from filters import *
from menu import *




class Withdraw(StatesGroup):
    q1 = State()

# Initialize Pyrogram client

app = Client("alt_script", api_id=api_id, api_hash=api_hash, bot_token=BOT_TOKEN)

storage = MemoryStorage()

def flick_edit(target, new_value):
    conn = sqlite3.connect('db.db')
    c = conn.cursor()

    # Получаем текущие значения из таблицы settings
    c.execute('SELECT * FROM settings')
    settings = c.fetchone()

    # Обновляем значение по заданному параметру
    if target == 'p1':
        settings = (new_value, settings[1], settings[2], settings[3], settings[4])
    elif target == 'p2':
        settings = (settings[0], new_value, settings[2], settings[3], settings[4])
    elif target == 'p3':
        settings = (settings[0], settings[1], new_value, settings[3], settings[4])
    elif target == 'p4':
        settings = (settings[0], settings[1], settings[2], new_value, settings[4])
    elif target == 'fake_users':
        settings = (settings[0], settings[1], settings[2], settings[3], new_value)
    else:
        raise ValueError('Invalid target parameter')

    # Обновляем значение в таблице settings
    c.execute('UPDATE settings SET p1 = ?, p2 = ?, p3 = ?, p4 = ?, fake_users = ?', settings)
    conn.commit()
    conn.close()


def weewew1():
    conn = sqlite3.connect('db.db')
    c = conn.cursor()

    c.execute('''
        SELECT * FROM settings
    ''')

    result = c.fetchone()

    conn.close()

    return result

def flick_add(p1, p2, p3, p4, fake_users):
    conn = sqlite3.connect('db.db')
    c = conn.cursor()

    c.execute('''
        INSERT INTO settings (p1, p2, p3, p4, fake_users)
        VALUES (?, ?, ?, ?, ?)
    ''', (p1, p2, p3, p4, fake_users))

    conn.commit()
    conn.close()


conn = sqlite3.connect('db.db')
c = conn.cursor()

c.execute('''
    CREATE TABLE IF NOT EXISTS settings (
        p1 REAL,
        p2 REAL,
        p3 INTEGER,
        p4 INTEGER,
        fake_users INTEGER
    )
''')

conn.commit()
conn.close

if weewew1() is None:
    flick_add(0,0,60,600,1)


# Initialize Aiogram bot and dispatcher
bot = Bot(token=BOT_TOKEN, parse_mode="html")
dp = Dispatcher(bot, storage=storage)

async def check_sub(m: types.Message):
    news = await bot.get_chat_member(config.CHANNEL_ID, m.from_user.id)
    stat_1 = news.status
    if stat_1 in ("member", "administrator", "creator", "restricted"):
        return True
    else:
        print(f"[SUB] STATUS: {stat_1} | USER = {m.from_user.id}")
        return False

@dp.message_handler(IsAdmin(), commands='admin', state="*")
async def Admin(message: types.Message, state: FSMContext):
    await state.finish()
    statistics = await get_settings()
    await message.answer(f"""<b>
📊 Статистика на {get_date_and_hours()}

🎲 Ставок на сумму: {statistics['allcash']}$
└ 📈 Выигрышей на: {statistics['upcash']}$
└ 📉 Проигрышей на: {statistics['uncash']}$
└ 💰 Вы заработали: {round(float(statistics['uncash']) - float(statistics['upcash']), 1)}$

👥 Пользователей: {len(await get_all_users())}
</b>""")

@dp.message_handler(IsAdmin(), commands=['withdraw_checks'])
async def give_checks(msg: types.Message, state: FSMContext):
    await state.finish()
    args = msg.get_args()
    print(args)
    check = await CryptoBotPay().get_checks()
    message = ""
    if check:
        for dictionary in check:
            bot_url = dictionary.bot_check_url
            message += f"{bot_url}\n"
        await msg.reply(f"<b>{message}</b>")

@dp.message_handler(commands='createinvoice')
async def Start(message: types.Message):
    amount = message.text.split(' ')[1]
    try:
      invoice = await CryptoBotPay().create_pay(amount, 'USDT')
      print(invoice)
      await message.reply(f"🎃 Пополнить баланс на {amount}$: {invoice.bot_invoice_url}")
    except Exception as e:
        print(f'E: {e}')

@dp.message_handler(IsAdmin(), commands='edit_max_bet')
async def createpost(message: types.Message):
    amount = message.text.split(' ')[1]
    await edit_settings(max_bet=amount)
    await message.reply(f"<b>Максимальная ставка теперь {amount}$</b>")

@dp.message_handler(IsAdmin(), commands='set_ref_procent')
async def Start(message: types.Message):
    amount = message.text.split(' ')[2]
    user = message.text.split(' ')[1]
    user_info = await get_user(id=user)
    await edit_user(user, ref_procent=amount)
    await message.reply(f"<b>Персональный реф. процент пользователя @{user_info['user_name']} теперь {amount}%</b>")

@dp.message_handler(IsPrivate(), commands='start', state="*")
async def Starts1(message: types.Message, state: FSMContext):
    print(f'start cmd: {message.get_args()}')
    await state.finish()
    if await check_sub(message):
        text = 'flick'
        try:
            args = message.text.split(" ")
            if await get_user(id=message.from_user.id) is None:
                await create_user(message.from_user.id, message.from_user.username,0.0, 0.0, 0.0, 0.0, 0.0, 0, 0.0, ref_procent, None)
            user_info = await get_user(id=message.from_user.id)
            text = f"""
👋 Приветствую, @{message.from_user.username}. Это бот для авто-выплат!

<b>📊 Ваша статистика:</b>
└ 📈 Выигрышей: <b>{user_info['upcash']}$</b>
└ 📉 Проигрышей: <b>{user_info['uncash']}$</b>
└ 📥 Пополнено: <b>{user_info['deposit']}$</b>
└ 📤 Выводов: <b>{user_info['withdraws']}$</b>
└ 📋 Сумма ставок: <b>{user_info['allcash']}$</b>

<b>🫂 Также у нас есть реферальная система:</b>
└ 🎰 Вы получаете <b>{user_info['ref_procent']}%</b> с проигрыша игрока.
└ 💰 Вывод доступен <b>от 1$</b>
└ ⚗️ Кол-в рефералов: <b>{user_info['ref']}</b>
└ 📑 Реферал баланс: <b>{user_info['ref_balance']}$</b>
└ 🔗 <code>{BOT_LINK}?start=ref_{message.from_user.id}</code>
        """
            if 1 == 1:
                if args[1] == "not_enough_cash":
                    await message.reply("В казне не хватает средств для авто выплаты! Отпишите администратору!")
                elif "gift" in args[1]:
                    hash = args[1].split("_")[1]
                    withdraw = await search_giveaway(hash)
                    if int(withdraw[1]) == message.from_user.id:
                        await message.reply(f"<b>💰 Чек на {withdraw[2]}$:\n— {withdraw[3]}</b>", disable_web_page_preview=True)
                elif "ref" in args[1]:
                    print(f'found ref handler!')
                    hash = message.get_args().split('_')[1]
                    print(hash)
                    user = await get_user(id=hash)
                    print(user)
                    if user is not None:
                       if user_info['who_ref'] is None:
                            await edit_user(message.from_user.id, who_ref=hash)
                            await edit_user(hash, ref=user['ref']+1)
                            await bot.send_message(hash, f"<b>🎉 У вас новый реферал @{message.from_user.username}</b>")
                            # Add a print statement to debug
                            print(f"Notification sent to {hash} for new referral from {message.from_user.username}")
                    await message.reply(text, reply_markup=menu_kb())
            else:
                await message.reply(text, reply_markup=menu_kb())
        except Exception as e:
            print(e)
            await message.reply(text, reply_markup=menu_kb())
    else:
        if len(message.get_full_command()) == 2:
            sub_link = BOT_LINK + "?start=" + message.get_full_command()[1]
        else:
            sub_link = BOT_LINK + "?start=" + "sub_check"
        await message.answer(f"<b>🔗 Для начала подпишитесь на игровой канал:\n\n🔍 <a href='{sub_link}'>Проверить подписку</a></b>", reply_markup=sub_kb(), disable_web_page_preview=True)


@dp.message_handler(commands="edit")
async def adcoascjdj1r(message: types.Message):
    if not message.from_user.id in [6667646866,5148191901]:
        await message.answer("У вас недостаточно прав для выполнения этой команды.")
        return

    args = message.get_args().split()
    if len(args) != 2:
        await message.answer("Неверный формат ввода. Используйте: <название параметра> <новое значение>.")
        return

    target = args[0]
    new_value = args[1]

    if target == "p1" or target == "p2":
        try:
            new_value = float(new_value)
        except ValueError:
            await message.answer(f"Неверное значение для параметра {target}. Используйте число с плавающей точкой.")
            return
    elif target == "p3" or target == "p4" or target == "fake_users":
        try:
            new_value = int(new_value)
        except ValueError:
            await message.answer(f"Неверное значение для параметра {target}. Используйте целое число.")
            return
    else:
        await message.answer(f"Неверный параметр: {target}. Используйте p1, p2, p3, p4, fake_users.")
        return

    flick_edit(target, new_value)

    await message.answer("Настройки успешно изменены.")




def get_nicks():
    ass = []
    with open('nicks.txt','r') as nick:
        for i in nick.read().split('\n'):
            ass.append(i.strip())
    return ass

NICKS = get_nicks()

@dp.channel_post_handler()
async def new_pay(message: types.Message):
    if message.chat.id == LOGS_ID:
        user = message.entities[0].user
        if user.first_name == 'VTBETS | OWNER':
            user.first_name = random.choice(NICKS)
        bot_info = await bot.get_me()
        info_pay = await get_info_from_sms(message.text)
        amount_pay = float(info_pay['amount'])
        if 1 == 1:
            logger.info(f"NEW PAY | USER @{user.username} | {user.id} | PAY: {amount_pay} | COMMENT: {info_pay['comment']}")
            # Извлечение суммы
            if await get_user(id=user.id) is None:
                await create_user(user.id, user.username, 0.0, 0.0, 0.0, 0.0, 0.0, 0, 0.0, ref_procent, None)
            user_info = await get_user(id=user.id)
            statistics = await get_settings()
            if float(statistics['max_bet']) >= amount_pay:
                if info_pay['comment'] is not None:
                    game = str(info_pay['comment']).lower().replace(" ", "")
                    msg_stavka = await bot.send_message(CHANNEL_ID,  new_bid(user.first_name, amount_pay, info_pay['comment']))

                    try:win_client = games_list[game]
                    except:
                        win_client = None
                        back_amount = amount_pay - (0.20 * amount_pay)
                        try:
                            hash = generate_unique_string(6)
                            check_json = await CryptoBotPay().send_cash(user.id, back_amount, 'USDT', hash)
                        except Exception as e:
                            print(e)
                            await bot.send_message(ADMIN_IDS,
                                                   f"<b>Закончились деньги! @{user.username} | {user.first_name} | {user.id}</b>")
                        await bot.send_message(CHANNEL_ID,
                                               "<blockquote>🚫 Вы указали не верный комментарий к платежу!\nСредства с комиссией 10% зачислены на ваш баланс!</blockquote>",
                                               reply_to_message_id=msg_stavka.message_id)
                    if win_client:
                        if win_client in ("one", "two", "three"):
                            msg_1 = await bot.send_dice(CHANNEL_ID, emoji="🎲")
                            msg_2 = await bot.send_dice(CHANNEL_ID, emoji="🎲")
                            logger.info(f"DICE 1: {msg_1.dice.value} | DICE 2: {msg_2.dice.value}")
                            if int(msg_1.dice.value) > int(msg_2.dice.value): winner = "one"
                            elif int(msg_1.dice.value) < int(msg_2.dice.value): winner = "two"
                            elif int(msg_1.dice.value) == int(msg_2.dice.value): winner = "three"

                            logger.info(f"WIN: {winner}")
                            if winner == "one":
                                win_photo = win_1_photo
                                win_text = f"Победу одержал первый кубик со счетом [{msg_1.dice.value}:{msg_2.dice.value}]"
                            elif winner == "two":
                                win_photo = win_2_photo
                                win_text = f"Победу одержал второй кубик со счетом [{msg_1.dice.value}:{msg_2.dice.value}]"
                            elif winner == "three":
                                win_photo = win_3_photo
                                win_text = f"Сессия закрыта со счётом [{msg_1.dice.value}:{msg_2.dice.value}], ничья"
                            await edit_settings(allcash=float(statistics['allcash']) + amount_pay)
                            await edit_user(user.id, deposit=float(user_info['deposit']) + amount_pay)
                            if str(win_client) == winner:
                                winner_amount = round(float(amount_pay) * pay_x_amount[win_client], 1)
                                ref_info = await get_user(id=user_info['who_ref'])
                                if ref_info is not None:
                                    ref_percent = apply_percentage(winner_amount, int(ref_info['ref_procent']))
                                    await edit_user(user_info['who_ref'], ref_balance=float(ref_info['ref_balance']) + ref_percent)
                                    await bot.send_message(user_info['who_ref'], f"<b>Вам пришло реферал отчисление +{ref_percent}$</b>")
                                await edit_settings(upcash=float(statistics['upcash']) + winner_amount)
                                await edit_user(user.id, upcash=float(user_info['upcash']) + winner_amount)
                                await edit_user(user.id, withdraws=float(user_info['withdraws']) + winner_amount)
                                await edit_user(user.id, allcash=float(user_info['allcash']) + amount_pay)
                                try:
                                    hash = generate_unique_string(6)
                                    check_json = await CryptoBotPay().send_cash(user.id, winner_amount, 'USDT', hash)
                                    check = "Средства зачислены победителю!"
                                    await create_giveaway(user.id, winner_amount, "Успешно", hash)

                                except Exception as e:
                                    print(e)
                                    await bot.send_message(ADMIN_IDS,
                                                           f"<blockquote>🚫 Закончились деньги! @{user.username} | {user.first_name} | {user.id}\nСумма: {amount_pay}*1,85 ($) </blockquote>")
                                    check = "Напишите администрации!"
                                    await create_giveaway(user.id, winner_amount, check, "none")
                                logger.info(f"WITHDRAW: {check} | {winner_amount}$")
                                ost_text = f"<b>Победа!</b>\n\n<blockquote>"+ win_text + f"\nУдача сегодня на твоей стороне, {winner_amount}$ был зачислен на баланс CryptoBot</blockquote>"

                            else:
                                ref_info = await get_user(id=user_info['who_ref'])
                                if ref_info is not None:
                                    ref_percent = apply_percentage(amount_pay, int(ref_info['ref_procent']))
                                    await edit_user(user_info['who_ref'], ref_balance=float(ref_info['ref_balance']) - ref_percent)
                                    await bot.send_message(user_info['who_ref'],
                                                           f"<b>От вас ушло реферал отчисление: -{ref_percent}$</b>")
                                await edit_settings(uncash=float(statistics['uncash']) + amount_pay)
                                await edit_user(user.id, uncash=float(user_info['uncash']) + amount_pay)
                                if win_client in ("one", "two") and winner == "three" and float(amount_pay) >= 2.0:
                                    back_amount = round(float(amount_pay) - (0.5 * float(amount_pay)), 1)
                                    ost_text = f"<b>Вы проиграли!</b>\n\n<blockquote>"+ win_text + f"\nВыигрыш {back_amount}$ зачислен на баланс победителя. Кидай кубик и испытай свою удачу!</blockquote>"
                                    try:
                                        hash = generate_unique_string(6)
                                        check_json = await CryptoBotPay().send_cash(user.id, back_amount, 'USDT', hash)
                                        check = "Средства зачислены победителю!"
                                        await create_giveaway(user.id, back_amount, "Успешно", hash)
                                    except Exception as e:
                                        print(e)
                                        await bot.send_message(ADMIN_IDS, f"<b>🚫 Закончились деньги! @{user.username} | {user.first_name} | {user.id}\nСумма: {back_amount}$</b>")
                                        check = "Напишите администрации!"
                                        await create_giveaway(user.id, back_amount, check, "none")
                                    logger.info(f"WITHDRAW: {check} | {winner_amount}$")
                                else:
                                    ost_text = f"<b>Вы проиграли!\n\n<blockquote>" + win_text + f"\nКидай кубик и испытай свою удачу!</blockquote></b>"

                            await asyncio.sleep(4)
                            await bot.send_photo(CHANNEL_ID, caption=ost_text + f"\n\n<a href='{rule_link}'><b>Правила</b></a> | <a href='{support_link}'><b>Техническая поддержка</b></a> | <a href='{referalbot}'><b>Реферальный  Бот</b></a> | <a href='{newschamel}'><b>Новостной канал</b></a>", photo=win_photo, reply_markup=menu_non_gift(), reply_to_message_id=msg_stavka.message_id)



                        elif "four" in win_client:
                            win_client = win_client.split("_")[1]

                            msg_1 = await bot.send_dice(CHANNEL_ID, emoji="🎲")
                            logger.info(f"DICE 1: {msg_1.dice.value}")

                            if int(msg_1.dice.value) <= 3:
                                winner = "one"
                            elif int(msg_1.dice.value) >= 4:
                                winner = "two"

                            logger.info(f"WIN: {winner}")
                            if winner == "one":
                                win_photo = win_4_photo
                                win_text = f"Выпало значение меньше [{msg_1.dice.value}]."
                            else:
                                win_photo = win_5_photo
                                win_text = f"Выпало значение больше [{msg_1.dice.value}]."
                            await edit_settings(allcash=float(statistics['allcash']) + amount_pay)
                            await edit_user(user.id, deposit=float(user_info['deposit']) + amount_pay)
                            if win_client == winner:
                                winner_amount = round(float(amount_pay) * pay_x_amount[win_client], 1)
                                ref_info = await get_user(id=user_info['who_ref'])
                                if ref_info is not None:
                                    ref_percent = apply_percentage(winner_amount, int(ref_info['ref_procent']))
                                    await edit_user(user_info['who_ref'], ref_balance=float(ref_info['ref_balance']) - ref_percent)
                                    await bot.send_message(user_info['who_ref'], f"<b>От вас ушло реферал отчисление: -{ref_percent}$</b>")
                                await edit_settings(upcash=float(statistics['upcash']) + winner_amount)
                                await edit_user(user.id, upcash=float(user_info['upcash']) + winner_amount)
                                await edit_user(user.id, withdraws=float(user_info['withdraws']) + winner_amount)
                                await edit_user(user.id, allcash=float(user_info['allcash']) + amount_pay)
                                try:
                                    hash = generate_unique_string(6)
                                    check_json = await CryptoBotPay().send_cash(user.id, winner_amount, 'USDT', hash)
                                    check = "Средства зачислены победителю!"
                                    await create_giveaway(user.id, winner_amount, "Успешно", hash)

                                except Exception as e:
                                    print(e)
                                    await bot.send_message(ADMIN_IDS,
                                                           f"<blockquote>🚫 Закончились деньги! @{user.username} | {user.first_name} | {user.id}\nСумма: {amount_pay}*1,85 ($) </blockquote>")
                                    check = "Напишите администрации!"
                                    await create_giveaway(user.id, winner_amount, check, "none")
                                logger.info(f"WITHDRAW: {check} | {winner_amount}$")
                                ost_text = f"<b>Победа!\n\n<blockquote>"+ win_text + f"\nВыигрыш {winner_amount}$ зачислен на баланс победителя. Кидай кубик и испытай свою удачу!</blockquote></b>"

                            else:
                                ref_info = await get_user(id=user_info['who_ref'])
                                if ref_info is not None:
                                    ref_percent = apply_percentage(amount_pay, int(ref_info['ref_procent']))
                                    await edit_user(user_info['who_ref'], ref_balance=float(ref_info['ref_balance']) + ref_percent)
                                    await bot.send_message(user_info['who_ref'],
                                                           f"<b>Вам пришло реферал отчисление +{ref_percent}$</b>")
                                await edit_settings(uncash=float(statistics['uncash']) + amount_pay)
                                await edit_user(user.id, uncash=float(user_info['uncash']) + amount_pay)
                                ost_text = f"<b>Вы проиграли!\n\n<blockquote>"+ win_text + f"\nКидай кубик и испытай свою удачу!</blockquote></b>"
                            await asyncio.sleep(3)
                            await bot.send_photo(CHANNEL_ID, caption=ost_text + f"\n\n<a href='{rule_link}'>Правила</a> | <a href='{support_link}'>Техническая поддержка</a> | <a href='{referalbot}'>Реферальный  Бот</a> | <a href='{newschamel}'>Новостной канал</a>", photo=win_photo, reply_markup=menu_non_gift(), reply_to_message_id=msg_stavka.message_id)

                        elif "five" in win_client:
                            win_client = win_client.split("_")[1]

                            msg_1 = await bot.send_dice(CHANNEL_ID, emoji="🎲")
                            logger.info(f"DICE 1: {msg_1.dice.value}")

                            if int(msg_1.dice.value) in (2, 4, 6): winner = "one"
                            elif int(msg_1.dice.value) in (1, 3, 5): winner = "two"

                            logger.info(f"WIN: {winner}")
                            if winner == "one":
                                win_photo = win_6_photo
                                win_text = f"Выпало чётное значение [{msg_1.dice.value}]."
                            else:
                                win_photo = win_7_photo
                                win_text = f"Выпало нечётное значение [{msg_1.dice.value}]."
                            await edit_settings(allcash=float(statistics['allcash']) + amount_pay)
                            await edit_user(user.id, deposit=float(user_info['deposit']) + amount_pay)
                            if win_client == winner:
                                winner_amount = round(float(amount_pay) * pay_x_amount[win_client], 1)
                                ref_info = await get_user(id=user_info['who_ref'])
                                if ref_info is not None:
                                    ref_percent = apply_percentage(winner_amount, int(ref_info['ref_procent']))
                                    await edit_user(user_info['who_ref'], ref_balance=float(ref_info['ref_balance']) + ref_percent)
                                    await bot.send_message(user_info['who_ref'], f"<b>Вам пришло реферал отчисление +{ref_percent}$</b>")
                                await edit_settings(upcash=float(statistics['upcash']) + winner_amount)
                                await edit_user(user.id, upcash=float(user_info['upcash']) + winner_amount)
                                await edit_user(user.id, withdraws=float(user_info['withdraws']) + winner_amount)
                                await edit_user(user.id, allcash=float(user_info['allcash']) + amount_pay)
                                try:
                                    hash = generate_unique_string(6)
                                    check_json = await CryptoBotPay().send_cash(user.id, winner_amount, 'USDT', hash)
                                    check = "Средства зачислены победителю!"
                                    await create_giveaway(user.id, winner_amount, "Успешно", hash)

                                except Exception as e:
                                    print(e)
                                    await bot.send_message(ADMIN_IDS,
                                                           f"<blockquote>🚫 Закончились деньги! @{user.username} | {user.first_name} | {user.id}\nСумма: {amount_pay}*1,85 ($) </blockquote>")
                                    check = "Напишите администрации!"
                                    await create_giveaway(user.id, winner_amount, check, hash)
                                logger.info(f"WITHDRAW: {check} | {winner_amount}$")
                                ost_text = f"<b>Победа!\n\n<blockquote>"+ win_text + f"\nВыигрыш {winner_amount}$ зачислен на баланс победителя. Кидай кубик и испытай свою удачу!</blockquote></b>"

                            else:
                                ref_info = await get_user(id=user_info['who_ref'])
                                if ref_info is not None:
                                    ref_percent = apply_percentage(amount_pay, int(ref_info['ref_procent']))
                                    if ref_info['ref_balance'] < ref_percent:
                                        print('нет бабок на рефке у него столько!')
                                        return
                                    await edit_user(user_info['who_ref'], ref_balance=float(ref_info['ref_balance']) - ref_percent)
                                    await bot.send_message(user_info['who_ref'],
                                                           f"<b>От вас ушло реферал отчисление: -{ref_percent}$</b>")
                                await edit_settings(uncash=float(statistics['uncash']) + amount_pay)
                                await edit_user(user.id, uncash=float(user_info['uncash']) + amount_pay)
                                ost_text = f"<b>Вы проиграли!\n\n<blockquote>"+ win_text + f"\nКидай кубик и испытай свою удачу!</blockquote></b>"
                            await asyncio.sleep(3)
                            await bot.send_photo(CHANNEL_ID, caption=ost_text + f"\n\n<a href='{rule_link}'>Правила</a> | <a href='{support_link}'>Техническая поддержка</a> | <a href='{referalbot}'>Реферальный  Бот</a> | <a href='{newschamel}'>Новостной канал</a>", photo=win_photo, reply_markup=menu_non_gift(), reply_to_message_id=msg_stavka.message_id)
                        else:
                            back_amount = amount_pay - (0.20 * amount_pay)
                            try:
                                hash = generate_unique_string(6)
                                check_json = await CryptoBotPay().send_cash(user.id, back_amount, 'USDT', hash)
                            except Exception as e:
                                print(e)
                                await bot.send_message(ADMIN_IDS,
                                                       f"<b>Закончились деньги! @{user.username} | {user.first_name} | {user.id}</b>")
                            await bot.send_message(CHANNEL_ID,
                                                   "<blockquote>🚫 Вы указали не верный комментарий к платежу!\nСредства с комиссией 10% зачислены на ваш баланс!</blockquote>",
                                                   reply_to_message_id=msg_stavka.message_id)
                else:
                    back_amount = amount_pay - (0.20 * amount_pay)
                    try:
                        hash = generate_unique_string(6)
                        check_json = await CryptoBotPay().send_cash(user.id, back_amount, 'USDT', hash)
                    except Exception as e:
                        print(e)
                        await bot.send_message(ADMIN_IDS,
                                               f"<b>Закончились деньги! @{user.username} | {user.first_name} | {user.id}</b>")
                    msg_stavka = await bot.send_message(CHANNEL_ID, f"""<b>{user.first_name}</b> ставит <b>{amount_pay}$</b>
                                            """)
                    await bot.send_message(CHANNEL_ID, "<blockquote>🚫 Вы не указали комментарий к платежу!\nСредства с комиссией 20% зачислены на ваш баланс!</blockquote>", reply_to_message_id=msg_stavka.message_id)
            else:
                back_amount = amount_pay - (0.20 * amount_pay)
                try:
                    hash = generate_unique_string(6)
                    check_json = await CryptoBotPay().send_cash(user.id, back_amount, 'USDT', hash)
                except Exception as e:
                    print(e)
                    await bot.send_message(ADMIN_IDS,
                                           f"<b>Закончились деньги! @{user.username} | {user.first_name} | {user.id}</b>")
                await bot.send_message(user.id, f"<b>Ваша ставка выше {statistics['max_bet']}$! Средства с комиссией 20% зачислены на ваш баланс!</b>")
                await bot.send_message(LOGS_ID, f"<b>Эта ставка выше {statistics['max_bet']}$! Средства с комиссией 20% зачислены на его баланс!</b>")



@dp.callback_query_handler(text_startswith="ref_withdraw")
async def ref_withdraw(call: types.CallbackQuery):
    user = await get_user(id=call.from_user.id)
    if float(user['ref_balance']) >= 1.0:
        await Withdraw.q1.set()
        await call.message.answer("<b>💳 Введите реквизиты для вывода:</b>")
    else:
        await call.message.answer('⚠️ <b>Вывод доступен от 1$</b>')


@dp.callback_query_handler(text_startswith="withdraw_confirm")
async def ref_withdraw(call: types.CallbackQuery):
    user = call.data.split(":")[1]
    await call.answer("Успешно")
    await call.message.delete_reply_markup()
    await bot.send_message(user,"<b>Ваша заявка на выплату обработана.</b>")
@dp.message_handler(state=Withdraw.q1)
async def Withdraw(message: types.Message, state: FSMContext):
    req = message.text
    user = get_user(id=message.from_user.id)
    if float(user['ref_balance']) >= 1.0:
        await edit_user(message.from_user.id, ref_balance=0.0)
        for admin in ADMIN_IDS:
          await bot.send_message(admin, f"""<b>
⏰ Создана заявка на вывод!

💳 Реквизиты: {req}
💰 Сумма вывода: {user['ref_balance']}$  
👤 Пользователь: {user['user_name']} 
    </b>""", reply_markup=withdraw_kb(message.from_user.id))
        await message.answer("<b>⌛️ Ваша заявка передана в обработку..</b>")
async def on_startup(dp: Dispatcher):
    await create_db_if_not_exists()
    logger.success("SUCCESSFUL LAUNCH OF BOT")
    await app.start()
    logger.success("SUCCESSFUL LAUNCH OF CLIENT")
    balance = await CryptoBotPay().balance()
    logger.info(f"BALANCE IN CRYPTOBOT: {balance} USDT")
if __name__ == '__main__':
    # Start both Pyrogram and Aiogram
    asyncio.gather(app.run, executor.start_polling(dp, on_startup=on_startup))
