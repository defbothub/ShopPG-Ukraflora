from data.config import sale_photo
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from loader import dp
from keyboards import *
from filters import IsAdmin, IsUser

catalog = '💐Букети'
cart = '🛒 Корзина'
sale = '🎁 Акція'
contacts = '📞Контакти'

settings = '⚙ Налаштування каталогу'
orders = '🚚 Замовлення'


@dp.message_handler(IsAdmin(), text=menu_message)
async def admin_menu(message: Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(settings)
    markup.add(orders)
    await message.answer('Меню', reply_markup=markup)


@dp.message_handler(IsUser(), text=menu_message)
async def user_menu(message: Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(catalog)
    markup.insert(cart)
    markup.add(sale).insert(contacts)
    await message.answer('Меню', reply_markup=markup)


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
    await message.answer('📍 Магазин УКРАФЛОРА: Київ, вул. Салютна, 2б')
    await message.answer_location(latitude=50.4711362, longitude=30.4011574, reply_markup=markup)

