# -*- coding: utf-8 -*-
# coding: utf-8
import dbworker, telebot, shelve, random, datetime, urllib, os
from kanc import dict2, dict_price
from telebot.types import LabeledPrice
from telebot import types
from datetime import datetime
import urllib.request as urllib2
from urllib.parse import urlparse
from PyPDF2 import PdfFileReader
import os.path
import xlrd
import pandas as pd
from docx import Document
import zipfile
from pptx import Presentation
from bs4 import BeautifulSoup
from flask import Flask, request

TOKEN = os.environ['token']
bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

user_dict = {}


class User:
    def __init__(self, start):
        self.start = start
        self.type_print = None
        self.num = None
        self.link = None
        self.file_id = None
        self.file_name = None
        self.apps = None
        self.num_page = None
        self.total_price = None
        self.price_print = None
        self.info_user = None
        self.message_id = None


class Markup():
    def __init__(self, start_func):
        self.start_func = start_func


    def inline_markup(self):
        markup = types.InlineKeyboardMarkup()
        markup.row_width = 1
        markup.add(types.InlineKeyboardButton("Ч/Б Печать(распечатка)", callback_data='Ч/Б Печать(распечатка)'),
                   types.InlineKeyboardButton("Цветная Печать А4", callback_data='Цветная печать А4'),
                   types.InlineKeyboardButton("Печать фото 10х15", callback_data='Печать фото 10х15'),
                   types.InlineKeyboardButton('А4 Ч/Б двусторонняя', callback_data='А4 Ч/Б двусторонняя'),
                    types.InlineKeyboardButton("Печать на фотобумаге А4 (глянец, матовая)", callback_data='Печать на фотобумаге')
                   )
        return markup


    def inline_markup2(self):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("➕ Добавить файл", callback_data='добавить'))
        return markup


    def num_copy_markup1(self):
        markup = types.InlineKeyboardMarkup()
        a1 = types.InlineKeyboardButton("-", callback_data=u'-1')
        a2 = types.InlineKeyboardButton('1', callback_data='jr')
        a3 = types.InlineKeyboardButton("+", callback_data=u'+1')
        a4 = types.InlineKeyboardButton("⬅ Назад", callback_data=u'назад1')
        a5 = types.InlineKeyboardButton("🛒 Корзина", callback_data=u'корзина')
        a6 = types.InlineKeyboardButton("📝 Примечания", callback_data=u'примечания')
        a7 = types.InlineKeyboardButton("❌ Удалить позицию", callback_data=u'удалить позицию')
        markup.add(a1, a2, a3)
        markup.add(a4, a5)
        markup.add(a6)
        markup.add(a7)
        return markup

    def num_copy_markup3(self):
        markup = types.InlineKeyboardMarkup()
        a1 = types.InlineKeyboardButton("-", callback_data=u'-1')
        a2 = types.InlineKeyboardButton('1', callback_data='jr')
        a3 = types.InlineKeyboardButton("+", callback_data=u'+1')
        a4 = types.InlineKeyboardButton("⬅ Назад", callback_data='НазадВканц')
        a5 = types.InlineKeyboardButton("🛒 Корзина", callback_data='корзина')
        a6 = types.InlineKeyboardButton("📝 Примечания", callback_data=u'примечания')
        a7 = types.InlineKeyboardButton("❌ Удалить позицию", callback_data=u'удалить позицию')
        markup.add(a1, a2, a3)
        markup.add(a4, a5)
        markup.add(a6)
        markup.add(a7)
        return markup


    def num_copy_markup2(self, callback, num):
        markup = types.InlineKeyboardMarkup()
        a1 = types.InlineKeyboardButton("-", callback_data=u'-1')
        a2 = types.InlineKeyboardButton(str(num), callback_data='jr')
        a3 = types.InlineKeyboardButton("+", callback_data=u'+1')
        a4 = types.InlineKeyboardButton("⬅ Назад", callback_data=u'назад1')
        a5 = types.InlineKeyboardButton("🛒 Корзина", callback_data=u'корзина')
        a6 = types.InlineKeyboardButton("📝 Примечания", callback_data=u'примечания')
        a7 = types.InlineKeyboardButton("❌ Удалить позицию", callback_data=u'удалить позицию')
        markup.add(a1, a2, a3)
        markup.add(a4, a5)
        markup.add(a6)
        markup.add(a7)
        return markup

    def clear_basket(self, chat_id):
        with shelve.open('itog.py') as db:
            lst3 = list(db.keys())
            lst = list((filter(lambda x: str(chat_id) in x, lst3)))
            for dd in lst:
                del db[dd]


    def gen_markup1(self, chat_id, total_price):
        markup = types.InlineKeyboardMarkup(True)
        #a1 = types.InlineKeyboardButton("Cейчас в Telegram", callback_data='now')
        a2 = types.InlineKeyboardButton("Оплатa при получении", callback_data='later')
        a3 = types.InlineKeyboardButton("Перевод Яндекс.Деньги", url=f'https://money.yandex.ru/transfer?receiver=410014990574641&sum={total_price}&success'
                                        f'URL=&quickpay-back-url=https://t.me/copykotbot&shop-host=&label={chat_id}&'
                                        'targets=Копир-коту&comment=&origin=form&selectedPaymentType=pc&destination='
                                        'Donate&form-comment=Donate&short-dest=&quickpay-form=shop')
        a4 = types.InlineKeyboardButton("⬅ Назад", callback_data='корзина')
        markup.add(a2)
        markup.add(a3)
        markup.add(a4)
        return markup


    def go_basket(self):
        markup = types.InlineKeyboardMarkup(True)
        markup.add(types.InlineKeyboardButton("🛒 В корзину", callback_data='корзина'),
                   types.InlineKeyboardButton("🔃 Изменить примечание ", callback_data='примечания'),
                   types.InlineKeyboardButton("⬅ Назад", callback_data='назад')
                   )
        return markup


    def back(self):
        markup = types.InlineKeyboardMarkup(True)
        markup.add(types.InlineKeyboardButton("⬅ Назад", callback_data='назад')
                   )
        return markup

    def gen_markup2(self):
        markup = types.InlineKeyboardMarkup(True)
        markup.row_width = 2
        markup.add(types.InlineKeyboardButton("🏁 Оформить", callback_data='оформить'),
                   types.InlineKeyboardButton("➕ Добавить", callback_data='добавить'),
                   types.InlineKeyboardButton("❎ Очистить", callback_data='очистить'),
                   types.InlineKeyboardButton("🔃 Изменить", switch_inline_query_current_chat='Изменить')
                   )
        return markup

    def kancel(self):
        markup = types.InlineKeyboardMarkup(True)
        markup.row_width = 2
        markup.add(types.InlineKeyboardButton("✏ Ручки/Карандаши", switch_inline_query_current_chat='Ручки/Карандаши'),
                   types.InlineKeyboardButton("📁 Папки и Файлы", switch_inline_query_current_chat='Папки и Файлы'),
                   types.InlineKeyboardButton("🗒 Корректирующие средства", switch_inline_query_current_chat='Корректирующие средства')
                   )
        return markup

    def klava(self, query, num):
        markup = types.InlineKeyboardMarkup()
        a1 = types.InlineKeyboardButton("-", callback_data=u'-1')
        a2 = types.InlineKeyboardButton(str(num), callback_data='jr')
        a3 = types.InlineKeyboardButton("+", callback_data=u'+1')
        a4 = types.InlineKeyboardButton("⬅ Назад", callback_data=u'назад1')
        a5 = types.InlineKeyboardButton("🛒 Корзина", callback_data=u'корзина')
        a6 = types.InlineKeyboardButton("📝 Примечания", callback_data=u'примечания')
        a7 = types.InlineKeyboardButton("❌ Удалить позицию", callback_data=u'удалить позицию')
        markup.add(a1, a2, a3)
        markup.add(a4, a5)
        markup.add(a6)
        markup.add(a7)
        return markup

    def random_pool(self):
        a = random.randint(999, 9999)
        return a


    def check_basket(self, chat_id, callback):
        chat_id = callback.from_user.id
        user = user_dict[chat_id]
        with shelve.open('itog.py') as db:
            lst3 = list(db.keys())
            if list(filter(lambda y: str(chat_id) in y, lst3)) == []:
                bot.send_message(chat_id, 'Ваша корзина пуста!', reply_markup=mark_up.inline_markup2())
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
                    line2 = ' '.join(line3[:5])
                    lin = line3[4]
                    s.append(float(lin))
                    l.append(line2)
                total_price = sum(s)
                m = ' ₽\n\n💾 '.join(l)
                user.total_price = total_price
                bot.send_message(chat_id, 'Ваша корзина :\n\n'
                                          f'💾 {m} ₽.\n\n'
                                          f'Итого: {str(total_price)}  ₽.', reply_markup=mark_up.gen_markup2())

    def result_ship(self, chat_id, int):
        with shelve.open('itog.py') as db:
            l = []
            r = []
            t = []
            lst3 = list(db.keys())
            lst = list((filter(lambda x: str(chat_id) in x, lst3)))  # фильтр на юзера
            for dd in lst:
                a = db.get(dd)
                r.append(a)
            for line3 in r:
                line1 = ' '.join(line3[:5])
                line2 = ' '.join(line3)
                l.append(line2)
                t.append(line1)
            m = '\n'.join(l)
            j = ' ₽\n\n💾 '.join(t)
            if int == 1:
                return j
            else:
                return m



    def gg_basket(self, callback):
        chat_id = callback.from_user.id
        user = user_dict[chat_id]
        with shelve.open('itog.py') as db:
            db[str(chat_id) + ':' + user.file_name] = [user.file_name, f' ({user.type_print}) ',
                                                       (str(user.num) + ' экз.'),
                                                       (str(user.num_page) + ' стр.'),
                                                       (str(user.num_page * user.num * user.price_print)),
                                                       ('\n\n' + str(user.link) + '\n\n'),
                                                       ('Прим.\n' + str(user.apps) + '\n\n')]

    def add_kancel(self, callback):
        chat_id = callback.from_user.id
        user = user_dict[chat_id]
        with shelve.open('itog.py') as db:
            db[str(chat_id) + ':' + user.file_name] = [user.file_name, f'{user.type_print}', (str(user.num) + ' экз.'),
                                                       ' - ',
                                                       (str(user.num * user.price_print)),
                                                       ('\n\n' + str(user.link) + '\n\n'),
                                                       ('Прим.\n' + str(user.apps) + '\n\n')]

    def callduty(self, price_print, callback):
        chat_id = callback.from_user.id
        user = user_dict[chat_id]
        type_print = callback.data
        user.price_print = price_print
        user.type_print = type_print

    def inline_plus(self, callback, num):
        markup = types.InlineKeyboardMarkup()
        a1 = types.InlineKeyboardButton("-", callback_data=u'-1')
        a2 = types.InlineKeyboardButton(str(num), callback_data='jr')
        a3 = types.InlineKeyboardButton("+", callback_data=u'+1')
        a4 = types.InlineKeyboardButton("⬅ Назад", callback_data=u'назад1')
        a5 = types.InlineKeyboardButton("🛒 Корзина", callback_data=u'корзина')
        a6 = types.InlineKeyboardButton("📝 Примечания", callback_data=u'примечания')
        a7 = types.InlineKeyboardButton("❌ Удалить позицию", callback_data=u'удалить позицию')
        markup.add(a1, a2, a3)
        markup.add(a4, a5)
        markup.add(a6)
        markup.add(a7)
        return markup

    def inline_plus_kanc(self, callback, num):
        markup = types.InlineKeyboardMarkup()
        a1 = types.InlineKeyboardButton("-", callback_data=u'-1')
        a2 = types.InlineKeyboardButton(str(num), callback_data='jr')
        a3 = types.InlineKeyboardButton("+", callback_data=u'+1')
        a4 = types.InlineKeyboardButton("⬅ Назад", callback_data='НазадВканц')
        a5 = types.InlineKeyboardButton("🛒 Корзина", callback_data='корзина')
        a6 = types.InlineKeyboardButton("📝 Примечания", callback_data=u'примечания')
        a7 = types.InlineKeyboardButton("❌ Удалить позицию", callback_data=u'удалить позицию')
        markup.add(a1, a2, a3)
        markup.add(a4, a5)
        markup.add(a6)
        markup.add(a7)
        return markup

    def plus(self, callback, num):
        markup = types.InlineKeyboardMarkup()
        a1 = types.InlineKeyboardButton("-", callback_data=u'-1')
        a2 = types.InlineKeyboardButton(str(num), callback_data='jr')
        a3 = types.InlineKeyboardButton("+", callback_data=u'+1')
        a4 = types.InlineKeyboardButton("⬅ Назад", callback_data=u'назад1')
        a5 = types.InlineKeyboardButton("🛒 Корзина", callback_data=u'корзина')
        a6 = types.InlineKeyboardButton("📝 Примечания", callback_data=u'примечания')
        markup.add(a1, a2, a3)
        markup.add(a4, a5)
        markup.add(a6)
        return markup

    def plus_kanc(self, callback, num):
        markup = types.InlineKeyboardMarkup()
        a1 = types.InlineKeyboardButton("-", callback_data=u'-1')
        a2 = types.InlineKeyboardButton(str(num), callback_data='jr')
        a3 = types.InlineKeyboardButton("+", callback_data=u'+1')
        a4 = types.InlineKeyboardButton("⬅ Назад", callback_data='НазадВканц')
        a5 = types.InlineKeyboardButton("🛒 Корзина", callback_data='корзина')
        a6 = types.InlineKeyboardButton("📝 Примечания", callback_data=u'примечания')
        markup.add(a1, a2, a3)
        markup.add(a4, a5)
        markup.add(a6)
        return markup

    def add_knopka(self, id, thumb_url, title, price):
        r1 = types.InlineQueryResultArticle(
            id=id,
            thumb_url=thumb_url,
            title=title,
            description=f'Цена {price} ₽',
            input_message_content=types.InputTextMessageContent(message_text=f"{title}\n\nЦена {price} ₽"
                                                                             f"[\xa0]({thumb_url})"
                                                                , parse_mode='Markdown'),
            reply_markup=mark_up.num_copy_markup3()
        )
        return r1

    def kanc_finish(self, atr):
        r = []
        n_keys = dict2[atr].keys()
        for key1 in n_keys:
            a = dict2[atr].get(key1)
            d = mark_up.add_knopka(
                a['id'], a['thumb_url'], a['title'], a['price']
            )
            r.append(d)
        return r
    
    def finish_payments(self, chat_id, user):
        number = str(mark_up.random_pool())
        j = mark_up.result_ship(chat_id, 1)
        m = mark_up.result_ship(chat_id, 0)
        from_chat_id = -1001302729558
        now = datetime.now()
        hours = int(now.hour) + 7
        time_order = str(f"{now.year}-{now.month}-{now.day}  {str(hours)}:{now.minute}")
        type_pay = 'Перевод Яндекс.Деньги'
        name = user.info_user
        bot.edit_message_text(chat_id=chat_id, message_id=user.message_id,
                          text=f'Супер! Платёж на сумму {str(user.total_price)} получен!✔\nТеперь ваш заказ отправлен Копир-кот!✔\n'
                           f'\n💾 {j} ₽\n\nЗабрать заказ можете в любое рабочее время по адресу: Проспект Мира 80а, Красноярск (ТЦ АВЕНЮ, 4 этаж)\n\n'
                           f'Номер вашего заказа - {number}', reply_markup=mark_up.forward())
        bot.send_message(from_chat_id, f'{m}'
                                   f'___________________________\n\n'
                                   f'Номер заказа - {number}\n'
                                   f'Время заказа: {time_order}\n'
                                   f'Заказчик: {name}\n'
                                   f'Тип оплаты: {type_pay}\n\n'
                                   f'Итого: {str(user.total_price)} ₽.'
                     )
        mark_up.clear_basket(chat_id)
        
    def pechat(self, a, price_print, callback):
                chat_id = callback.from_user.id
                user = user_dict[chat_id]
                mark_up.callduty(price_print, callback)
                num = user.num
                print(num)
                if num != 1:
                    markup = mark_up.num_copy_markup2(callback, num)
                else:
                    markup = mark_up.num_copy_markup1()
                if callback.inline_message_id == None:
                    bot.edit_message_text(chat_id=callback.from_user.id, message_id=callback.message.message_id,
                                      text=f'📌 {a} - {str(price_print)} руб/стр.\n\n'
                                      'Выберите кол-во копий:', reply_markup=markup)
                else:
                    bot.edit_message_text(inline_message_id=callback.inline_message_id,
                                          text=f'📌 {a} - {str(price_print)} руб/стр.\n\n'
                                      'Выберите кол-во копий:', reply_markup=markup)
                    
    def forward(self):
        markup = types.InlineKeyboardMarkup(True)
        markup.add(types.InlineKeyboardButton("Поделиться", switch_inline_query='https://t.me/copykotbot')
        return markup
        
    

mark_up = Markup('ok')

@bot.message_handler(commands=['start', 'reset'])
def handle_start(message):
    user_markup1 = telebot.types.ReplyKeyboardMarkup(True, True)
    user_markup1.row('➕ Добавить файл', '🛒 Корзина')
    user_markup1.row('📌 Канцелярия', '📲 Обратная связь')
    name = message.from_user.first_name
    dbworker.set_state(str(message.chat.id), '1')
    bot.send_message(message.chat.id, f'Приветствую, {name}! Я Копир-кот!\n\nУ нас ты можешь сделать:\n🔹 Ч/Б копии/распечатка А4 - 2,5 руб/стр.'
                                        f'\n🔹 А4 Ч/Б двусторонняя - 4 руб/стр.\n🔹 Скан - 2 руб/стр.\n🔹 Цветная распечатка А4 - 20 руб/стр.\n'
                                      f'🔹 Печать фото 10х15 - 10 руб/фото.'
                                      f'\n🔹 Печать на фотобумаге А4 (глянец, матовая) - 30 руб/стр.'
                                      f'\n🔹 Купить канцелярию.\n\nЗаходи в ТЦ АВЕНЮ на 4 этаж!',
                     reply_markup=user_markup1)



@bot.message_handler(func=lambda message: dbworker.get_current_state(str(message.chat.id)) == 'kanc')
def msg_apps(message):
    try:
        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.type_print = 'Канцелярия'
        for y in dict_price.keys():
            if y in message.text:
                user.file_name = y
                user.price_print = dict_price.get(y)
            else:
                pass
        dbworker.set_state(str(chat_id), '1')
    except Exception as e:
        print(e)


@bot.message_handler(func=lambda message: dbworker.get_current_state(str(message.chat.id)) == 'change')
def msg_apps(message):
    try:
        chat_id = message.chat.id
        user = user_dict[chat_id]
        with shelve.open('itog.py') as db:
            lst3 = list(db.keys())
            keys = list((filter(lambda x: str(message.from_user.id) in x, lst3)))
            for dd in keys:
                a = list(db.get(dd))
                if message.text in a[0]:
                    num = a[2]
                    link = a[5]
                    if a[3] == ' - ':
                        num_page = '1'
                    else:
                        num_page = (a[3])[:-4]
                    user.file_name = a[0]
                    user.price_print = (float(a[4]) / (float(num[:-4]) * float(num_page)))
                    user.link = link[2:-2]
                    user.type_print = a[1]
                    user.num = int(num[0])
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
        user.apps = message.text
        bot.reply_to(message, 'Добавлю это сообщение в примечание к файлу', reply_markup=mark_up.go_basket())
        dbworker.set_state(str(chat_id), '1')
    except Exception as e:
        print(e)



@bot.message_handler(content_types=['text', 'document', 'photo'])
def msg_hand(message):
    try:
        chat_id = message.from_user.id
        start = 'ok'
        user = User(start)
        user_dict[chat_id] = user
        user.info_user = f'{message.from_user.first_name} {message.from_user.last_name} @{message.from_user.username}'
        num = 1
        user.num = num
        if message.text == '📌 Канцелярия':
            bot.send_message(chat_id, 'Добро пожаловать в канцелярию ..', reply_markup=mark_up.kancel())
            user.type_print = 'Канцелярия'
        if message.text == '📲 Обратная связь':
            bot.send_contact(chat_id, phone_number=89039206886, first_name='Екатерина')
            bot.send_location(chat_id, 56.012386, 92.8707427)
            bot.send_message(chat_id, 'Адрес: Проспект Мира 80а, Красноярск (ТЦ АВЕНЮ, 4 этаж)\n'
                                       'Пн - Сб 10:00 - 19:00\nВс - выходной')
        if message.content_type == 'photo':
            file_id = (message.json).get('photo')[0].get('file_id')
            user.file_id = file_id
            file_info = bot.get_file(file_id)
            link = f'https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}'
            user.link = link
            file_name = file_id[:10] + '.png'
            user.file_name = file_name
            bot.send_message(message.chat.id, 'Вы добавили файл:\n\n'
                                                f'💾 {file_name}'
                                              '\n\nВыберите услугу:', reply_markup=mark_up.inline_markup())
        if message.content_type == 'document':
            file_id = message.document.file_id
            user.file_id = file_id
            file_info = bot.get_file(file_id)
            link = f'https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}'
            user.link = link
            file_name = message.document.file_name
            user.file_name = file_name
            if file_name.endswith('.ppt') or file_name.endswith('.doc') or file_name.endswith('.xls'):
                bot.send_message(message.from_user.id,
                                 '❗Такие старые форматы  -  .doc,  .xls,  .ppt.❗\n\n'
                                 f'💾 {file_name}\n\n'
                                 '❗Не смогу определить их'
                                 ' стоимость❗\nПоэтому принимаю кол-во страниц этого файла за 0❗\n\nПоддерживаю форматы:\n\n'
                                 '✔pdf, docx, pptx, xlsx\n✔frw, cdw, dwg\n✔png, jpeg'
                                 '\n\nВыберите услугу:', reply_markup=mark_up.inline_markup())
            else:
                bot.send_message(message.chat.id,  'Вы добавили файл:\n\n'
                                                   f'💾 {file_name}\n\n'
                                                   'Выберите услугу:', reply_markup=mark_up.inline_markup())
        if 'http' in message.text:
            if 'no_preview' or 'psv4.userapi.com' in message.text:
                url = message.text
                result = urllib.request.urlopen(url)
                file_name = os.path.basename(urllib.parse.urlparse(result.url).path)
                user.file_name = file_name
                user.link = url
                if file_name.endswith('.ppt') or file_name.endswith('.doc') or file_name.endswith('.xls'):
                    bot.send_message(message.from_user.id,
                                     '❗Такие старые форматы  -  .doc,  .xls,  .ppt.❗\n\n'
                                    f'💾 {file_name}\n\n'
                                    '❗Не смогу определить их'
                                    ' стоимость❗\nПоэтому принимаю кол-во страниц этого файла за 0❗\n\nПоддерживаю форматы:\n\n'
                                    '✔pdf, docx, pptx, xlsx\n✔frw, cdw, dwg\n✔png, jpeg'
                                    '\n\nВыберите услугу:', reply_markup=mark_up.inline_markup())
                else:
                    bot.send_message(message.chat.id, 'Вы добавили файл:\n\n'
                                                        f'💾 {file_name}\n\n'
                                                      'Выберите услугу:', reply_markup=mark_up.inline_markup())
            else:
                bot.reply_to(message, '❗По этой ссылку я скачать файл не смогу - нужна ссылка на скачивание❗\n\n'
                                      'Пример формата ссылок из VK:\n\n'
                                      '📎 https://vk.com/doc81064057_483314359?hash=406d1e781b028f5265&dl=HAYTANRUGA2TO:'
                                      '1544379753:9642c332b34e71d369&api=1&no_preview=1\n\n'
                                      '📎 https://psv4.userapi.com/c848036/u81064057/docs/d16/3bc44478b397/Skhema_Kriolita.pdf'
                                      '?extra=P2VMpQXtPHssvjwo2YAeVlvWK86Ox-cjjWcM3yJDZlb1eMN-EpsOJ8gh3yFbFkHeisDyZXP'
                                      '-Yci9uxQqf2IpI6fcSUZAhw02RKOfVvGAbEEmCLsG4_PGgCChuAhqArcnrySY_2kgDI9Y32_XuD6Kjkg',
                             reply_markup=mark_up.inline_markup2())
        if message.text == '➕ Добавить файл':
            bot.send_message(chat_id,
                             text=
                                    '❗Отправьте, пожалуйста, ссылку на файл, фотографию или сам файл, который нужно распечатать❗\n\n'
                                    'Поддерживаю форматы:\n\n'
                                    '✔pdf, docx, pptx, xlsx\n✔frw, cdw, dwg\n✔png, jpeg')
        if message.text == '🛒 Корзина':
            mark_up.check_basket(chat_id, callback=message)
    except Exception as e:
        print(e)
        if e == 'HTTP Error 404: Not Found':
            bot.reply_to(message, 'Ой, ошибка❗\nНичего не нашел по этой ссылке, попробуйте скинуть ссылку на файл по-другому')
        bot.send_message(481077652, str(e))



@bot.inline_handler(func=lambda query: True)
def inline_query(query):
    try:
        chat_id = query.from_user.id
        user = user_dict[chat_id]
        dbworker.set_state(str(chat_id), 'kanc')
        if query.query == 'Ручки/Карандаши':
            r = mark_up.kanc_finish(atr='pens')
            bot.answer_inline_query(query.id, r, cache_time=0, is_personal=True)
        if query.query == 'Папки и Файлы':
            r = mark_up.kanc_finish(atr='files')
            bot.answer_inline_query(query.id, r, cache_time=0, is_personal=True)
        if query.query == 'Корректирующие средства':
            r = mark_up.kanc_finish(atr='corection')
            bot.answer_inline_query(query.id, r, cache_time=0, is_personal=True)
        if query.query == 'Изменить':
            with shelve.open('itog.py') as db:
                r = []
                lst3 = list(db.keys())
                keys = list((filter(lambda x: str(query.from_user.id) in x, lst3)))
                for dd in keys:
                    a = list(db.get(dd))
                    default = 'https://pp.userapi.com/c845218/v845218058/cd929/DMHxsJvNO6s.jpg'
                    num = a[2]
                    markup = types.InlineKeyboardMarkup()
                    a1 = types.InlineKeyboardButton("-", callback_data=u'-1')
                    a2 = types.InlineKeyboardButton(str(num[:-4]), callback_data='jr')
                    a3 = types.InlineKeyboardButton("+", callback_data=u'+1')
                    if a[1] == 'Канцелярия':
                        a4 = types.InlineKeyboardButton("⬅ Назад", callback_data=u'НазадВканц')
                    else:
                        a4 = types.InlineKeyboardButton("⬅ Назад", callback_data=u'назад1')
                    a5 = types.InlineKeyboardButton("🛒 Корзина", callback_data=u'корзина')
                    a6 = types.InlineKeyboardButton("📝 Примечания", callback_data=u'примечания')
                    a7 = types.InlineKeyboardButton("❌ Удалить позицию", callback_data=u'удалить позицию')
                    markup.add(a1, a2, a3)
                    markup.add(a4, a5)
                    markup.add(a6)
                    markup.add(a7)
                    input_content = types.InputTextMessageContent(message_text=f"{a[0]}\n\n")
                    r2 = types.InlineQueryResultArticle(id=a[0],
                                                        thumb_url=default, title=a[0],
                                                        description=f'{a[1]}\n{a[2]}\n{a[4]} ₽',
                                                        input_message_content=input_content, reply_markup=markup)
                    r.append(r2)
                dbworker.set_state(str(chat_id), 'change')
                bot.answer_inline_query(query.id, r, cache_time=0, is_personal=True)
    except Exception as e:
        print(e)








@bot.callback_query_handler(func=lambda call: call == '+1' or '-1')
def callback_query_handler(callback):
    try:
        if callback:
            chat_id = callback.from_user.id
            user = user_dict[chat_id]
            num = user.num
            if callback.data == 'удалить позицию':
                if callback.inline_message_id == None:
                    bot.edit_message_text(chat_id=chat_id, message_id=callback.message.message_id, text='Позиция удалена', reply_markup
                                         =mark_up.inline_markup2())
                else:
                    bot.edit_message_text(inline_message_id=callback.inline_message_id, text='Позиция удалена')
                with shelve.open('user_db.py') as db:
                    del db[str(chat_id) + ':' + user.file_name]
                mark_up.check_basket(chat_id, callback)
            if callback.data == '+1':
                num += 1
                user.num = num
                if callback.inline_message_id == None:
                    markup = mark_up.plus(callback, num)
                    bot.edit_message_reply_markup(callback.from_user.id, callback.message.message_id, reply_markup=markup)
                else:
                    if user.type_print == 'Канцелярия':
                        markup = mark_up.inline_plus_kanc(callback, num)
                    else:
                        markup = mark_up.inline_plus(callback, num)
                    bot.edit_message_reply_markup(inline_message_id=callback.inline_message_id, reply_markup=markup)
            if callback.data == '-1':
                num -= 1
                if num < 1:
                    num = 1
                if callback.inline_message_id == None:
                    markup = mark_up.plus(callback, num)
                    bot.edit_message_reply_markup(callback.from_user.id, callback.message.message_id, reply_markup=markup)
                else:
                    if user.type_print == 'Канцелярия':
                        markup = mark_up.inline_plus_kanc(callback, num)
                    else:
                        markup = mark_up.inline_plus(callback, num)
                    bot.edit_message_reply_markup(inline_message_id=callback.inline_message_id, reply_markup=markup)
                user.num = num
            if callback.data == 'назад1':
                if callback.inline_message_id == None:
                    if user.type_print == 'Канцелярия':
                        markup = mark_up.kancel()
                    else:
                        markup = mark_up.inline_markup()
                    bot.edit_message_text(chat_id=chat_id, message_id=callback.message.message_id,
                                          text=f'Выберите услугу:\n\n'
                                               f'💾 {user.file_name}',
                                          reply_markup=markup)
                else:
                    bot.edit_message_text(inline_message_id=callback.inline_message_id,
                                          text=f'Выберите услугу:\n\n'
                                               f'💾 {user.file_name}',
                                          reply_markup=mark_up.inline_markup())
            if callback.data == 'НазадВканц':
                if callback.inline_message_id == None:
                    bot.edit_message_text(chat_id=chat_id, message_id=callback.message.message_id,
                                      text=f'Добро пожаловать в канцелярию ..',
                                      reply_markup=mark_up.kancel())
                else:
                    bot.send_message(chat_id,
                                     text=f'Добро пожаловать в канцелярию ..',
                                     reply_markup=mark_up.kancel())
            if callback.data == 'корзина':
                file_name = (user.file_name).lower()
                url = user.link
                if user.type_print != 'Канцелярия':
                    urllib2.urlretrieve(url, file_name)
                elif user.type_print == 'Канцелярия':
                    mark_up.add_kancel(callback)
                if file_name.endswith('.docx'):
                    document = Document(file_name)
                    document.save(f'{file_name}1.docx')
                    document.save(f'{file_name}1.zip')
                    zf = zipfile.ZipFile(f'{file_name}1.zip')
                    f = zf.open('docProps/app.xml').read()
                    soup = BeautifulSoup(f, 'xml')
                    num_page = soup.find('Pages').next_element
                    user.num_page = int(num_page)
                    mark_up.gg_basket(callback)
                if file_name.endswith('.pdf'):
                    input1 = PdfFileReader(open(file_name, "rb"))
                    num_page = input1.getNumPages()
                    user.num_page = int(num_page)
                    mark_up.gg_basket(callback)
                format1 = ['.frw', '.cdw', '.png', 'jpeg', '.dwg', '.dwt' '.gif', '.txt', '.mp4', '.jpg']
                for y in format1:
                    if y == file_name[-4:]:
                        num_page = 1
                        user.num_page = num_page
                        mark_up.gg_basket(callback)
                    else:
                        pass
                if file_name.endswith('.doc'):
                    num_page = 0
                    user.num_page = num_page
                    mark_up.gg_basket(callback)
                if file_name.endswith('.pptx'):
                    filename = os.path.abspath(file_name)
                    np = Presentation(filename)
                    num_page = len(np.slides)
                    user.num_page = int(num_page)
                    mark_up.gg_basket(callback)
                if file_name.endswith('.xlsx'):
                    xl = pd.ExcelFile(os.path.abspath(file_name))
                    num_page = len(xl.sheet_names)
                    user.num_page = int(num_page)
                    mark_up.gg_basket(callback)
                with shelve.open('itog.py') as db:
                    l = []
                    s = []
                    r = []
                    lst3 = list(db.keys())
                    lst = list((filter(lambda x: str(chat_id) in x, lst3)))
                    for dd in lst:
                        a = db.get(dd)
                        r.append(a)
                    for line3 in r:
                        line2 = ' '.join(line3[:5])
                        lin = line3[4]
                        s.append(float(lin))
                        l.append(line2)
                    total_price = sum(s)
                m = ' ₽\n\n💾 '.join(l)
                user.total_price = total_price
                if callback.inline_message_id == None:
                    bot.edit_message_text(chat_id=chat_id, message_id=callback.message.message_id, text='Ваша корзина :\n\n'
                                                                                                    f'💾 {m} ₽.\n\n'
                                                                                                    f'Итого: {str(total_price)}  ₽.',
                                      reply_markup=mark_up.gen_markup2())
                else:
                    bot.send_message(chat_id,
                                          text='Ваша корзина :\n\n'
                                               f'💾 {m} ₽.\n\n'
                                               f'Итого: {str(total_price)}  ₽.',
                                          reply_markup=mark_up.gen_markup2())
            if callback.data == 'примечания':
                if callback.inline_message_id == None:
                    bot.edit_message_text(chat_id=chat_id, message_id=callback.message.message_id,
                                      text='Идём дальше! Напишите примечания к данному файлу ..\n\n'
                                           f'💾 {user.file_name}', reply_markup=mark_up.back())
                else:
                    bot.edit_message_text(inline_message_id=callback.inline_message_id,
                                          text='Идём дальше! Напишите примечания к данному файлу ..\n\n'
                                               f'💾 {user.file_name}', reply_markup=mark_up.back())
                dbworker.set_state(str(chat_id), '2')
            if callback.data == 'оформить':
                markup = mark_up.gen_markup1(chat_id, total_price=user.total_price)
                user.message_id = callback.message.message_id
                bot.edit_message_text(chat_id=chat_id, message_id=callback.message.message_id,
                                      text='❗Внимание❗\nЕсли кол-во страниц '
                                           'не совпадает с действительностью, то рекомендуется выбрать "Оплата при получении"\n\n'
                                           'Выберите тип оплаты ..', reply_markup=markup)
            if callback.data == 'очистить':
                mark_up.clear_basket(chat_id)
                bot.edit_message_text(chat_id=chat_id, message_id=callback.message.message_id,
                                      text='Ваша корзина очищена!', reply_markup=mark_up.inline_markup2())
            if callback.data == 'добавить':
                num = 1
                user.num = num
                bot.edit_message_text(chat_id=chat_id, message_id=callback.message.message_id,
                                      text='❗Отправьте, пожалуйста, ссылку на файл или сам файл, который нужно распечатать❗\n\n'
                                 'Поддерживаю форматы:\n\n'
                                 '✔pdf, docx, pptx, xlsx\n✔frw, cdw, dwg\n✔png, jpeg')
            if callback.data == 'назад':
                dbworker.set_state(str(chat_id), '1')
                if callback.inline_message_id == None:
                    if user.type_print == 'Канцелярия':
                        markup = mark_up.plus_kanc(callback, num)
                    else:
                        markup = mark_up.plus(callback, num)
                    bot.edit_message_text(chat_id=chat_id, message_id=callback.message.message_id,
                                      text='Хорошо, выберите кол-во копий:', reply_markup=markup)
                else:
                    if user.type_print == 'Канцелярия':
                        markup = mark_up.inline_plus_kanc(callback, num)
                    else:
                        markup = mark_up.inline_plus(callback, num)
                    bot.edit_message_text(inline_message_id=callback.inline_message_id,
                                          text='Хорошо, выберите кол-во копий:', reply_markup=markup)
            if callback.data == 'Ч/Б Печать(распечатка)':
                mark_up.pechat(a='Ч/Б копии/распечатка А4', price_print=2.5, callback=callback)
            if callback.data == 'Печать фото 10х15':
                mark_up.pechat(a='Печать фото 10х15', price_print=10.0, callback=callback)
            if callback.data == 'Цветная печать А4':
                mark_up.pechat(a='Цветная распечатка А4', price_print=20.0, callback=callback)
            if callback.data == 'А4 Ч/Б двусторонняя':
                price_print = 2.0
                mark_up.callduty(price_print, callback)
                num = user.num
                if num != 1:
                    markup = mark_up.num_copy_markup2(callback, num)
                else:
                    markup = mark_up.num_copy_markup1()
                if callback.inline_message_id == None:
                    bot.edit_message_text(chat_id=callback.from_user.id, message_id=callback.message.message_id,
                                      text='📌 А4 Ч/Б двусторонняя - 4 руб/стр.\n\n'
                                           'Выберите кол-во копий:', reply_markup=markup)
                else:
                    bot.edit_message_text(inline_message_id=callback.inline_message_id,
                                          text='📌 А4 Ч/Б двусторонняя - 4 руб/стр.\n\n'
                                               'Выберите кол-во копий:', reply_markup=markup)
            if callback.data == 'Печать на фотобумаге':
                mark_up.pechat(a='Печать на фотобумаге А4 (глянец, матовая)', price_print=30.0, callback=callback)
            if callback.data == "later":
                number = f'{mark_up.random_pool()}'
                bot.answer_callback_query(callback.id, "Вы выбрали - По факту получения")
                j = mark_up.result_ship(chat_id, 1)
                m = mark_up.result_ship(chat_id, 0)
                now = datetime.now()
                today = datetime.today().strftime('%H:%M')
                time_order = f"{now.year}-{now.month}-{now.day}  {today}"
                from_chat_id = -1001302729558
                type_pay = 'По факту получения'
                name = f'{callback.from_user.first_name} {callback.from_user.last_name} @{callback.from_user.username}'
                bot.edit_message_text(chat_id=callback.from_user.id, message_id=callback.message.message_id,
                                      text=f'Супер!✔\nТеперь ваш заказ на сумму {str(user.total_price)} отправлен Копир-коту!'
                        f'✔\n\n💾 {j} ₽\n\nЗабрать заказ можете в любое рабочее время по адресу: Проспект Мира 80а, Красноярск (ТЦ АВЕНЮ, 4 этаж)\n\n'
                        f'Номер вашего заказа - {number}', reply_markup=mark_up.forward())
                bot.send_message(from_chat_id, f'{m}'
                                               f'______________________________\n\n'
                                               f'Номер заказа - {number}\n'
                                               f'Время заказа: {time_order}\n'
                                               f'Заказчик: {name}\n'
                                               f'Тип оплаты: {type_pay}\n\n'
                                               f'Итого: {str(user.total_price)} руб.'
                                 )
                mark_up.clear_basket(chat_id)
    except KeyError as a:
        print(a)
        chat_id = callback.from_user.id
        bot.send_message(chat_id,
                         text='Отправьте, пожалуйста, ссылку на файл или сам файл, который нужно распечатать\n\n'
                              'Поддерживаю форматы:\n\n'
                              '✔pdf, docx, pptx, xlsx\n✔frw, cdw, dwg\n✔png, jpeg')
        bot.send_message(481077652, str(a))
    except Exception as e:
        print(e)
        chat_id = callback.from_user.id
        if e == 'expected string or bytes-like object' or chat_id:
            mark_up.check_basket(chat_id, callback)
        bot.send_message(481077652, str(e))




"""
@bot.shipping_query_handler(func=lambda query: True)
def shipping(shipping_query):
    bot.answer_shipping_query(shipping_query.id, ok=True, shipping_options=False,
                              error_message='Oh, што-то пошло не так. Попробуйте повторить позже!')


@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True,
                                  error_message="Проблемы с картой"
                                                " повторите платеж позже.")


@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    chat_id = message.chat.id
    user = user_dict[chat_id]
    number = str(mark_up.random_pool())
    bot.send_message(message.from_user.id, 'Супер! Теперь ваш заказ отправлен..\nНомер вашего заказа - ' + number)
    mark_up.result_ship(chat_id)
    from_chat_id = -1001302729558
    now = datetime.now()
    hours = int(now.hour) + 7
    time_order = str(f"{now.year}-{now.month}-{now.day}  {str(hours)}:{now.minute}")
    type_pay = 'Наличные'
    name = f'{message.from_user.first_name} {message.from_user.last_name} @{message.from_user.username}'
    bot.edit_message_text(chat_id=message.from_user.id, message_id=message.message_id,
                          text=f'Супер!✔\nТеперь ваш заказ отправлен✔\n\n💾 {j} ₽\n\nНомер вашего заказа - {number}')
    bot.send_message(from_chat_id, f'{m}'
                                   f'___________________________\n\n'
                                   f'Номер заказа - {number}\n'
                                   f'Время заказа: {time_order}\n'
                                   f'Заказчик: {name}\n'
                                   f'Тип оплаты: {type_pay}\n\n'
                                   f'Итого: {str(user.total_price)} ₽.'
                     )
    mark_up.clear_basket(chat_id)
"""

@server.route('/' + TOKEN, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "OK", 200

@server.route('/' + 'PAYMENTS', methods=['POST'])
def Check_Payments():
    chat_id = int(request.form['label'])
    user = user_dict[chat_id]
    total_price1 = float(request.form['amount'])
    total_price2 = (float(user.total_price) * 0.98)
    if total_price1 == total_price2:
        mark_up.finish_payments(chat_id, user)
    return "HTTP 200 OK", 200
    
     

@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://flask-est-1996.herokuapp.com/' + TOKEN)
    return "!", 200


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
