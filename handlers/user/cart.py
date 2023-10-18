from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from keyboards.inline.products_from_cart import product_markup, product_cb
from keyboards.default.markups import *
from .menu import user_menu
from aiogram.types.chat import ChatActions
from states import CheckoutState
from loader import dp, db, bot, logger
from filters import IsUser
from .menu import cart
from utils.db.models import Products, Ordered_products, Orders
from sqlalchemy.orm import joinedload

'''Показать корзину'''


@dp.message_handler(IsUser(), text=cart)
async def process_cart(message: Message, state: FSMContext):
    logger.info(
        f"User id - {message.from_user.id} name - {message.from_user.first_name} showed all products in cart")
    # Вытаскиваем заказ по tg_uid и проверяем его статус
    order = db.db_session.query(Orders).filter_by(
        tg_uid=message.chat.id).filter(Orders.is_orderd == False).first()
    if order == None:
        ordered_products = []
        await message.answer('Ваша корзина порожня.', reply_markup=menu_markup())
    else:
        # Вытаскиваем все заказанные продукты по оредру
        ordered_products = db.db_session.query(Ordered_products, Orders) \
            .join(Orders, Ordered_products.order_id == Orders.id) \
            .filter(Orders.id == order.id) \
            .options(joinedload(Ordered_products.product)) \
            .all()
        await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
        async with state.proxy() as data:
            data['products'] = {}
        order_cost = 0
        for orderd_product, _ in ordered_products:
            # Вытаскиваем информацию по продукту
            product = db.db_session.query(Products).filter_by(
                id=orderd_product.product_id).first()

            if product == None:
                db.db_session.delete(orderd_product)
                db.db_session.commit()
            else:
                # считаем цену всех продуктов
                order_cost += product.price

                async with state.proxy() as data:
                    data['products'][product.id] = (
                        product, orderd_product, order)
                markup = product_markup(product.id, orderd_product.quantity)
                text = f'{product.title}\n\n{product.body}\n\nЦіна: -  {product.price} ₴.'

                await message.answer_photo(photo=product.photo,
                                           caption=text,
                                           reply_markup=markup)
        if order_cost != 0:
            await message.answer('Перейти до оформлення?',
                                 reply_markup=cart_markup())

'''В корзине при нажатии на цифру под товаром'''


@dp.callback_query_handler(IsUser(), product_cb.filter(action='count'))
async def product_count_callback_handler(query: CallbackQuery, callback_data: dict, state: FSMContext):
    idx = callback_data['id']
    async with state.proxy() as data:
        _, orderd_product, _ = data['products'][int(idx)]
        if 'products' not in data.keys():
            await process_cart(query.message, state)
        else:
            await query.answer('Кількість - ' + str(orderd_product.quantity))
    db.db_session.commit()

'''В корзине при нажатии на уменьшение или увеличение под товаром'''


@dp.callback_query_handler(IsUser(), product_cb.filter(action='increase'))
@dp.callback_query_handler(IsUser(), product_cb.filter(action='decrease'))
async def product_callback_handler(query: CallbackQuery, callback_data: dict, state: FSMContext):
    id = callback_data['id']
    action = callback_data['action']
    async with state.proxy() as data:
        if 'products' not in data.keys():
            await process_cart(query.message, state)
        else:
            _, orderd_product, _ = data['products'][int(id)]
            '''Увеличиваем кол-во продукта'''
            orderd_product = db.db_session.query(
                Ordered_products).filter_by(id=orderd_product.id).first()
            orderd_product.quantity += 1 if 'increase' == action else -1
            db.db_session.commit()
            if orderd_product.quantity == 0:
                db.db_session.delete(orderd_product)
                db.db_session.commit()
                await query.message.delete()
            else:
                await query.message.edit_reply_markup(product_markup(id, orderd_product.quantity))
    db.db_session.commit()
    orderlen = db.db_session.query(Ordered_products).filter_by(
        id=orderd_product.id).count()
    if orderlen == 0:
        await process_cart(query.message, state)

'''В корзине при нажатии на ОФОРМИТЬ ЗАКАЗ'''


@dp.message_handler(IsUser(), text=checkout_message)
async def process_checkout(message: Message, state: FSMContext):
    await CheckoutState.check_cart.set()
    await checkout(message, state)

'''Считает и показывает цену'''


async def checkout(message, state):
    answer = ''
    total_price = 0

    async with state.proxy() as data:
        for product, ordered_product, _ in data['products'].values():
            ordered_product = db.db_session.query(
                Ordered_products).filter_by(id=ordered_product.id).first()
            tp = product.price
            answer += f"<b>{product.title}</b> {ordered_product.quantity} шт. по {product.price} ₴\n"
            answer += f'<b>Разом - {tp * ordered_product.quantity} ₴</b>\n'

            total_price += tp * ordered_product.quantity

    await message.answer(f'{answer}\nЗагальна сума замовлення: {total_price} ₴',
                         reply_markup=check_markup())


'''Отчистка корзины'''


@dp.message_handler(IsUser(), text=cancel_cart_message)
async def clear_cart(message: Message):
    logger.info(
        f"User id - {message.from_user.id} name - {message.from_user.first_name} clear a cart.")
    order_id = db.db_session.query(Orders).filter_by(
        tg_uid=message.chat.id).first()
    db.db_session.delete(order_id)
    db.db_session.commit()
    await message.answer("Корзина очищена.\nТисніть Menu, щоб продовжити.", reply_markup=menu_markup())

'''В корзине написал текст'''


@dp.message_handler(IsUser(), lambda message: message.text not in [all_right_message, back_message], state=CheckoutState.check_cart)
async def process_check_cart_invalid(message: Message):
    await message.reply('Такого варіанту не було.')

'''При потверждении нажал назад'''


@dp.message_handler(IsUser(), text=back_message, state=CheckoutState.check_cart)
async def process_check_cart_back(message: Message, state: FSMContext):
    await state.finish()
    await process_cart(message, state)

'''При потверждении нажал потвердить'''


@dp.message_handler(IsUser(), text=all_right_message, state=CheckoutState.check_cart)
async def process_check_cart_all_right(message: Message, state: FSMContext):
    await CheckoutState.next()
    await message.answer("Вкажіть свій номер телефону.",
                         reply_markup=back_markup())

'''При вводе имени нажал назад'''


@dp.message_handler(IsUser(), text=back_message, state=CheckoutState.name)
async def process_name_back(message: Message, state: FSMContext):
    await CheckoutState.check_cart.set()
    await checkout(message, state)

'''При вводе имени ввел имя'''


@dp.message_handler(IsUser(), state=CheckoutState.name)
async def process_name(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
        if 'address' in data.keys():
            await confirm(message)
            await CheckoutState.confirm.set()
        else:
            await CheckoutState.next()
            await message.answer("🔹Доставка по Києву 100 грн.\nПри замовленні від 1000 грн. доставка безкоштовна.\n🔹Вкажіть адресу доставки.",
                                 reply_markup=back_markup())

'''При вводе адреса нажал назад'''


@dp.message_handler(IsUser(), text=back_message, state=CheckoutState.address)
async def process_address_back(message: Message, state: FSMContext):

    async with state.proxy() as data:

        await message.answer("Змінити номер з <b>" + data['name'] + '</b>?',
                             reply_markup=back_markup())

    await CheckoutState.name.set()

'''При вводе адреса ввел адрес'''


@dp.message_handler(IsUser(), state=CheckoutState.address)
async def process_address(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['address'] = message.text
    await confirm(message)
    await CheckoutState.next()

'''Потверждение'''


async def confirm(message):
    await message.answer('Перевірте чи все правильно оформлено і підтвердіть замовлення.',
                         reply_markup=confirm_markup())

'''При потверждении заказа ввел текст вместо нажатия на кнопку'''


@dp.message_handler(IsUser(), lambda message: message.text not in [confirm_message, back_message], state=CheckoutState.confirm)
async def process_confirm_invalid(message: Message):
    await message.reply('Такого варіанту не було.')

'''При потверждении заказа нажал назад'''


@dp.message_handler(IsUser(), text=back_message, state=CheckoutState.confirm)
async def process_confirm(message: Message, state: FSMContext):
    await CheckoutState.address.set()
    async with state.proxy() as data:
        await message.answer('Змінити адресу з <b>' + data['address'] + '</b>?',
                             reply_markup=back_markup())

'''Потвердил заказ'''


@dp.message_handler(IsUser(), text=confirm_message, state=CheckoutState.confirm)
async def process_confirm(message: Message, state: FSMContext):
    markup = ReplyKeyboardRemove()
    logger.info(
        f"User id - {message.from_user.id} name - {message.from_user.first_name} Deal was made.")
    async with state.proxy() as data:
        cid = message.chat.id
        '''Вытаскиваем заказ меняем его статус и добовляем имя и адрес'''
        order = db.db_session.query(Orders).filter(
            Orders.tg_uid == cid).filter(Orders.is_orderd == False).first()
        order.is_orderd = True
        order.usr_name = data['name']
        order.usr_address = data['address']
        db.db_session.commit()
        await message.answer("Ок! Ваше замовлення прийняте. \nТелефон: <b>" + data['name'] + '</b>\nАдреса: <b>' + data['address'] + '</b>', reply_markup=markup)

    await state.finish()
    await bot.send_message(chat_id=6128561399, text="Нове замовлення!")
    await message.answer("Дякуємо за замовлення! \nЩоб продовжити покупки, натисніть Menu", reply_markup=menu_markup())
