import telebot
import os
from telebot import types
import urllib.request as urllib2
from flask import Flask, request
bot = telebot.Telebot('')
server = Flask(__name__)




@bot.message_handler(commands=['start'])
def handle_start(message):
    user_markup1 = telebot.types.ReplyKeyboardMarkup(True, False)
    user_markup1.row('Копирование', 'Печать(распечатка)')
    user_markup1.row('Сканирование', 'Переплет')
    name = message.from_user.first_name
    bot.send_message(message.chat.id, 'Привет, {}! Рад тебя видеть! Выберите услугу'.format(name), reply_markup=user_markup1)

user_dict = set()

@bot.message_handler(func=lambda message: message.text == 'Печать(распечатка)')
def info_message(message):
        msg = bot.send_message(message.from_user.id,
                         "Отправьте, пожалуйста, ссылку на файл или сам файл, который нужно распечатать")
        bot.register_next_step_handler(msg, link_text)
        #Должны сохран ссылку

def link_text(message):
    link = message.text
    a = user_dict
    a.add(link)
    keyboard = types.InlineKeyboardMarkup()
    callback_button1 = types.InlineKeyboardButton(text=".pdf", callback_data='pdf')
    callback_button2 = types.InlineKeyboardButton(text='.doc/.docx', callback_data='doc')
    callback_button3 = types.InlineKeyboardButton(text=".cdw", callback_data='cdw')
    callback_button4 = types.InlineKeyboardButton(text=".xls", callback_data='xls')
    keyboard.add(callback_button1, callback_button2, callback_button3, callback_button4)
    msg = bot.send_message(message.chat.id, 'Выберите формат файла',
                     reply_markup=keyboard)
    bot.register_next_step_handler(msg, callback_inline)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
        if call.message:
            user = user_dict
            if call.data == "pdf":
                filename = 'file.pdf'
                urllib2.urlretrieve(user, filename) #user = url
                doc = open(filename, "rb")
                from_chat_id = -1001302729558
                bot.send_document(from_chat_id, doc, caption="сюда запишу кол-во страниц")
                doc.close()
                bot.send_message(call.from_user.id,
                                 "Отправьте, пожалуйста, ссылку на файл или сам файл, который нужно распечатать")
            if call.data == "doc":
                filename = 'file.doc'
                urllib2.urlretrieve(user, filename)
                doc = open(filename, "rb")
                from_chat_id = -1001302729558
                bot.send_document(from_chat_id, doc, caption="сюда запишу кол-во страниц")
                doc.close()
            if call.data == "cdw":
                filename = 'file.cdw'
                urllib2.urlretrieve(user, filename)
                doc = open(filename, "rb")
                from_chat_id = -1001302729558
                bot.send_document(from_chat_id, doc, caption="сюда запишу кол-во страниц")
                doc.close()
            if call.data == "xls":
                filename = 'file.xls'
                urllib2.urlretrieve(user, filename)
                doc = open(filename, "rb")
                from_chat_id = -1001302729558
                bot.send_document(from_chat_id, doc, caption="сюда запишу кол-во страниц")
                doc.close()

@bot.message_handler(content_types=['document'])
def handle_text(message):
    from_chat_id = -1001302729558
    chat_id = message.from_user.id
    message_id = message.message_id
    bot.forward_message(from_chat_id, chat_id, message_id)
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
