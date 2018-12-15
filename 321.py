# -*- coding: utf-8 -*-
#coding: utf-8
import dbworker
import telebot
from telebot.types import LabeledPrice
from telebot import types
import shelve
import random
import datetime
from datetime import datetime
import urllib
import urllib.request as urllib2
import os
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


def inline_markup():
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(types.InlineKeyboardButton("Ч/Б Печать(распечатка)", callback_data='Ч/Б Печать(распечатка)'),
               types.InlineKeyboardButton("Цветная Печать А4", callback_data='Цветная печать А4'),
               types.InlineKeyboardButton("Печать фото 10х15", callback_data='Печать фото 10х15'))
    return markup

def inline_markup2():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("➕ Добавить файл", callback_data='добавить'))
    return markup


def num_copy_markup1():
    markup = types.InlineKeyboardMarkup()
    a1 = types.InlineKeyboardButton("-", callback_data=u'-1')
    a2 = types.InlineKeyboardButton('1', callback_data='jr')
    a3 = types.InlineKeyboardButton("+", callback_data=u'+1')
    a4 = types.InlineKeyboardButton("⬅ Назад", callback_data=u'назад1')
    a5 = types.InlineKeyboardButton("🛒 Корзина", callback_data=u'корзина')
    a6 = types.InlineKeyboardButton("📝 Примечания", callback_data=u'примечания')
    markup.add(a1, a2, a3)
    markup.add(a4, a5)
    markup.add(a6)
    return markup

def num_copy_markup2(callback, num):
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

def gen_markup1():
    markup = types.InlineKeyboardMarkup(True)
    markup.row_width = 2
    markup.add(types.InlineKeyboardButton("Cейчас в Telegram", callback_data='now'),
               types.InlineKeyboardButton("По факту получения", callback_data='later'),
               types.InlineKeyboardButton("⬅ Назад", callback_data='корзина'))
    return markup

def go_basket():
    markup = types.InlineKeyboardMarkup(True)
    markup.add(types.InlineKeyboardButton("🛒 В корзину", callback_data='корзина'),
               types.InlineKeyboardButton("🔃 Изменить примечание ", callback_data='примечания'),
               types.InlineKeyboardButton("⬅ Назад", callback_data='назад')
              )
    return markup

def go_old():
    markup = types.InlineKeyboardMarkup(True)
    markup.add(types.InlineKeyboardButton("🛒 Далее", callback_data='корзина2'),
               types.InlineKeyboardButton("❎ Очистить", callback_data='очистить')
              )
    return markup   
    
def gen_markup2():
    markup = types.InlineKeyboardMarkup(True)
    markup.row_width = 2
    markup.add(types.InlineKeyboardButton("🏁 Оформить", callback_data='оформить'),
               types.InlineKeyboardButton("➕ Добавить файл", callback_data='добавить'),
               types.InlineKeyboardButton("❎ Очистить", callback_data='очистить'),
               types.InlineKeyboardButton("⬅ Назад", callback_data='назад')
               )
    return markup


@bot.message_handler(commands=['start', 'reset'])
def handle_start(message):
    user_markup1 = telebot.types.ReplyKeyboardMarkup(True, True)
    user_markup1.row('➕ Добавить файл', '🛒 Корзина')
    user_markup1.row('📌 Канцелярия', '📲 Обратная связь')
    name = message.from_user.first_name
    dbworker.set_state(str(message.chat.id), '1')
    bot.send_message(message.chat.id, f'Приветствую, {name}! Я Копир-кот!\n\nУ нас ты можешь сделать:\n🔹 распечатки'
                                      f' А4;\n🔹 копии А4;\n🔹 купить канцелярию.\n\nЗаходи в ТЦ АВЕНЮ на 4 этаж!',
                     reply_markup=user_markup1)

@bot.message_handler(func=lambda message: dbworker.get_current_state(str(message.chat.id)) == '2')
def msg_apps(message):
    try:
        chat_id = message.chat.id
        user = user_dict[chat_id]
        apps = message.text
        user.apps = apps
        bot.reply_to(message, 'Добавлю это сообщение в примечание к файлу', reply_markup=go_basket()) 
        dbworker.set_state(str(chat_id), '1')
    except Exception as e:
        print(e)
    
    
@bot.message_handler(content_types=['text', 'document', 'photo'])
def msg_hand(message):
    try:
        chat_id = message.chat.id
        start = 'ok'
        user = User(start)
        user_dict[chat_id] = user
        num = 1
        user.num = num
        if message.content_type == 'photo':
                bot.send_message(message.chat.id, '❗Пожалуйста скиньте фотографию, как файл❗\n\n'
                                               'Поддерживаю форматы:\n\✔npdf, docx, pptx, xlsx\n✔frw, cdw, dwg\n✔png, jpeg')
        if message.content_type == 'document':
                file_id = message.document.file_id
                user.file_id = file_id
                file_info = bot.get_file(file_id)
                link = f'https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}'
                user.link = link
                file_name = message.document.file_name
                user.file_name = file_name
                if file_name.endswith('.ppt') or file_name.endswith('.doc') or file_name.endswith('.xls'):
                    bot.send_message(message.from_user.id, '❗Такие старые форматы - .doc, .xls, .ppt. Не смогу определить их'
                                                           'стоимость❗\nПоэтому принимаю кол-во страниц за 1❗\n\nПоддерживаю форматы:\n\n'
                                                           '✔pdf, docx, pptx, xlsx\n✔frw, cdw, dwg\n✔png, jpeg'
                                                           '\n\nВыберите услугу:', reply_markup=inline_markup())
                else:
                    bot.send_message(message.chat.id, 'Поддерживаю форматы:\n\n'
                                                      '✔pdf, docx, pptx, xlsx\n✔frw, cdw, dwg\n✔png, jpeg'
                                                      '\n\nВыберите услугу:', reply_markup=inline_markup())
        if 'https' in message.text:
            if 'no_preview' or 'psv4.userapi.com' in message.text:
                url = message.text
                result = urllib.request.urlopen(url)
                file_name = os.path.basename(urllib.parse.urlparse(result.url).path)
                user.file_name = file_name
                user.link = url
                if file_name.endswith('.ppt') or file_name.endswith('.doc') or file_name.endswith('.xls'):
                    bot.send_message(message.from_user.id, '❗Такие старые форматы - .doc, .xls, .ppt. Не смогу определить их'
                                                           'стоимость❗\nПоэтому принимаю кол-во страниц за 1❗\n\nПоддерживаю форматы:\n\n'
                                                           '✔pdf, docx, pptx, xlsx\n✔frw, cdw, dwg\n✔png, jpeg'
                                                           '\n\nВыберите услугу:', reply_markup=inline_markup())
                else:
                    bot.send_message(message.chat.id, 'Поддерживаю форматы:\n\n'
                                                  '✔pdf, docx, pptx, xlsx\n✔frw, cdw, dwg\n✔png, jpeg'
                                                  '\n\nВыберите услугу:', reply_markup=inline_markup())
            else:
                bot.reply_to(message, '❗По этой ссылку я скачать файл не смогу - нужна ссылка на скачивание❗\n\n'
                    'Пример формата ссылок из VK:\n\n'
                    '📎 https://vk.com/doc81064057_483314359?hash=406d1e781b028f5265&dl=HAYTANRUGA2TO:'
                    '1544379753:9642c332b35e71d379&api=1&no_preview=1\n\n'
                    '📎 https://psv4.userapi.com/c848036/u81064057/docs/d16/3bc44478b397/Skhema_Kriolita.pdf'
                    '?extra=P2VMpQXtPHssvjwo2YAeVlvWK86Ox-cjjWcM3yJDZlb1eMN-EpsOJ8gh3yFbFkHeisDyZXP'
                    '-Yci9uxQqf2IpI6fcSUZAhw0lRKOiVvGAbEEmCLsG4_PGgCChuAhqArcnrySY_2kgDI9Y32_XuD6Kjkg', reply_markup=inline_markup2()) 
        if message.text == '➕ Добавить файл':
            bot.send_message(chat_id,
                                  text='Отправьте, пожалуйста, ссылку на файл или сам файл, который нужно распечатать\n\n'
                                  'Поддерживаю форматы:\n\n'
                                  '✔pdf, docx, pptx, xlsx\n✔frw, cdw, dwg\n✔png, jpeg')
        if message.text == '🛒 Корзина':
            with shelve.open('itog.py') as db:
                lst3 = list(db.keys())
                if list(filter(lambda y: str(chat_id) in y, lst3)) == []:
                    bot.send_message(chat_id, 'Ваша корзина пуста!', reply_markup=inline_markup2())
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
                                              f'Итого: {str(total_price)}  ₽.', reply_markup=gen_markup2())
    except Exception as e:
        print(e)

        
def gg_basket(callback):
    chat_id = callback.from_user.id
    user = user_dict[chat_id]
    with shelve.open('itog.py') as db:
        db[str(chat_id) + ':' + user.file_name] = [user.file_name, f'({user.type_print})', (str(user.num) + ' экз.'),
            (str(user.num_page) + ' стр.'),
            (str(user.num_page * user.num * user.price_print)),
            ('\n\n' + user.link + '\n\n'), ('Прим.\n' + str(user.apps) + '\n\n')]
 
def callduty(price_print, callback):
    chat_id = callback.from_user.id
    user = user_dict[chat_id]
    type_print = callback.data
    user.price_print = price_print
    user.type_print = type_print
        
@bot.callback_query_handler(func=lambda call: call == '+1' or '-1')
def callback_query_handler(callback):
    try:
        if callback.message:
            chat_id = callback.from_user.id
            user = user_dict[chat_id]
            num = user.num
            if callback.data == '+1':
                num += 1
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
                bot.edit_message_reply_markup(callback.from_user.id, callback.message.message_id, reply_markup=markup)
                user.num = num
            if callback.data == '-1':
                num -= 1
                if num < 1:
                    num = 1
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
                user.num = num
                bot.edit_message_reply_markup(callback.from_user.id, callback.message.message_id, reply_markup=markup)
            if callback.data == 'назад1':
                bot.edit_message_text(chat_id=chat_id, message_id=callback.message.message_id, text='Выберите услугу:', reply_markup=inline_markup())
            if callback.data == 'корзина':
                file_name = user.file_name
                url = user.link
                urllib2.urlretrieve(url, file_name)
                if '.docx' in file_name:
                    print(file_name)
                    document = Document(file_name)
                    document.save(f'{file_name}1.docx')
                    document.save(f'{file_name}1.zip')
                    zf = zipfile.ZipFile(f'{file_name}1.zip')
                    f = zf.open('docProps/app.xml').read()
                    soup = BeautifulSoup(f, 'xml')
                    num_page = soup.find('Pages').next_element
                    user.num_page = int(num_page)
                    gg_basket(callback) 
                elif '.pdf' in file_name:
                    input1 = PdfFileReader(open(file_name, "rb"))
                    num_page = input1.getNumPages()
                    user.num_page = int(num_page)
                    gg_basket(callback)
                elif file_name.endswith('.ppt') or file_name.endswith('.doc') or file_name.endswith('.xls'):
                    num_page = 1
                    user.num_page = num_page
                    gg_basket(callback) 
                elif '.frw' or '.cdw' or '.png' or '.jpeg' or '.dwg' in file_name:
                    num_page = 1
                    user.num_page = num_page
                    gg_basket(callback)
                elif '.pptx' in file_name:
                    filename = os.path.abspath(file_name)
                    np = Presentation(filename)
                    num_page = len(np.slides)
                    user.num_page = int(num_page)
                    gg_basket(callback)
                elif '.xlsx' in file_name:
                    xl = pd.ExcelFile(os.path.abspath(file_name))
                    num_page = len(xl.sheet_names)
                    user.num_page = int(num_page)
                    gg_basket(callback)
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
                bot.edit_message_text(chat_id=chat_id, message_id=callback.message.message_id, text='Ваша корзина :\n\n'
                                                       f'💾 {m} ₽.\n\n'
                                                       f'Итого: {str(total_price)}  ₽.', reply_markup=gen_markup2())
            if callback.data == 'примечания':
                bot.edit_message_text(chat_id=chat_id, message_id=callback.message.message_id, text='Идём дальше! Напишите примечания к заказу ..')
                dbworker.set_state(str(chat_id), '2')
            if callback.data == 'оформить':
                bot.edit_message_text(chat_id=chat_id, message_id=callback.message.message_id, text='❗Внимание❗\nЕсли кол-во страниц ' 
                                      'не совпадает с действительностью, то рекомендуется выбрать "По факту получения"\n\n'  
                                      'Выберите тип оплаты ..', reply_markup=gen_markup1())
            if callback.data == 'очистить':
                with shelve.open('itog.py') as db:
                    lst3 = list(db.keys())
                    lst = list((filter(lambda x: str(chat_id) in x, lst3)))
                    for dd in lst:
                        del db[dd]
                bot.edit_message_text(chat_id=chat_id, message_id=callback.message.message_id, text='Ваша корзина очищена!', reply_markup=inline_markup2())
            if callback.data == 'добавить':
                num = 1
                user.num = num
                bot.send_message(callback.from_user.id,
                                       "Отправьте, пожалуйста, ссылку на файл или сам файл, который нужно распечатать")
            if callback.data == 'назад':
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
                bot.edit_message_text(chat_id=chat_id, message_id=callback.message.message_id,
                                      text='Хорошо, выберите кол-во копий:', reply_markup=markup)
            if callback.data == 'Ч/Б Печать(распечатка)':  
                price_print = 2.5
                callduty(price_print, callback)
                num = user.num
                if num != 1:
                    markup = num_copy_markup2(callback, num)
                else:
                    markup = num_copy_markup1()
                bot.edit_message_text(chat_id=callback.from_user.id, message_id=callback.message.message_id,
                                      text='Хорошо, выберите кол-во копий', reply_markup=markup)
            if callback.data == 'Печать фото 10х15':
                price_print = 10.0
                callduty(price_print, callback)
                num = user.num
                if num != 1:
                    markup = num_copy_markup2(callback, num)
                else:
                    markup = num_copy_markup1()
                bot.edit_message_text(chat_id=callback.from_user.id, message_id=callback.message.message_id,
                                      text='Хорошо, выберите кол-во копий', reply_markup=markup)
            if callback.data == 'Цветная печать А4':
                price_print = 20.0
                callduty(price_print, callback)
                num = user.num
                if num != 1:
                    markup = num_copy_markup2(callback, num)
                else:
                    markup = num_copy_markup1()
                bot.edit_message_text(chat_id=callback.from_user.id, message_id=callback.message.message_id,
                                      text='Хорошо, выберите кол-во копий', reply_markup=markup)
            if callback.data == "later":
                number = str(random_pool())
                bot.answer_callback_query(callback.id, "Вы выбрали - По факту получения")
                bot.edit_message_text(chat_id=callback.from_user.id, message_id=callback.message.message_id,
                                      text='Супер!✔\nТеперь ваш заказ отправлен✔\n\nНомер вашего заказа - ' + number)
                with shelve.open('itog.py') as db:
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
                type_pay = 'По факту получения'
                name = callback.from_user.first_name + ' ' + callback.from_user.last_name + ' @' + callback.from_user.username
                bot.send_message(from_chat_id, f'{m}'
                                               f'______________________________\n\n'
                                               f'Номер заказа - {number}\n'
                                               f'Время заказа: {time_order}\n'
                                               f'Заказчик: {name}\n'
                                               f'Тип оплаты: {type_pay}\n\n'
                                               f'Итого: {str(user.total_price)} руб.'
                                 )
                with shelve.open('itog.py') as db:
                    lst3 = list(db.keys())
                    lst = list((filter(lambda x: str(chat_id) in x, lst3)))
                    for dd in lst:
                        del db[dd]
            if callback.data == "now":
                bot.answer_callback_query(callback.id, "Вы выбрали - Cейчас в Telegram")
                price = str(user.total_price)
                price1 = user.total_price * 100
                prices = [LabeledPrice(label=f'Стоимость услуги: ', amount=int(price1))]
                title = user.type_print
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
                                            f'Однако Вы можете оплатить заказ по факту получения', reply_markup=gen_markup2())
    except Exception as e:
        print(e)




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


@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    chat_id = message.chat.id
    user = user_dict[chat_id]
    number = str(random_pool())
    bot.send_message(message.from_user.id, 'Супер! Теперь ваш заказ отправлен..\nНомер вашего заказа - ' + number)
    with shelve.open('itog.py') as db:
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

    with shelve.open('itog') as db:
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
