#import os
from flask import Flask, request
import telebot
import urllib.request as urllib2
TOKEN = ""
#TOKEN = os.environ.get('TOKEN')
bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

class User:
    def __init__(self, link):
        self.link = link
        self.format_file = None
        self.apps = None

    def show_link(self):
        link_desc = (self.link).title()
        return link_desc

    def show_format(self):
        format_doc = (self.format_file).title()
        return format_doc

    def show_apps(self):
        send_apps = (self.apps).title()
        return send_apps

user_dict = {}

@bot.message_handler(commands=['start'])
def handle_start(message):
    user_markup1 = telebot.types.ReplyKeyboardMarkup(True, False)
    user_markup1.row('Копирование', 'Печать(распечатка)')
    user_markup1.row('Сканирование', 'Переплет')
    name = message.from_user.first_name
    bot.send_message(message.chat.id, 'Привет, {}! Рад тебя видеть! Выберите услугу'.format(name), reply_markup=user_markup1)

@bot.message_handler(func=lambda message: message.text == 'Печать(распечатка)')
def info_message(message):
        msg = bot.send_message(message.from_user.id,
                         "Отправьте, пожалуйста, ссылку на файл или сам файл, который нужно распечатать")
        bot.register_next_step_handler(msg, link_text)
        #Должны сохран ссылку

def link_text(message): #лОВИМ url
    chat_id = message.chat.id
    link = message.text
    link_doc = User(link)
    user_dict[chat_id] = link_doc
    keyboard = types.InlineKeyboardMarkup()
    callback_button1 = types.InlineKeyboardButton(text=".pdf", callback_data='pdf')
    callback_button2 = types.InlineKeyboardButton(text='.doc/.docx', callback_data='doc')
    callback_button3 = types.InlineKeyboardButton(text=".cdw", callback_data='cdw')
    callback_button4 = types.InlineKeyboardButton(text=".xls", callback_data='xls')
    keyboard.add(callback_button1, callback_button2, callback_button3, callback_button4)
    msg = bot.send_message(message.chat.id, 'Выберите формат файла',
                     reply_markup=keyboard)
    bot.register_next_step_handler(msg, callback_inline)

@bot.callback_query_handler(func=lambda call: True) #Ловим формат
def callback_inline(call):
        if call.message:
            chat_id = call.from_user.id
            #link_doc = user_dict[chat_id]
            #url = link_doc.show_link().lower()
            if call.data == "pdf":
                format_file = call.data
                format_doc = User(format_file)
                user_dict[chat_id] = format_doc
            if call.data == "doc":
                format_file = call.data
                format_doc = User(format_file)
                user_dict[chat_id] = format_doc
            if call.data == "cdw":
                format_file = call.data
                format_doc = User(format_file)
                user_dict[chat_id] = format_doc
            if call.data == "xls":
                format_file = call.data
                format_doc = User(format_file)
                user_dict[chat_id] = format_doc
            msg = bot.send_message(call.from_user.id, 'Супер! Теперь можете написать примечания к заказу..')
            bot.register_next_step_handler(msg, get_app)

def get_app(message): #Ловим примечания
    chat_id = message.chat.id
    apps = message.text
    user_apps = User(apps)
    user_dict[chat_id] = user_apps
    msg = bot.send_message(message.chat.id, 'Супер! Теперь можете написать примечания к заказу..')
    bot.register_next_step_handler(msg, get_file)

def get_file(message): #Кидаем заказ в канал
    chat_id = message.chat.id #полу4аем
    link_doc = user_dict[chat_id]   #достаем url
    url = link_doc.show_link().lower()
    format_doc = user_dict[chat_id] #достаем формат
    filename = 'file.' + format_doc.show_format().lower()
    #print(filename)
    user_apps = user_dict[chat_id]  #достаем дополнени9
    description = user_apps.show_apps().lower()
    urllib2.urlretrieve(url, filename)
    doc = open(filename, "rb")
    from_chat_id = -1001302729558
    bot.send_document(from_chat_id, doc, caption=url + '\n\n' + description)
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
