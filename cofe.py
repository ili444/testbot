import telebot
import dbworker
import os 
import shelve
import datetime
from datetime import datetime
import random
from telebot.types import LabeledPrice
from telebot import types
import urllib.request as urllib2
from flask import Flask, request
TOKEN = os.environ['token2']
bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)
user_dict = {}

class User:
    def __init__(self, start):
        self.start = start
        self.num = None
        self.name_lot = None
        self.price = None
        self.total_price = None
        self.pic = None
        self.number_ship = None
        self.time = None


def dobavki():
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(types.InlineKeyboardButton("⬅ Назад", callback_data='назад_инлайн'),
               types.InlineKeyboardButton("Корица", callback_data='Корица'),
               types.InlineKeyboardButton("Горячий шоколад 20 мл +30 ₽", callback_data='Шоколад'),
               types.InlineKeyboardButton("Лимон 10 гр +15 ₽", callback_data='Лимон'),
               types.InlineKeyboardButton("Молоко 50 гр", callback_data='Молоко'),
               types.InlineKeyboardButton("🛒 В Корзину", callback_data='корзина')
               )
    return markup




def catalog():
    keyboard = types.InlineKeyboardMarkup()
    switch_button1 = types.InlineKeyboardButton(text="Кофе", switch_inline_query_current_chat="Кофе")
    switch_button2 = types.InlineKeyboardButton(text="Десерт", switch_inline_query_current_chat="Десерт")
    keyboard.add(switch_button1, switch_button2)
    return keyboard


def num_markup1():
    markup = types.InlineKeyboardMarkup()
    a1 = types.InlineKeyboardButton("-", callback_data=u'-1')
    a2 = types.InlineKeyboardButton('1', callback_data='jr')
    a3 = types.InlineKeyboardButton("+", callback_data=u'+1')
    a4 = types.InlineKeyboardButton(text='⬅ Назад', switch_inline_query_current_chat="Кофе")
    a6 = types.InlineKeyboardButton("☕ Добавки", callback_data=u'добавки')
    a5 = types.InlineKeyboardButton("🛒 Корзина", callback_data='корзина')
    markup.add(a1, a2, a3)
    markup.add(a4, a5)
    markup.add(a6)
    return markup

def num_markup2(callback, num):
    markup = types.InlineKeyboardMarkup()
    a1 = types.InlineKeyboardButton("-", callback_data=u'-1')
    a2 = types.InlineKeyboardButton(str(num), callback_data='jr')
    a3 = types.InlineKeyboardButton("+", callback_data=u'+1')
    a4 = types.InlineKeyboardButton(text='⬅ Назад', switch_inline_query_current_chat="Кофе")
    a6 = types.InlineKeyboardButton("☕ Добавки", callback_data=u'добавки')
    a5 = types.InlineKeyboardButton("🛒 Корзина", callback_data='корзина')
    markup.add(a1, a2, a3)
    markup.add(a4, a5)
    markup.add(a6)
    return markup

def check_basket(chat_id, callback):
    chat_id = callback.from_user.id
    user = user_dict[chat_id]
    with shelve.open('user_db.py') as db:
        lst3 = list(db.keys())
        if list(filter(lambda y: str(chat_id) in y, lst3)) == []:
            bot.send_message(chat_id, 'Ваша корзина пуста!', reply_markup=add_lot())
        else:
            l = []
            s = []
            r = []
            lst3 = list(db.keys())
            lst = list((filter(lambda x: str(chat_id) in x, lst3)))
            for dd in lst:
                a = db.get(dd)
                r.append(a)
            for line3 in r:
                line2 = ' '.join(line3[:3])
                lin = line3[2]
                s.append(float(lin))
                l.append(line2)
            total_price = sum(s)
            m = ' ₽\n\n🔹 '.join(l)
            user.total_price = total_price
            bot.send_message(chat_id, 'Ваша корзина :\n\n'
                                      f'🔹 {m} ₽.\n\n'
                                      f'Итого: {str(total_price)}  ₽.', reply_markup=finish_markup())


@bot.message_handler(commands=['start', 'reset'])
def callback_inline(message):
    chat_id = message.from_user.id
    start = 'ok'
    user = User(start)
    user_dict[chat_id] = user
    user_markup1 = telebot.types.ReplyKeyboardMarkup(True, True)
    user_markup1.row('☕ Каталог', '🛒 Корзина')
    user_markup1.row('📌 Акции', '📲 Обратная связь')
    name = message.from_user.first_name
    dbworker.set_state(str(message.chat.id), '1')
    bot.send_message(message.chat.id, f'Приветствую, {name}! Я Кофе-бот!\n\nУ нас ты можешь заказать кофе!',
                     reply_markup=user_markup1)
    bot.send_message(message.from_user.id, 'Выбери категорию:',
                         reply_markup=catalog())


@bot.inline_handler(func=lambda query: True)
def inline_query(query):
    try:
        chat_id = query.from_user.id
        user = user_dict[chat_id]
        num = 1
        user.num = num
        dbworker.set_state(str(chat_id), '2')
        if query.query == 'Кофе':
            r1 = types.InlineQueryResultArticle(
                id='1',
                thumb_url='https://2tea.pro/wp-content/uploads/2018/02/3-e1518513952423.jpg',
                title="Американо",
                description='Цена 70 ₽',
                input_message_content=types.InputTextMessageContent('Американо\n\nЦена 70 ₽'
                                                                    '[\xa0](https://2tea.pro/wp-content/uploads/2018/02/3-e1518513952423.jpg)',
                                                                    parse_mode="Markdown"),
                reply_markup=num_markup1()
            )
            r2 = types.InlineQueryResultArticle(
                id='2',
                thumb_url='http://faraon35.ru/uploads/эспрессо.jpeg',
                title="Эспрессо",
                description='Цена 80 ₽',
                input_message_content=types.InputTextMessageContent('Эспрессо\n\nЦена 80 ₽'
                                                                    '[\xa0](http://faraon35.ru/uploads/эспрессо.jpeg)',
                                                                    parse_mode="Markdown"),
                reply_markup=num_markup1()
            )
            bot.answer_inline_query(query.id, [r1, r2], cache_time=0)
        if query.query == 'изменить':
            with shelve.open('user_db.py') as db:
                r = []
                lst3 = list(db.keys())
                keys = list((filter(lambda x: str(query.from_user.id) in x, lst3)))
                for dd in keys:
                    a = list(db.get(dd))
                    default = a[3]
                    num = a[1]
                    markup = types.InlineKeyboardMarkup()
                    a1 = types.InlineKeyboardButton("-", callback_data=u'-1')
                    a2 = types.InlineKeyboardButton(str(num[3:-3]), callback_data='jr')
                    a3 = types.InlineKeyboardButton("+", callback_data=u'+1')
                    a4 = types.InlineKeyboardButton("⬅ Назад", switch_inline_query_current_chat="Кофе")
                    a5 = types.InlineKeyboardButton("🛒 Корзина", callback_data=u'корзина')
                    a6 = types.InlineKeyboardButton("☕ Добавки", callback_data=u'добавки')
                    a7 = types.InlineKeyboardButton("❌ Удалить позицию", callback_data=u'удалить позицию')
                    markup.add(a1, a2, a3)
                    markup.add(a4, a5)
                    markup.add(a6)
                    markup.add(a7)
                    input_content = types.InputTextMessageContent(message_text=f"{a[0]}\n\nЦена {a[2]}"
                                                                               f"[\xa0]({a[3]})", parse_mode='Markdown')
                    r2 = types.InlineQueryResultArticle(id=a[0],
                                                        thumb_url=default, title=a[0],
                                                        description=f'{(a[1])[3:-3]} шт.\n{a[2]} ₽',
                                                        input_message_content=input_content, reply_markup=markup)
                    r.append(r2)
                dbworker.set_state(str(chat_id), 'change')
                bot.answer_inline_query(query.id, r, cache_time=0, is_personal=True)
    except Exception as e:
        print(e)



@bot.message_handler(func=lambda message: dbworker.get_current_state(str(message.chat.id)) == 'change')
def msg_apps(message):
    try:
        chat_id = message.chat.id
        user = user_dict[chat_id]
        with shelve.open('user_db.py') as db:
            lst3 = list(db.keys())
            keys = list((filter(lambda x: str(message.from_user.id) in x, lst3)))
            for dd in keys:
                a = list(db.get(dd))
                if a[0] in message.text:
                    num = (a[1])[3:-3]
                    user.name_lot = a[0]
                    user.price = (float(a[2]))
                    user.num = int(num)
                    user.pic = a[3]
                else:
                    pass
        dbworker.set_state(str(chat_id), '1')
    except Exception as e:
        print(e)



@bot.message_handler(func=lambda message: dbworker.get_current_state(str(message.chat.id)) == '2')
def msg_apps(message):
    try:
        chat_id = message.chat.id
        user = user_dict[chat_id]
        if 'Американо' in message.text:
            user.pic = 'https://2tea.pro/wp-content/uploads/2018/02/3-e1518513952423.jpg'
            user.name_lot = 'Американо'
            user.price = 70.0
        if 'Эспрессо' in message.text:
            user.pic = 'http://faraon35.ru/uploads/эспрессо.jpeg'
            user.name_lot = 'Эспрессо'
            user.price = 80.0
        dbworker.set_state(str(chat_id), '1')
    except Exception as e:
        print(e)



@bot.message_handler(func=lambda message: True)
def handle_text(message):
    try:
        chat_id = message.chat.id
        user = user_dict[chat_id]
        if message.text == "☕ Каталог":
            bot.send_message(chat_id, 'Выберите категорию', reply_markup=catalog())
        if message.text == "🛒 Корзина":
            with shelve.open('user_db.py') as db:
                lst3 = list(db.keys())
                if list(filter(lambda y: str(chat_id) in y, lst3)) == []:
                    bot.send_message(chat_id, 'Ваша корзина пуста!', reply_markup=add_lot())
                else:
                    l = []
                    s = []
                    r = []
                    lst3 = list(db.keys())  # все клю4и из дб
                    lst = list((filter(lambda x: str(chat_id) in x, lst3)))  # нужный юзер
                    for dd in lst:
                        a = db.get(dd)
                        r.append(a)
                    for line3 in r:
                        line2 = ' '.join(line3[:3])
                        lin = line3[2]
                        s.append(float(lin))
                        l.append(line2)
                    total_price = sum(s)
                    m = ' ₽\n\n🔹 '.join(l)
                    user.total_price = total_price
                    bot.send_message(chat_id,
                                 text='Ваша корзина :\n\n'
                                      f'🔹 {m} ₽.\n\n'
                                      f'Итого: {str(total_price)}  ₽.',
                                 reply_markup=finish_markup())
    except Exception as e:
        print(e)


def gg_basket(callback):
    chat_id = callback.from_user.id
    user = user_dict[chat_id]
    with shelve.open('user_db.py') as db:
        db[str(chat_id) + ':' + user.name_lot] = [user.name_lot, '  |' + str(user.num) + '|  ', str(user.price * user.num), str(user.pic)]

def backbasket():
    markup = types.InlineKeyboardMarkup()
    a1 = types.InlineKeyboardButton(text='⬅ Назад в Корзину', callback_data=u'корзина')
    markup.add(a1)
    return markup

def finish_markup():
    markup = types.InlineKeyboardMarkup()
    a1 = types.InlineKeyboardButton("✔Ближайщее время", callback_data=u'Ближайщее время')
    a2 = types.InlineKeyboardButton("10 мин.", callback_data='10 мин.')
    a3 = types.InlineKeyboardButton("30 мин.", callback_data=u'30 мин.')
    a4 = types.InlineKeyboardButton("60 мин.", callback_data=u'60 мин.')
    a5 = types.InlineKeyboardButton("📝 Изменить", switch_inline_query_current_chat='изменить')
    a55 = types.InlineKeyboardButton("➕ Добавить", callback_data='добавить')
    a6 = types.InlineKeyboardButton("❎ Очистить", callback_data='очистить')
    a7 = types.InlineKeyboardButton("🏁 Оформить", callback_data='оформить')
    markup.add(a1)
    markup.add(a2, a3, a4)
    markup.add(a5, a55)
    markup.add(a6, a7)
    return markup

def add_lot():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("➕ Добавить", callback_data='добавить'))
    return markup

def time2(callback):
    if callback.data == 'Ближайщее время':
        markup = types.InlineKeyboardMarkup()
        a1 = types.InlineKeyboardButton("✔Ближайщее время", callback_data=u'Ближайщее время')
        a2 = types.InlineKeyboardButton("10 мин.", callback_data='10 мин.')
        a3 = types.InlineKeyboardButton("30 мин.", callback_data=u'30 мин.')
        a4 = types.InlineKeyboardButton("60 мин.", callback_data=u'60 мин.')
        a5 = types.InlineKeyboardButton("📝 Изменить", switch_inline_query_current_chat='изменить')
        a55 = types.InlineKeyboardButton("➕ Добавить", callback_data='добавить')
        a6 = types.InlineKeyboardButton("❎ Очистить", callback_data='очистить')
        a7 = types.InlineKeyboardButton("🏁 Оформить", callback_data='оформить')
        markup.add(a1)
        markup.add(a2, a3, a4)
        markup.add(a5, a55)
        markup.add(a6, a7)
        return markup
    elif callback.data == '10 мин.':
        markup = types.InlineKeyboardMarkup()
        a1 = types.InlineKeyboardButton("Ближайщее время", callback_data=u'Ближайщее время')
        a2 = types.InlineKeyboardButton("✔10 мин.", callback_data='10 мин.')
        a3 = types.InlineKeyboardButton("30 мин.", callback_data=u'30 мин.')
        a4 = types.InlineKeyboardButton("60 мин.", callback_data=u'60 мин.')
        a5 = types.InlineKeyboardButton("📝 Изменить", switch_inline_query_current_chat='изменить')
        a55 = types.InlineKeyboardButton("➕ Добавить", callback_data='добавить')
        a6 = types.InlineKeyboardButton("❎ Очистить", callback_data='очистить')
        a7 = types.InlineKeyboardButton("🏁 Оформить", callback_data='оформить')
        markup.add(a1)
        markup.add(a2, a3, a4)
        markup.add(a5, a55)
        markup.add(a6, a7)
        return markup
    elif callback.data == '30 мин.':
        markup = types.InlineKeyboardMarkup()
        a1 = types.InlineKeyboardButton("Ближайщее время", callback_data=u'Ближайщее время')
        a2 = types.InlineKeyboardButton("10 мин.", callback_data='10 мин.')
        a3 = types.InlineKeyboardButton("✔30 мин.", callback_data=u'30 мин.')
        a4 = types.InlineKeyboardButton("60 мин.", callback_data=u'60 мин.')
        a5 = types.InlineKeyboardButton("📝 Изменить", switch_inline_query_current_chat='изменить')
        a55 = types.InlineKeyboardButton("➕ Добавить", callback_data='добавить')
        a6 = types.InlineKeyboardButton("❎ Очистить", callback_data='очистить')
        a7 = types.InlineKeyboardButton("🏁 Оформить", callback_data='оформить')
        markup.add(a1)
        markup.add(a2, a3, a4)
        markup.add(a5, a55)
        markup.add(a6, a7)
        return markup
    elif callback.data == '60 мин.':
        markup = types.InlineKeyboardMarkup()
        a1 = types.InlineKeyboardButton("Ближайщее время", callback_data=u'Ближайщее время')
        a2 = types.InlineKeyboardButton("10 мин.", callback_data='10 мин.')
        a3 = types.InlineKeyboardButton("30 мин.", callback_data=u'30 мин.')
        a4 = types.InlineKeyboardButton("✔60 мин.", callback_data=u'60 мин.')
        a5 = types.InlineKeyboardButton("📝 Изменить", switch_inline_query_current_chat='изменить')
        a55 = types.InlineKeyboardButton("➕ Добавить", callback_data='добавить')
        a6 = types.InlineKeyboardButton("❎ Очистить", callback_data='очистить')
        a7 = types.InlineKeyboardButton("🏁 Оформить", callback_data='оформить')
        markup.add(a1)
        markup.add(a2, a3, a4)
        markup.add(a5, a55)
        markup.add(a6, a7)
        return markup


@bot.callback_query_handler(func=lambda callback: True)
def callback_inline(callback):
    try:
        if callback:
            chat_id = callback.from_user.id
            user = user_dict[chat_id]
            num = user.num
            if callback.data == '+1':
                num += 1
                markup = types.InlineKeyboardMarkup()
                a1 = types.InlineKeyboardButton("-", callback_data=u'-1')
                a2 = types.InlineKeyboardButton(str(num), callback_data='jr')
                a3 = types.InlineKeyboardButton("+", callback_data=u'+1')
                a4 = types.InlineKeyboardButton("⬅ Назад", switch_inline_query_current_chat="Кофе")
                a5 = types.InlineKeyboardButton("🛒 Корзина", callback_data=u'корзина')
                a6 = types.InlineKeyboardButton("☕ Добавки", callback_data=u'добавки')
                a7 = types.InlineKeyboardButton("❌ Удалить позицию", callback_data=u'удалить позицию')
                markup.add(a1, a2, a3)
                markup.add(a4, a5)
                markup.add(a6)
                markup.add(a7)
                bot.edit_message_reply_markup(inline_message_id=callback.inline_message_id, reply_markup=markup)
                user.num = num
            if callback.data == '-1':
                num -= 1
                if num < 1:
                    num = 1
                markup = types.InlineKeyboardMarkup()
                a1 = types.InlineKeyboardButton("-", callback_data=u'-1')
                a2 = types.InlineKeyboardButton(str(num), callback_data='jr')
                a3 = types.InlineKeyboardButton("+", callback_data=u'+1')
                a4 = types.InlineKeyboardButton("⬅ Назад", switch_inline_query_current_chat="Кофе")
                a5 = types.InlineKeyboardButton("🛒 Корзина", callback_data=u'корзина')
                a6 = types.InlineKeyboardButton("☕ Добавки", callback_data=u'добавки')
                a7 = types.InlineKeyboardButton("❌ Удалить позицию", callback_data=u'удалить позицию')
                markup.add(a1, a2, a3)
                markup.add(a4, a5)
                markup.add(a6)
                markup.add(a7)
                bot.edit_message_reply_markup(inline_message_id=callback.inline_message_id, reply_markup=markup)
                user.num = num
            if callback.data == "корзина":
                gg_basket(callback)
                with shelve.open('user_db.py') as db:
                    l = []
                    s = []
                    r = []
                    lst3 = list(db.keys()) #все клю4и из дб
                    lst = list((filter(lambda x: str(chat_id) in x, lst3))) #нужный юзер
                    for dd in lst:
                        a = db.get(dd)
                        r.append(a)
                    for line3 in r:
                        line2 = ' '.join(line3[:3])
                        lin = line3[2]
                        s.append(float(lin))
                        l.append(line2)
                    total_price = sum(s)
                    m = ' ₽\n\n🔹 '.join(l)
                    user.total_price = total_price
                bot.edit_message_text(inline_message_id=callback.inline_message_id, text='Вы перешли в корзину')
                bot.send_message(chat_id,
                                 text='Ваша корзина :\n\n'
                                            f'🔹 {m} ₽.\n\n'
                                            f'Итого: {str(total_price)}  ₽.',
                                      reply_markup=finish_markup())
            if callback.data == 'удалить позицию':
                bot.edit_message_text(inline_message_id=callback.inline_message_id, text='Позиция удалена')
                check_basket(chat_id, callback)
                with shelve.open('user_db.py') as db:
                    del db[str(chat_id) + ':' + user.name_lot]
            if callback.data == 'очистить':
                with shelve.open('user_db.py') as db:
                    lst3 = list(db.keys())
                    lst = list((filter(lambda x: str(chat_id) in x, lst3)))
                    for dd in lst:
                        del db[dd]
                bot.edit_message_text(chat_id=chat_id, message_id=callback.message.message_id,
                                      text='Ваша корзина очищена!', reply_markup=add_lot())
            if callback.data == 'добавить':
                bot.edit_message_text(chat_id=chat_id, message_id=callback.message.message_id,
                                      text='Выберите категорию', reply_markup=catalog())
            if callback.data == 'выполнение':
                bot.send_message(-1001302729558, f'Заказ номер: #{user.number_ship}\n\n')
                bot.answer_callback_query(callback.id, "Ваш заказ в процессе приготовления!")
            if callback.data == 'добавки':
                bot.edit_message_text(inline_message_id=callback.inline_message_id,
                                          text='Добавки для напитков..\n(Можно выбрать один вариант)',
                                          reply_markup=dobavki())
            if callback.data == 'назад_инлайн':
                markup = num_markup2(callback, num)
                bot.edit_message_text(inline_message_id=callback.inline_message_id,
                                      text=f"{user.name_lot}\n\nЦена {user.price}"
                                            f"[\xa0]({user.pic})", parse_mode='Markdown', reply_markup=markup)
            if callback.data == 'оформить':
                with shelve.open('user_db.py') as db:
                    r = []
                    lst3 = list(db.keys()) #все клю4и из дб
                    lst = list((filter(lambda x: str(chat_id) in x, lst3))) #нужный юзер
                    for dd in lst:
                        a = list(db.get(dd))
                        r.append(f'- {a[0]} {(a[1])[3:-3]} шт.')
                    m = '\n'.join(r)
                price = str(user.total_price)
                price1 = user.total_price * 100
                prices = [LabeledPrice(label=f'Стоимость услуги: ', amount=int(price1))]
                user.number_ship = str(random_pool())
                title = f'Заказ: {user.number_ship}'
                if price1 > 6569.0:
                    bot.send_invoice(callback.from_user.id, provider_token='381764678:TEST:5508',
                                     start_parameter='true',
                                     title=title,
                                     description=f'\n{m}',
                                     invoice_payload='test',
                                     currency='RUB',
                                     prices=prices,
                                     need_phone_number=True,
                                     photo_url='http://www.tobystevens.co.uk/wp-content/uploads/2012/04/7.-SAMSUNG_COFFEE_CAFE_LOGO_GRAPHIC.jpg',
                                     photo_height=512,
                                     photo_width=512,
                                     photo_size=512,
                                     )
                else:
                    bot.edit_message_text(chat_id=callback.from_user.id, message_id=callback.message.message_id,
                                          text='К сожалению, Telegram обслуживает платежи не менее 1$\n'
                                               f'Сумма вашего заказа: {price} ₽\n'
                                               f'Добавьте в корзину позиции..',
                                          reply_markup=add_lot())
            if "Ближайщее время" or 'мин.' in callback.data:
                markup = time2(callback)
                user.time = callback.data
                bot.edit_message_reply_markup(callback.from_user.id, callback.message.message_id, reply_markup=markup)
    except Exception as e:
        print(e)


@bot.shipping_query_handler(func=lambda query: True)
def shipping(shipping_query):
    bot.answer_shipping_query(shipping_query.id, ok=True, shipping_options=False,
                              error_message='Oh, што-то пошло не так. Попробуйте повторить позже!')

@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True,
                                  error_message="Проблемы с картой"
                                                " повторите платеж позже.")


def common():
    markup = types.InlineKeyboardMarkup()
    a1 = types.InlineKeyboardButton("Начать выполнение ", callback_data=u'выполнение')
    markup.add(a1)
    return markup

@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    chat_id = message.chat.id
    user = user_dict[chat_id]
    with shelve.open('user_db.py') as db:
        l = []
        r = []
        lst3 = list(db.keys())
        lst = list((filter(lambda x: str(chat_id) in x, lst3))) #фильтр на юзера
        for dd in lst:
            a = db.get(dd)
            r.append(a)
        for line3 in r:
            line2 = ' '.join(line3[:3])
            l.append(line2)
        m = '₽\n\n➕ '.join(l)
    from_chat_id = -1001302729558
    now = datetime.now()
    today = datetime.today().strftime('%H:%M')
    time_order = f"{now.year}-{now.month}-{now.day}  {today}"
    type_pay = 'Банк. карта'
    name = f'{message.from_user.first_name} {message.from_user.last_name} @{message.from_user.username}'
    bot.send_message(message.from_user.id, f'Супер! Теперь ваш заказ отправлен..\n\n➕ {m} ₽\n\nНомер вашего заказа - {user.number_ship}',
                     reply_markup=common())
    bot.send_message(from_chat_id, f'➕ {m} ₽\n'
                                   f'___________________________\n\n'
                                   f'Номер заказа - #{user.number_ship}\n'
                                   f'Время заказа: {time_order}\n'
                                   f'Заказчик: {name}\n'
                                   f'Тип оплаты: {type_pay}\n\n'
                                   f'Итого: {str(user.total_price)} ₽.'
                     )

    with shelve.open('user_db.py') as db:
        lst3 = list(db.keys())
        lst = list((filter(lambda x: str(chat_id) in x, lst3)))
        for dd in lst:
            del db[dd]


def random_pool():
    a = random.randint(999, 9999)
    return a




@server.route('/' + TOKEN, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200


@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://cofe-testbot-1996.herokuapp.com/' + TOKEN)
    return "!", 200


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
