from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

back_message = '👈 Назад'
confirm_message = '✅ Підтвердити замовлення'
all_right_message = '✅ Все вірно'
cancel_message = '🚫 Відмінити'
# menu_message = 'Menu'
checkout_message = '📦 Оформити замовлення'
cancel_cart_message = 'Очистити'
end_add_adivives_message = 'next'

catalog = '🛍️ Магазин'
cart = '🛒 Корзина'
sale = '🎁 Акція'
contacts = '📞Контакти'

settings = '⚙ Налаштування каталогу'
orders = '🚚 Замовлення'

# def menu_markup():
#     markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
#     markup.add(menu_message)
#
#     return markup


user_markup = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [
            KeyboardButton(text=catalog),
            KeyboardButton(text=cart)
        ],
        [
            KeyboardButton(text=sale),
            KeyboardButton(text=contacts)
        ]
    ]
)

admin_markup = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [
            KeyboardButton(text=settings),
            KeyboardButton(text=orders)
        ]
    ]
)


def cart_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(checkout_message)
    markup.add(cancel_cart_message)
    markup.add(back_message)

    return markup


def admin_defalt_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(confirm_message)
    markup.add(back_message)

    return markup


def confirm_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(confirm_message)
    markup.add(back_message)

    return markup


def back_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(back_message)

    return markup


def back_addetive_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(back_message)
    markup.add(end_add_adivives_message)

    return markup


def check_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.row(back_message, all_right_message)

    return markup


def submit_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.row(cancel_message, all_right_message)

    return markup
