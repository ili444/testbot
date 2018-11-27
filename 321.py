# -*- coding: utf-8 -*-
#coding: utf-8
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

def main_menu():
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(types.InlineKeyboardButton("Ч/Б Печать(распечатка)", callback_data='1Ч/Б Печать(распечатка)'),
               types.InlineKeyboardButton("Цветная Печать А4", callback_data='1Цветная печать А4'),
               types.InlineKeyboardButton("Печать фото 10х15", callback_data='1Печать фото 10х15'))
    return markup

def inline_markup():
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(types.InlineKeyboardButton("Ч/Б Печать(распечатка)", callback_data='Ч/Б Печать(распечатка)'),
               types.InlineKeyboardButton("Цветная Печать А4", callback_data='Цветная печать А4'),
               types.InlineKeyboardButton("Печать фото 10х15", callback_data='Печать фото 10х15'))
    return markup

def inline_markup2():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Добавить файл", callback_data='добавить'))
    return markup

def clear_basket():
    user_markup1 = telebot.types.ReplyKeyboardMarkup(True, False)
    user_markup1.row('Копирование', 'Ч/Б Печать(распечатка)')
    user_markup1.row('Канцелярия', 'Печать фото 10х15')
    user_markup1.row('Цветная печать', 'Обратная связь')
    return clear_basket()


def num_copy_markup1():
    markup = types.InlineKeyboardMarkup()
    a1 = types.InlineKeyboardButton("-", callback_data=u'-1')
    a2 = types.InlineKeyboardButton('1', callback_data='jr')
    a3 = types.InlineKeyboardButton("+", callback_data=u'+1')
    a4 = types.InlineKeyboardButton("Назад", callback_data=u'назад1')
    a5 = types.InlineKeyboardButton("Корзина", callback_data=u'корзина')
    markup.add(a1, a2, a3)
    markup.add(a4, a5)
    return markup

def gen_markup1():
    markup = types.InlineKeyboardMarkup(True)
    markup.row_width = 2
    markup.add(types.InlineKeyboardButton("Cейчас в Telegram", callback_data='now'),
               types.InlineKeyboardButton("По факту получения", callback_data='later'),
               types.InlineKeyboardButton("Назад", callback_data='корзина'))
    return markup



def gen_markup2():
    markup = types.InlineKeyboardMarkup(True)
    markup.row_width = 2
    markup.add(types.InlineKeyboardButton("Оформить", callback_data='оформить'),
               types.InlineKeyboardButton("Добавить файл", callback_data='добавить'),
               types.InlineKeyboardButton("Очистить", callback_data='очистить'),
               types.InlineKeyboardButton("Назад", callback_data='назад')
               )
    return markup


@bot.message_handler(commands=['start'])
def handle_start(message):
    user_markup1 = telebot.types.ReplyKeyboardMarkup(True, True)
    user_markup1.row('Главное меню', 'Корзина')
    user_markup1.row('Канцелярия', 'Обратная связь')
    name = message.from_user.first_name
    bot.send_message(message.chat.id, f'Приветствую, {name}! Я Копир-кот!\n\nУ нас ты можешь сделать:\n- распечатки'
                                      f' А4;\n- копии А4;\n- купить канцелярию.\n\nЗаходи в ТЦ АВЕНЮ на 4 этаж!', reply_markup=user_markup1)

  
                                      
@bot.message_handler(content_types=['text', 'document'])
def msg_hand(message):
    try:
        chat_id = message.chat.id
        start = 'ok'
        user = User(start)
        user_dict[chat_id] = user
        num = 1
        user.num = num
        if message.content_type == 'document':
            if user.type_print == None:
                file_id = message.document.file_id
                user.file_id = file_id
                file_info = bot.get_file(file_id)
                link = f'https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}'
                user.link = link
                file_name = message.document.file_name
                user.file_name = file_name
                if file_name.endswith('.ppt') or file_name.endswith('.doc') or file_name.endswith('.xls'):
                    bot.send_message(message.from_user.id, 'Такие старые форматы - не смогу определить их'
                                     'стоимость!\nПерешлю без выставления чека!\n\nПоддерживаю форматы:\n\n'
                                     'pdf, docx, pptx, xlsx\nfrw, cdw, dwg\npng, jpeg')
                else:
                    bot.send_message(message.chat.id, 'Поддерживаю форматы:\n\n'
                                     'pdf, docx, pptx, xlsx\nfrw, cdw, dwg\npng, jpeg'
                                     '\n\nВыберите услугу:', reply_markup=inline_markup())
            else:
                bot.send_message(chat_id, text='Хорошо, выберите кол-во копий:', reply_markup=num_copy_markup1())
        if 'https' in message.text:
            if user.type_print == None:
                url = message.text
                result = urllib.request.urlopen(url)
                file_name = os.path.basename(urllib.parse.urlparse(result.url).path)
                user.file_name = file_name
                user.link = url
                bot.send_message(message.chat.id, 'Поддерживаю форматы:\n\n'
                                     'pdf, docx, pptx, xlsx\nfrw, cdw, dwg\npng, jpeg'
                                 '\n\nВыберите услугу:', reply_markup=inline_markup())
            else:
                bot.send_message(chat_id, text='Хорошо, выберите кол-во копий:', reply_markup=num_copy_markup1())
        if message.text == 'Главное меню':
            bot.send_message(message.chat.id, 'Поддерживаю форматы:\n\n'
                                     'pdf, docx, pptx, xlsx\nfrw, cdw, dwg\npng, jpeg'
                             '\n\nВыберите услугу:', reply_markup=main_menu())
        if message.text == 'Корзина':
            with shelve.open('itog') as db:
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
    with shelve.open('itog') as db:
        db[str(chat_id) + ':' + user.file_name] = [user.file_name, f'({user.type_print})', (str(user.num) + ' экз.'),
            (str(user.num_page) + ' стр.'),
            (str(user.num_page * user.num * user.price_print)),
            ('\n\n' + user.link + '\n\n')]
 
def callduty(price_print, callback):
    type_print = callback.data
    user.price_print = price_print
    user.type_print = type_print
        
@bot.callback_query_handler(func=lambda call: call == '+1' or '-1')
def callback_query_handler(callback):
    if callback.message:
        chat_id = callback.from_user.id
        user = user_dict[chat_id]
        num = user.num
        if callback.data == '1Печать фото 10х15':
            price_print = 10.0
            callduty(price_print, callback)
            bot.edit_message_text(chat_id=chat_id, message_id=callback.message.message_id,
                                  text="Отправьте, пожалуйста, ссылку на файл или сам файл, который нужно распечатать")
        if callback.data == '1Цветная печать А4':
            price_print = 20.0
            callduty(price_print, callback)
            bot.edit_message_text(chat_id=chat_id, message_id=callback.message.message_id,
                                  text="Отправьте, пожалуйста, ссылку на файл или сам файл, который нужно распечатать")
        if callback.data == '1Ч/Б Печать(распечатка)':
            price_print = 2.5
            callduty(price_print, callback)
            bot.edit_message_text(chat_id=chat_id, message_id=callback.message.message_id,
                                  text="Отправьте, пожалуйста, ссылку на файл или сам файл, который нужно распечатать")
        if callback.data == '+1':
            num += 1
            markup = types.InlineKeyboardMarkup()
            a1 = types.InlineKeyboardButton("-", callback_data=u'-1')
            a2 = types.InlineKeyboardButton(str(num), callback_data='jr')
            a3 = types.InlineKeyboardButton("+", callback_data=u'+1')
            a4 = types.InlineKeyboardButton("Назад", callback_data=u'назад1')
            a5 = types.InlineKeyboardButton("Корзина", callback_data=u'корзина')
            markup.add(a1, a2, a3)
            markup.add(a4, a5)
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
            a4 = types.InlineKeyboardButton("Назад", callback_data=u'назад1')
            a5 = types.InlineKeyboardButton("Корзина", callback_data=u'корзина')
            markup.add(a1, a2, a3)
            markup.add(a4, a5)
            user.num = num
            bot.edit_message_reply_markup(callback.from_user.id, callback.message.message_id, reply_markup=markup)
        if callback.data == 'назад1':
            bot.edit_message_text(chat_id=chat_id, message_id=callback.message.message_id, text='Выберите услугу:', reply_markup=inline_markup())
        if callback.data == 'корзина':
            file_name = user.file_name
            url = user.link
            urllib2.urlretrieve(url, file_name)
            if '.docx' in file_name:
                document = Document(file_name)
                document.save(f'{file_name}1.docx')
                document.save(f'{file_name}1.zip')
                zf = zipfile.ZipFile(f'{file_name}1.zip')
                f = zf.open('docProps/app.xml').read()
                soup = BeautifulSoup(f, 'xml')
                num_page = soup.find('Pages').next_element
                user.num_page = int(num_page)
                gg_basket(callback) 
            if '.pdf' in file_name:
                input1 = PdfFileReader(open(file_name, "rb"))
                num_page = input1.getNumPages()
                user.num_page = int(num_page)
                gg_basket(callback)
            if '.frw' or '.cdw' or '.png' or '.jpeg' or '.dwg':
                user.num_page = 1
                gg_basket(callback)
            if '.pptx' in file_name:
                filename = os.path.abspath('1111.pptx')
                np = Presentation(filename)
                num_page = len(np.slides)
                user.num_page = int(num_page)
                gg_basket(callback)
            if '.xlsx' in file_name:
                xl = pd.ExcelFile(os.path.abspath(file_name))
                num_page = len(xl.sheet_names)
                user.num_page = int(num_page)
                gg_basket(callback)
            with shelve.open('itog') as db:
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
            #bot.send_message(callback.from_user.id, 'Идём дальше! Напишите примечания к заказу ..')
        if callback.data == 'оформить':
            bot.edit_message_text(chat_id=chat_id, message_id=callback.message.message_id, text='Выберите тип оплаты ..', reply_markup=gen_markup1())
        if callback.data == 'очистить':
            with shelve.open('itog') as db:
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
            a4 = types.InlineKeyboardButton("Назад", callback_data=u'назад1')
            a5 = types.InlineKeyboardButton("Корзина", callback_data=u'корзина')
            markup.add(a1, a2, a3)
            markup.add(a4, a5)
            bot.edit_message_text(chat_id=chat_id, message_id=callback.message.message_id,
                                  text='Хорошо, выберите кол-во копий:', reply_markup=markup)
        if callback.data == 'Ч/Б Печать(распечатка)':  
            price_print = 2.5
            callduty(price_print, callback)
            bot.edit_message_text(chat_id=callback.from_user.id, message_id=callback.message.message_id,
                                  text='Хорошо, выберите кол-во копий', reply_markup=num_copy_markup1())
        if callback.data == 'Печать фото 10х15':
            price_print = 10.0
            callduty(price_print, callback)
            bot.edit_message_text(chat_id=callback.from_user.id, message_id=callback.message.message_id,
                                  text='Хорошо, выберите кол-во копий', reply_markup=num_copy_markup1())
        if callback.data == 'Цветная печать А4':
            price_print = 20.0
            callduty(price_print, callback)
            bot.edit_message_text(chat_id=callback.from_user.id, message_id=callback.message.message_id,
                                  text='Хорошо, выберите кол-во копий', reply_markup=num_copy_markup1())

        if callback.data == "later":
            number = str(random_pool())
            bot.answer_callback_query(callback.id, "Вы выбрали - По факту получения")
            bot.edit_message_text(chat_id=callback.from_user.id, message_id=callback.message.message_id,
                                  text='Супер! Теперь ваш заказ отправлен..\nНомер вашего заказа - ' + number)
            bot.send_message(callback.from_user.id, 'Выберите услугу:', reply_markup=main_menu())
        

            with shelve.open('itog') as db:
                l = []
                for line3 in db.values():
                    line2 = ' '.join(line3)
                    l.append(line2)
                m = '\n'.join(l)


            from_chat_id = -1001302729558
            now = datetime.now()
            time_order = str(f"{now.year}-{now.month}-{now.day}  {now.hour}:{now.minute}")
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
            with shelve.open('itog') as db:
                lst3 = list(db.keys())
                lst = list((filter(lambda x: str(chat_id) in x, lst3)))
                for dd in lst:
                    del db[dd]
        if callback.data == "now":
            bot.answer_callback_query(callback.id, "Вы выбрали - Cейчас в Telegram")
            price = str(user.total_price)
            price1 = user.total_price * 100
            print(price1)
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
    with shelve.open('itog') as db:
        l = []
        for line3 in db.values():
            line2 = ' '.join(line3)
            l.append(line2)
        m = '\n'.join(l)
    from_chat_id = -1001302729558
    now = datetime.now()
    time_order = str(f"{now.year}-{now.month}-{now.day}  {now.hour}:{now.minute}")
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
