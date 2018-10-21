import os
from flask import Flask, request
import telebot
import urllib.request
TOKEN = "696434286:AAGtH9kExLEAiX4m1eUl2CyM1MBkUmcqWco"
#TOKEN = os.environ.get('TOKEN')
bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)


@bot.message_handler(commands=['start'])
def handle_start(message):
    user_markup1 = telebot.types.ReplyKeyboardMarkup(True, False)
    user_markup1.row('Копирование', 'Печать(распечатка)')
    user_markup1.row('Сканирование', 'Переплет')
    name = message.from_user.first_name
    bot.send_message(message.chat.id, 'Привет, {}! Рад тебя видеть!'.format(name), reply_markup=user_markup1)

@bot.message_handler(func=lambda message:True, content_types=['text'])
def info_message(message):
    if message.text == "Печать(распечатка)":
        bot.send_message(message.from_user.id,
                         "Отправьте, пожалуйста, ссылку на файл или сам файл, который нужно распечатать")
    elif 'https:' in message.text:
        url = message.text
        filename = 'filename.doc'
        urllib.request.urlretrieve(url, filename)
        doc = open(filename, "rb")
        from_chat_id = -1001302729558
        bot.send_document(from_chat_id, doc, caption="сюда запишу кол-во страниц")
        doc.close()
        bot.send_message(message.from_user.id, 'Супер, теперь напишите ньюансы при распечатке: время, кол-во страниц')
    else:#пересылает текст смс юзера в канал
        chat_id = message.from_user.id
        message_id = message.message_id
        from_chat_id = -1001302729558
        bot.forward_message(from_chat_id, chat_id, message_id)

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
