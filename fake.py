import asyncio
import random
from aiogram import Bot, types
import sqlite3

BOT_TOKEN = '7429518608:AAFMU2R_CyyLqPhWl2LJTWxTQVPU1DhSppk'
CHANNEL_ID = -1002243436081
NICKS = [
    'яочочо','true','MoneyEarner | AnyBet', '💘 Fucking duck',' ЯЗЫК ПРОГРАММИСТА','a4d07c307fedd79b'
]

bot = Bot(token=BOT_TOKEN)

def get_settings():
    conn = sqlite3.connect('db.db')
    c = conn.cursor()

    c.execute('''
        SELECT * FROM settings
    ''')

    result = c.fetchone()

    conn.close()

    if result is None:
      return [0,0,60,600,1]
    return result

async def send_fake_activity():
    while True:
        settings = get_settings()

        if settings[4] == 0:
            await asyncio.sleep(60)  
            continue  

        nick = random.choice(NICKS)
        bet = round(random.uniform(1, 3),2)
        stav = ['Больше', 'меньше' 'чет' 'нечет','победа 1','победа 2']
        print(stav)
        bet1 = random.choice(stav)
        print(bet1)

        user_id = 6667646866
        user_first_name = nick
        user_username = nick

        message_text = f'{nick} отправил(а) {bet} USDT (${bet}).\n\n💬 {bet1}'
        print(message_text)

        message_entities = [
            types.MessageEntity(type='text_mention', offset=0, length=len(nick), user=types.User(id=user_id, is_bot=False, first_name=user_first_name, username=user_username, language_code='ru', is_premium=True)),
            types.MessageEntity(type='bold', offset=0, length=len(nick)),
            types.MessageEntity(type='text_link', offset=len(nick) + 1, length=11, url='http://t.me/CryptoBot?start=IVlkKngNxXPT'),
            types.MessageEntity(type='bold', offset=len(nick) + 12, length=len(f"{bet} USDT (${bet})."))
        ]

        
        await bot.send_message(
            chat_id=CHANNEL_ID,
            text=message_text,
            entities=message_entities,
            disable_notification=True
        )
        
        sleep = random.randint(settings[2],settings[3])
        print(f'[ FAKE USERS ]: Sleep {sleep}s. for next bet...\n')
        await asyncio.sleep(sleep)


asyncio.run(send_fake_activity())
