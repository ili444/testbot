import telebot
import os 
import shelve
import datetime
from datetime import datetime
import random
from telebot.types import LabeledPrice
from telebot import types
import urllib.request as urllib2
from flask import Flask, request
TOKEN = os.environ['token']
bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)
user_dict = {}

class User:
    def __init__(self, start):
        self.start = start
        self.num = None
        self.name_lot = None
        self.price = None

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
    a5 = types.InlineKeyboardButton("🛒 Корзина", callback_data='корзина')
    markup.add(a1, a2, a3)
    markup.add(a4, a5)
    return markup


@bot.message_handler(commands=['start', 'reset'])
def callback_inline(message):
    user_markup1 = telebot.types.ReplyKeyboardMarkup(True, True)
    user_markup1.row('☕ Каталог', '🛒 Корзина')
    user_markup1.row('📌 Акции', '📲 Обратная связь')
    name = message.from_user.first_name
    bot.send_message(message.chat.id, f'Приветствую, {name}! Я Кофе-бот!\n\nУ нас ты можешь заказать кофе!',
                     reply_markup=user_markup1)
    bot.send_message(message.from_user.id, 'Выбери категорию:',
                         reply_markup=catalog())


@bot.inline_handler(func=lambda query: True)
def inline_query(query):
    try:
        if query.query == 'Кофе':
            r1 = types.InlineQueryResultArticle(
                id='1',
                thumb_url='https://foodsoul.pro/uploads/ru/chains/1096/images/branches/1365/items/large/11683e07a82db0d0b430645ae5419e15.jpg',
                title="Американо",
                description='Цена 70 ₽',
                input_message_content=types.InputTextMessageContent(message_text="Американо"),
            )
            r2 = types.InlineQueryResultArticle(
                id='2',
                thumb_url='https://foodsoul.pro/uploads/ru/chains/1096/images/branches/1365/items/large/11683e07a82db0d0b430645ae5419e15.jpg',
                title="Эспрессо",
                description='Цена 80 ₽',
                input_message_content=types.InputTextMessageContent(message_text="Эспрессо")
            )
            bot.answer_inline_query(query.id, [r1], [r2])
    except Exception as e:
        print(e)




@bot.message_handler(func=lambda message: True)
def handle_text(message):
    try:
        chat_id = message.chat.id
        start = 'ok'
        user = User(start)
        user_dict[chat_id] = user
        num = 1
        user.num = num
        if message.text == 'Американо':
            url = 'https://foodsoul.pro/uploads/ru/chains/1096/images/branches/1365/items/large/11683e07a82db0d0b430645ae5419e15.jpg'
            urllib2.urlretrieve(url, 'url_image.jpg')
            img = open('url_image.jpg', 'rb')
            user.name_lot = 'Американо'
            user.price = 70
            bot.send_photo(message.from_user.id, img, caption='Американо\n\nЦена 70 ₽', reply_markup=num_markup1())
            img.close()
        if message.text == 'Эспрессо':
            url = 'https://foodsoul.pro/uploads/ru/chains/1096/images/branches/1365/items/large/11683e07a82db0d0b430645ae5419e15.jpg'
            urllib2.urlretrieve(url, 'url_image2.jpg')
            img = open('url_image2.jpg', 'rb')
            user.name_lot = 'Эспрессо'
            user.price = 80
            bot.send_photo(message.from_user.id, img, caption='Эспрессо\n\nЦена 80 ₽', reply_markup=num_markup1())
            img.close()
    except Exception as e:
        print(e)


def gg_basket(callback):
    chat_id = callback.from_user.id
    user = user_dict[chat_id]
    with shelve.open('user_db.py') as db:
        db[str(chat_id) + ':' + user.name_lot] = [user.name_lot, '  |' + str(user.num) + '|  ', str(user.price * user.num)]

def backbasket():
    markup = types.InlineKeyboardMarkup()
    a1 = types.InlineKeyboardButton(text='⬅ Назад в Корзину', callback_data=u'Корзина')
    markup.add(a1)
    return markup

def finish_markup():
    markup = types.InlineKeyboardMarkup()
    a1 = types.InlineKeyboardButton("Ближайщее время", callback_data=u'Ближайщее время')
    a2 = types.InlineKeyboardButton("10 мин.", callback_data='10 мин.')
    a3 = types.InlineKeyboardButton("30 мин.", callback_data=u'30 мин.')
    a4 = types.InlineKeyboardButton("60 мин.", callback_data=u'60 мин.')
    a5 = types.InlineKeyboardButton("📝 Изменить", callback_data='изменить')
    a6 = types.InlineKeyboardButton("❎ Очистить", callback_data='очистить')
    a7 = types.InlineKeyboardButton("🏁 Оформить", callback_data='оформить')
    markup.add(a1)
    markup.add(a2, a3, a4)
    markup.add(a5)
    markup.add(a6, a7)
    return markup

def add_lot():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("➕ Добавить файл", callback_data='добавить'))
    return markup

def time2(callback):
    if callback.data == 'Ближайщее время':
        markup = types.InlineKeyboardMarkup()
        a1 = types.InlineKeyboardButton("✔Ближайщее время", callback_data=u'Ближайщее время')
        a2 = types.InlineKeyboardButton("10 мин.", callback_data='10 мин.')
        a3 = types.InlineKeyboardButton("30 мин.", callback_data=u'30 мин.')
        a4 = types.InlineKeyboardButton("60 мин.", callback_data=u'60 мин.')
        a5 = types.InlineKeyboardButton("📝 Изменить", callback_data='изменить')
        a6 = types.InlineKeyboardButton("❎ Очистить", callback_data='очистить')
        a7 = types.InlineKeyboardButton("🏁 Оформить", callback_data='оформить')
        markup.add(a1)
        markup.add(a2, a3, a4)
        markup.add(a5)
        markup.add(a6, a7)
        return markup
    elif callback.data == '10 мин.':
        markup = types.InlineKeyboardMarkup()
        a1 = types.InlineKeyboardButton("Ближайщее время", callback_data=u'Ближайщее время')
        a2 = types.InlineKeyboardButton("✔10 мин.", callback_data='10 мин.')
        a3 = types.InlineKeyboardButton("30 мин.", callback_data=u'30 мин.')
        a4 = types.InlineKeyboardButton("60 мин.", callback_data=u'60 мин.')
        a5 = types.InlineKeyboardButton("📝 Изменить", callback_data='изменить')
        a6 = types.InlineKeyboardButton("❎ Очистить", callback_data='очистить')
        a7 = types.InlineKeyboardButton("🏁 Оформить", callback_data='оформить')
        markup.add(a1)
        markup.add(a2, a3, a4)
        markup.add(a5)
        markup.add(a6, a7)
        return markup
    elif callback.data == '30 мин.':
        markup = types.InlineKeyboardMarkup()
        a1 = types.InlineKeyboardButton("Ближайщее время", callback_data=u'Ближайщее время')
        a2 = types.InlineKeyboardButton("10 мин.", callback_data='10 мин.')
        a3 = types.InlineKeyboardButton("✔30 мин.", callback_data=u'30 мин.')
        a4 = types.InlineKeyboardButton("60 мин.", callback_data=u'60 мин.')
        a5 = types.InlineKeyboardButton("📝 Изменить", callback_data='изменить')
        a6 = types.InlineKeyboardButton("❎ Очистить", callback_data='очистить')
        a7 = types.InlineKeyboardButton("🏁 Оформить", callback_data='оформить')
        markup.add(a1)
        markup.add(a2, a3, a4)
        markup.add(a5)
        markup.add(a6, a7)
        return markup
    elif callback.data == '60 мин.':
        markup = types.InlineKeyboardMarkup()
        a1 = types.InlineKeyboardButton("Ближайщее время", callback_data=u'Ближайщее время')
        a2 = types.InlineKeyboardButton("10 мин.", callback_data='10 мин.')
        a3 = types.InlineKeyboardButton("30 мин.", callback_data=u'30 мин.')
        a4 = types.InlineKeyboardButton("✔60 мин.", callback_data=u'60 мин.')
        a5 = types.InlineKeyboardButton("📝 Изменить", callback_data='изменить')
        a6 = types.InlineKeyboardButton("❎ Очистить", callback_data='очистить')
        a7 = types.InlineKeyboardButton("🏁 Оформить", callback_data='оформить')
        markup.add(a1)
        markup.add(a2, a3, a4)
        markup.add(a5)
        markup.add(a6, a7)
        return markup


@bot.callback_query_handler(func=lambda callback: True)
def callback_inline(callback):
        if callback.message:
            chat_id = callback.from_user.id
            user = user_dict[chat_id]
            num = user.num
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
            if callback.data == 'оформить':
                bot.edit_message_text(chat_id=chat_id, message_id=callback.message.message_id,
                                      text='Оформление заказа', reply_markup=backbasket())
                #bot.answer_callback_query(callback.id, "Вы выбрали - Cейчас в Telegram")
                price = str(user.total_price)
                price1 = user.total_price * 100
                prices = [LabeledPrice(label=f'Стоимость услуги: ', amount=int(price1))]
                title = 'Заказ'
                if price1 > 6569.0:
                    bot.send_invoice(callback.from_user.id, provider_token='381764678:TEST:7231',
                                     start_parameter='true',
                                     title=title,
                                     description=f'Тип услуги: {title}\nЦена {price} ₽',
                                     invoice_payload='test',
                                     currency='RUB',
                                     prices=prices,
                                     need_phone_number=True,
                                     photo_url='https://pp.userapi.com/c845218/v845218058/cd929/DMHxsJvNO6s.jpg',
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
            if callback.data == '+1':
                num += 1
                markup = types.InlineKeyboardMarkup()
                a1 = types.InlineKeyboardButton("-", callback_data=u'-1')
                a2 = types.InlineKeyboardButton(str(num), callback_data='jr')
                a3 = types.InlineKeyboardButton("+", callback_data=u'+1')
                a4 = types.InlineKeyboardButton("⬅ Назад", switch_inline_query_current_chat="Кофе")
                a5 = types.InlineKeyboardButton("🛒 Корзина", callback_data=u'корзина')
                markup.add(a1, a2, a3)
                markup.add(a4, a5)
                bot.edit_message_reply_markup(callback.from_user.id, callback.message.message_id, reply_markup=markup)
                user.num = num
            if callback.data == '-1':
                num -= 1
                markup = types.InlineKeyboardMarkup()
                a1 = types.InlineKeyboardButton("-", callback_data=u'-1')
                a2 = types.InlineKeyboardButton(str(num), callback_data='jr')
                a3 = types.InlineKeyboardButton("+", callback_data=u'+1')
                a4 = types.InlineKeyboardButton("⬅ Назад", switch_inline_query_current_chat="Кофе")
                a5 = types.InlineKeyboardButton("🛒 Корзина", callback_data=u'корзина')
                markup.add(a1, a2, a3)
                markup.add(a4, a5)
                bot.edit_message_reply_markup(callback.from_user.id, callback.message.message_id, reply_markup=markup)
                user.num = num
            if callback.data == "Корзина":
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
                        line2 = ' '.join(line3)
                        lin = line3[2]
                        s.append(float(lin))
                        l.append(line2)
                    total_price = sum(s)
                    m = ' ₽\n\n🔹 '.join(l)
                    user.total_price = total_price
                bot.edit_message_text(chat_id=chat_id, message_id=callback.message.message_id,
                                      text='Ваша корзина :\n\n'
                                            f'🔹 {m} ₽.\n\n'
                                            f'Итого: {str(total_price)}  ₽.',
                                      reply_markup=finish_markup())



@bot.shipping_query_handler(func=lambda query: True)
def shipping(shipping_query):
    print(shipping_query)
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
    number = str(random_pool())
    bot.send_message(message.from_user.id, 'Супер! Теперь ваш заказ отправлен..\nНомер вашего заказа - ' + number, reply_markup=common())
    with shelve.open('user_db.py') as db:
        l = []
        r = []
        lst3 = list(db.keys())
        lst = list((filter(lambda x: str(chat_id) in x, lst3))) #фильтр на юзера
        for dd in lst:
            a = db.get(dd)
            r.append(a)
        for line3 in r:
            line2 = ' '.join(line3)
            l.append(line2)
        m = '\n'.join(l)
    from_chat_id = -1001302729558
    now = datetime.now()
    hours = int(now.hour) + 7
    time_order = str(f"{now.year}-{now.month}-{now.day}  {str(hours)}:{now.minute}")
    type_pay = 'Наличные'
    name = message.from_user.first_name + ' ' + message.from_user.last_name + ' @' + message.from_user.username
    bot.send_message(from_chat_id, f'{m}'
                                   f'___________________________\n\n'
                                   f'Номер заказа - {number}\n'
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
    bot.set_webhook(url='https://flask-est-1996.herokuapp.com/' + TOKEN)
    return "!", 200


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
