import time

from aiogram.dispatcher.filters import CommandStart

from data.config import sale_photo
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from loader import dp
from keyboards import *
from filters import IsAdmin, IsUser
import asyncio

catalog = '🛍️ Магазин'
cart = '🛒 Корзина'
sale = '🎁 Акція'
contacts = '📞Контакти'

settings = '⚙ Налаштування каталогу'
orders = '🚚 Замовлення'


# @dp.message_handler(CommandStart(), IsAdmin())
# async def admin_menu(message: Message):
#     markup = ReplyKeyboardMarkup(resize_keyboard=True)
#     markup.add(settings)
#     markup.add(orders)
#     await message.answer('Меню', reply_markup=markup)


# @dp.message_handler(CommandStart(), IsUser())
# async def user_menu(message: Message):
#     markup = ReplyKeyboardMarkup(resize_keyboard=True)
#     markup.add(catalog)
#     markup.insert(cart)
#     markup.add(sale).insert(contacts)
#     await message.answer('Меню', reply_markup=markup)


@dp.message_handler(IsUser(), text=sale)
async def user_menu(message: Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(catalog)
    markup.insert(cart)
    markup.add(sale).insert(contacts)
    await message.answer_photo(sale_photo, reply_markup=markup)
    await message.answer('🔥Акційна пропозиція🔥 '
                         '\n*Висота букета:*'
                         '\n`50-60 см`'
                         '\n*Основна квітка:*'
                         '\n`Троянда`'
                         '\n*Колір:*'
                         '\n`Червоний`', parse_mode='MarkdownV2')


@dp.message_handler(IsUser(), text=contacts)
async def user_menu(message: Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(catalog)
    markup.insert(cart)
    markup.add(sale).insert(contacts)
    await message.answer(' Магазини УКРАФЛОРА 🌷'
                         '\n📍 Київ, вул. Салютна, 2Б')
    await message.answer_location(latitude=50.4711362, longitude=30.4011574)
    await asyncio.sleep(2)
    await message.answer('📍 Київ, вул. Оноре де Бальзака, 2А ТЦ"Глобал"')
    await message.answer_location(latitude=50.4711362, longitude=30.4011574, reply_markup=markup)
    await message.answer('☎️ Безкоштовно по Україні')
    await message.answer("0800330088")
