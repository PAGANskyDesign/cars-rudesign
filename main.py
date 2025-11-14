import asyncio
import os
import logging
import random
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import aiosqlite

# ======================
# КОНФИГУРАЦИЯ
# ======================

BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ Не задан BOT_TOKEN! Добавь его в Variables на Railway.")

CREATOR_USERNAME = "@sky_for_pagani2"
DB_PATH = "/tmp/cars_bot.db"

# Курсы валют
USD_TO_RUB = 80.0
USD_TO_EUR = 0.93

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()

# ======================
# ДАННЫЕ МАШИН (400+ моделей)
# ======================

CARS = [
    # Автосалон: Гиперкары и роскошь
    {"id": 1, "name": "Pagani Huayra", "price": 2500000, "year": 2011, "type": "salon", "max_global": 100, "image": "pagani_huayra.png"},
    {"id": 2, "name": "Pagani Utopia", "price": 2800000, "year": 2022, "type": "salon", "max_global": 99, "image": "pagani_utopia.png"},
    {"id": 3, "name": "Mercedes AMG Project: One", "price": 2700000, "year": 2022, "type": "salon", "max_global": 275, "image": "mercedes_project_one.png"},
    {"id": 4, "name": "McLaren Stirling Moss", "price": 5000000, "year": 2009, "type": "salon", "max_global": 6, "image": "mclaren_stirling_moss.png"},
    {"id": 5, "name": "Rolls Royce Boattail", "price": 28000000, "year": 2021, "type": "salon", "max_global": 5, "image": "rolls_royce_boattail.png"},
    {"id": 6, "name": "Brabham BT62", "price": 1500000, "year": 2018, "type": "salon", "max_global": 70, "image": "brabham_bt62.png"},
    {"id": 7, "name": "Bugatti Chiron", "price": 3000000, "year": 2016, "type": "salon", "max_global": 500, "image": "bugatti_chiron.png"},
    {"id": 8, "name": "Bugatti Tourbillon", "price": 4000000, "year": 2024, "type": "salon", "max_global": 250, "image": "bugatti_tourbillon.png"},
    {"id": 9, "name": "Bugatti Chiron Super Sport", "price": 3800000, "year": 2021, "type": "salon", "max_global": 80, "image": "bugatti_chiron_ss.png"},
    {"id": 10, "name": "Bugatti Veyron", "price": 1800000, "year": 2005, "type": "salon", "max_global": 450, "image": "bugatti_veyron.png"},
    {"id": 11, "name": "Hispano-Suiza Carmen", "price": 1700000, "year": 2019, "type": "salon", "max_global": 19, "image": "hispano_suiza_carmen.png"},
    {"id": 12, "name": "Spania GTA Spano", "price": 1200000, "year": 2013, "type": "salon", "max_global": 99, "image": "spania_gta_spano.png"},
    {"id": 13, "name": "Koenigsegg Regera", "price": 2200000, "year": 2015, "type": "salon", "max_global": 80, "image": "koenigsegg_regera.png"},
    {"id": 14, "name": "Rolls Royce DropTail", "price": 35000000, "year": 2023, "type": "salon", "max_global": 3, "image": "rolls_royce_droptail.png"},
    {"id": 15, "name": "McLaren 722", "price": 1000000, "year": 2007, "type": "salon", "max_global": 150, "image": "mclaren_722.png"},
    
    # Автосалон: Обычные
    {"id": 16, "name": "Spyker C8", "price": 500000, "year": 2000, "type": "salon", "max_global": 120, "image": "spyker_c8.png"},
    {"id": 17, "name": "Aston Martin One-77", "price": 1800000, "year": 2009, "type": "salon", "max_global": 77, "image": "aston_martin_one77.png"},
    {"id": 18, "name": "Ruf CTR3", "price": 800000, "year": 2007, "type": "salon", "max_global": 30, "image": "ruf_ctr3.png"},
    {"id": 19, "name": "SSC Ultimate Aero TT", "price": 700000, "year": 2009, "type": "salon", "max_global": 25, "image": "ssc_ultimate_aero.png"},
    {"id": 20, "name": "Zenvo ST1", "price": 1200000, "year": 2009, "type": "salon", "max_global": 15, "image": "zenvo_st1.png"},
    
    # DROP (примеры)
    {"id": 31, "name": "Mercedes-Benz S-Class", "price": 120000, "year": 2022, "type": "drop", "max_global": 1000, "image": "mercedes_sclass.png"},
    {"id": 32, "name": "BMW M5", "price": 110000, "year": 2023, "type": "drop", "max_global": 900, "image": "bmw_m5.png"},
    {"id": 33, "name": "Nissan GT-R", "price": 150000, "year": 2022, "type": "drop", "max_global": 800, "image": "nissan_gtr.png"},
    
    # Акция удачи
    {"id": 200, "name": "Rolls Royce Phantom II Jonckheere", "price": 8000000, "year": 1932, "type": "luck_case", "max_global": 1, "image": "rolls_phantom_jonckheere.png"},
    {"id": 201, "name": "W Motors Lykan Hypersport", "price": 3400000, "year": 2013, "type": "luck_case", "max_global": 7, "image": "w_motors_lykan.png"},
    
    # Тюнинг
    {"id": 300, "name": "Pagani Huayra BC", "price": 2800000, "year": 2016, "type": "tuning", "max_global": 40, "image": "pagani_huayra_bc.png"},
    {"id": 301, "name": "Brabus G900", "price": 500000, "year": 2023, "type": "tuning", "max_global": 100, "image": "brabus_g900.png"},
]

# Недвижимость
PROPERTIES = {
    "houses": [
        {"id": "h1", "name": "Дом The Vineyards Resort", "location": "Bulgaria, Aheloi", "price": 210000},
        {"id": "h2", "name": "Дом Updown Court", "location": "England, Windlesham", "price": 140000000},
        {"id": "h3", "name": "Особняк Daniel’s Lane", "location": "USA, NY", "price": 100000000},
    ],
    "villas": [
        {"id": "v1", "name": "Вилла Coastlands House", "location": "USA, California", "price": 2000000},
        {"id": "v2", "name": "Вилла Swiss Gold House", "location": "Швейцария", "price": 12000000},
        {"id": "v3", "name": "Вилла Villa Leopolda", "location": "Франция", "price": 506000000},
    ],
    "apartments": [
        {"id": "a1", "name": "Квартира Yaroslavl City", "location": "РФ, Ярославль", "price": 1050000},
        {"id": "a2", "name": "Таун-хаус Boka Place", "location": "Chernogoria, Tivan", "price": 910000},
    ],
    "other": [
        {"id": "o1", "name": "Небоскреб Commerzbank Tower", "location": "Франкфурт", "price": 1200000000, "income": 120000},
        {"id": "o2", "name": "Messeturm", "location": "Франкфурт", "price": 3700000000, "income": 200000},
    ]
}

# ======================
# БАЗА ДАННЫХ
# ======================

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                display_name TEXT,
                balance REAL DEFAULT 0,
                last_drop TEXT,
                last_luck_case TEXT,
                last_tuning_case TEXT,
                currency TEXT DEFAULT 'USD',
                last_promo_test TEXT,
                last_promo_test2 TEXT,
                last_promo_bt TEXT,
                last_promo_betatest TEXT,
                beta_test_remaining INTEGER DEFAULT 0,
                blocked INTEGER DEFAULT 0,
                last_income_time TEXT
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS user_cars (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                car_id INTEGER,
                is_duplicate BOOLEAN DEFAULT 0,
                source TEXT,
                acquired_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS global_car_counts (
                car_id INTEGER PRIMARY KEY,
                issued_count INTEGER DEFAULT 0
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS user_properties (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                property_id TEXT,
                acquired_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Предзаполнение глобальных лимитов
        for car in CARS:
            await db.execute('''
                INSERT OR IGNORE INTO global_car_counts (car_id, issued_count)
                VALUES (?, 0)
            ''', (car['id'],))
        
        await db.commit()

# ======================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ======================

async def get_user(user_id, username, display_name):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            INSERT OR IGNORE INTO users 
            (user_id, username, display_name) 
            VALUES (?, ?, ?)
        ''', (user_id, username, display_name))
        await db.commit()

async def add_car_to_user(user_id, car_id, source):
    async with aiosqlite.connect(DB_PATH) as db:
        # Проверка на дубликат
        cursor = await db.execute('''
            SELECT COUNT(*) FROM user_cars 
            WHERE user_id = ? AND car_id = ?
        ''', (user_id, car_id))
        is_duplicate = (await cursor.fetchone())[0] > 0
        
        # Проверка глобального лимита
        cursor = await db.execute('''
            SELECT issued_count FROM global_car_counts WHERE car_id = ?
        ''', (car_id,))
        issued_count = (await cursor.fetchone())[0]
        
        car = next((c for c in CARS if c['id'] == car_id), None)
        if not car:
            return False, "Машина не найдена"
        
        if car['max_global'] > 0 and issued_count >= car['max_global']:
            return False, "Достигнут глобальный лимит!"
        
        # Добавление машины
        await db.execute('''
            INSERT INTO user_cars (user_id, car_id, is_duplicate, source)
            VALUES (?, ?, ?, ?)
        ''', (user_id, car_id, is_duplicate, source))
        
        if not is_duplicate:
            await db.execute('''
                UPDATE global_car_counts SET issued_count = issued_count + 1 
                WHERE car_id = ?
            ''', (car_id,))
        
        # Начисление баланса за выпавшую машину
        if source in ["drop", "luck_case", "tuning"]:
            await db.execute('UPDATE users SET balance = balance + ? WHERE user_id = ?', (car['price'], user_id))
        
        await db.commit()
        return True, ""

async def get_user_balance(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
        result = await cursor.fetchone()
        return result[0] if result else 0

# ======================
# ОСНОВНЫЕ КОМАНДЫ
# ======================

@router.message(Command("start"))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or f"user_{user_id}"
    display_name = message.from_user.full_name
    
    await get_user(user_id, username, display_name)
    
    kb = [
        ["🚗 Автосалон", "💰 Мои средства"],
        ["🏆 Мои машины", "🎰 Выбить машину"],
        ["🎁 Акция удачи", "🔧 Тюнинг ателье"],
        ["🏠 Недвижимость", "🌍 Все машины"],
        ["🏆 Лидеры", "🔧 Консоль"]
    ]
    markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=btn) for btn in row] for row in kb], resize_keyboard=True)
    
    await message.answer(
        "🌟 Добро пожаловать в Car's by RuDesign!\n"
        "Собирайте коллекцию эксклюзивных автомобилей!",
        reply_markup=markup
    )

@router.message(Command("promo"))
async def cmd_promo(message: Message, command: CommandObject):
    user_id = message.from_user.id
    promo = command.args
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = await cursor.fetchone()
        if not user:
            await message.answer("Сначала напишите /start")
            return
        
        if promo == "test":
            if user[8]:  # last_promo_test
                await message.answer("Промокод уже использован!")
                return
            await db.execute('UPDATE users SET balance = balance + 1200000000, last_promo_test = ? WHERE user_id = ?', (datetime.now().isoformat(), user_id))
            await message.answer("✅ +1,200,000,000$")
        elif promo == "test2":
            if user[9]:
                await message.answer("Промокод уже использован!")
                return
            await db.execute('UPDATE users SET balance = balance + 150000000, last_promo_test2 = ? WHERE user_id = ?', (datetime.now().isoformat(), user_id))
            await message.answer("✅ +150,000,000$")
        elif promo == "BT":
            if user[10]:
                await message.answer("Промокод уже использован!")
                return
            await db.execute('UPDATE users SET balance = balance + 20000000, last_promo_bt = ? WHERE user_id = ?', (datetime.now().isoformat(), user_id))
            await message.answer("✅ +20,000,000$")
        elif promo == "BetaTest":
            if user[11]:
                await message.answer("Промокод уже использован!")
                return
            await db.execute('UPDATE users SET beta_test_remaining = 5, last_promo_betatest = ? WHERE user_id = ?', (datetime.now().isoformat(), user_id))
            await message.answer("✅ +5 кейсов 'Выбить машину'")
        else:
            await message.answer("❌ Неверный промокод!")
        await db.commit()

# ======================
# ЗАПУСК
# ======================

async def main():
    await init_db()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
