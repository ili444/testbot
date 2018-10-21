import os
from flask import Flask, request
import telebot
import urllib.request
TOKEN = "696434286:AAGtH9kExLEAiX4m1eUl2CyM1MBkUmcqWco"
#TOKEN = os.environ.get('TOKEN')
bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

user_dict = {}


class User:
    def __init__(self, name):
        self.name = name
        self.age = None
        self.sex = None


# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    msg = bot.reply_to(message, """\
Hi there, I am Example bot.
What's your name?
""")
    bot.register_next_step_handler(msg, process_name_step)


def process_name_step(message):
    try:
        chat_id = message.chat.id
        name = message.text
        user = User(name)
        user_dict[chat_id] = user
        msg = bot.reply_to(message, 'How old are you?')
        bot.register_next_step_handler(msg, process_age_step)
    except Exception as e:
        bot.reply_to(message, 'oooops')


def process_age_step(message):
    try:
        chat_id = message.chat.id
        age = message.text
        if not age.isdigit():
            msg = bot.reply_to(message, 'Age should be a number. How old are you?')
            bot.register_next_step_handler(msg, process_age_step)
            return
        user = user_dict[chat_id]
        user.age = age
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('Male', 'Female')
        msg = bot.reply_to(message, 'What is your gender', reply_markup=markup)
        bot.register_next_step_handler(msg, process_sex_step)
    except Exception as e:
        bot.reply_to(message, 'oooops')


def process_sex_step(message):
    try:
        chat_id = message.chat.id
        sex = message.text
        user = user_dict[chat_id]
        if (sex == u'Male') or (sex == u'Female'):
            user.sex = sex
        else:
            raise Exception()
        bot.send_message(chat_id, 'Nice to meet you ' + user.name + '\n Age:' + str(user.age) + '\n Sex:' + user.sex)
    except Exception as e:
        bot.reply_to(message, 'oooops')


# Enable saving next step handlers to file "./.handlers-saves/step.save".
# Delay=2 means that after any change in next step handlers (e.g. calling register_next_step_handler())
# saving will hapen after delay 2 seconds.
bot.enable_save_next_step_handlers(delay=2)

# Load next_step_handlers from save file (default "./.handlers-saves/step.save")
# WARNING It will work only if enable_save_next_step_handlers was called!
bot.load_next_step_handlers()

"""
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
"""


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
