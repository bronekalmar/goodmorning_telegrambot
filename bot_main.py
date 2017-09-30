# -*- coding: utf-8 -*-

import config
import telebot
from telebot import *
from telebot import types
import logging
import ssl
import datetime
from aiohttp import web
import time
from apscheduler.schedulers.background import BackgroundScheduler

admins = config.LIST_OF_ADMINS
bot = telebot.TeleBot(config.token)
app = web.Application()
# DB to store chat IDs, wishes and other stuff
connection = config.db
#cursor = connection.cursor()
ids = []
scheduler = BackgroundScheduler()
logger = telebot.logger
telebot.logger.setLevel(logging.INFO)
now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

# Process webhook calls
async def handle(request):
    if request.match_info.get('token') == bot.token:
        request_body_dict = await request.json()
        update = telebot.types.Update.de_json(request_body_dict)
        bot.process_new_updates([update])
        return web.Response()
    else:
        return web.Response(status=403)

app.router.add_post('/{token}/', handle)

try:
    with connection.cursor() as cursor:
        connection.ping()
        users_in_sql = "SELECT User_ID from ids"
        cursor.execute(users_in_sql)
        user_id_in_sql = cursor.fetchall()

        for i in range(len(user_id_in_sql)):
            ids.append(user_id_in_sql[i][0])
finally:
    connection.close()

def randomize_wishes():
    try:
        with connection.cursor() as cursor:
            connection.ping()
            # Get random first part of wish
            first_part = "SELECT first_part from wishes where first_part is not NULL ORDER BY RAND()"
            cursor.execute(first_part)
            first_part_result = cursor.fetchone()
            # Get random second part of wish
            second_part = "SELECT second_part from wishes where second_part is not NULL ORDER BY RAND()"
            cursor.execute(second_part)
            second_part_result = cursor.fetchone()
            # Full Randomized wish
            rnd_wish = str(first_part_result[0]) + ", " + str(second_part_result[0]) + "!"
            return rnd_wish
    finally:
        connection.close()



def randomize_addition_answers():
    try:
        with connection.cursor() as cursor:
            connection.ping()
            additional_answer = "SELECT answer from addition_answers ORDER BY RAND()"
            cursor.execute(additional_answer)
            additional_answer_result = cursor.fetchone()
            rnd_answer = additional_answer_result[0]
    finally:
        connection.close()
    return rnd_answer


def randomize_poems():
    try:
        with connection.cursor() as cursor:
            connection.ping()
            poem = "SELECT poem from poems ORDER BY RAND()"
            cursor.execute(poem)
            poem_result = cursor.fetchone()
            rnd_poem = poem_result[0]
            return rnd_poem
    finally:
        connection.close()

# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.send_message(message.chat.id, """\
    Привет! Я бот, который всегда пожелает тебе доброго утра!\
    """)
    try:
        with connection.cursor() as cursor:
            connection.ping()
            if str(message.chat.id) in ids:
                print("Exist! ", message.chat.id)

            else:
                connection.ping()
                sql = "INSERT INTO ids (User_ID) VALUES (%s)"
                cursor.execute(sql, (str(message.chat.id)))
                connection.commit()
                print("Added! ", message.chat.id)
                bot.send_message(admins[0], "Whe have new user! ID: ".format(message.chat.id))
    finally:
        connection.close()

    time.sleep(2)
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('Да!')
    msg = bot.send_message(message.chat.id, 'Ты согласна?', reply_markup=markup)
    bot.register_next_step_handler(msg, process_testing)


def process_testing(message):
    if (message.text == 'Да, давай еще раз') or (message.text == 'Да!'):
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('Проверить')
        msg = bot.send_message(message.chat.id, 'Тогда жми ккнопку', reply_markup=markup)
        bot.register_next_step_handler(msg, process_send_test_message)
    else:
        msg = bot.send_message(message.chat.id, 'Тогда утром не забудь заглянуть в телеграм ;-)')
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('Обязательно!')
        bot.send_message(message.chat.id, 'Ок?', reply_markup=markup)
        bot.register_next_step_handler(msg, daily_send)


@bot.message_handler(commands=['test'])
def process_send_test_message(message):
    bot.send_message(message.chat.id, randomize_wishes())
    bot.send_message(message.chat.id, randomize_addition_answers())
    bot.send_message(message.chat.id, randomize_poems())
    time.sleep(2)
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('Да, давай еще раз', 'Нет, теперь только утром')
    msg = bot.send_message(message.chat.id, 'Еще раз?', reply_markup=markup)
    bot.register_next_step_handler(msg, process_testing)


@bot.message_handler(commands=['append'])
def append(message):
    print("appending in progress by", message.chat.id)
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('first_part', 'second_part')
    markup.add('addition_answer', 'poem')
    msg = bot.send_message(message.chat.id, 'Select which to insert in DB', reply_markup=markup)
    bot.register_next_step_handler(msg, append_selecting)


def append_selecting(message):
    #    bot.send_message(message.chat.id, "Enter your text")

    if message.text == 'first_part':
        print("appending first part")
        msg = bot.send_message(message.chat.id, "Enter \"first_part\"")
        bot.register_next_step_handler(msg, append_first_part)

    elif message.text == 'second_part':
        print("appending second part")
        msg = bot.send_message(message.chat.id, "Enter \"second_part\"")
        bot.register_next_step_handler(msg, append_second_part)

    elif message.text == 'addition_answer':
        print("appending addition answer")
        msg = bot.send_message(message.chat.id, "Enter \"addition_answer\"")
        bot.register_next_step_handler(msg, append_addition_answer)

    elif message.text == 'poem':
        print("appending poem")
        msg = bot.send_message(message.chat.id, "Enter \"append_poem\"")
        bot.register_next_step_handler(msg, append_poem)

    else:
        print("Error in select where to insert data")
        msg = bot.send_message(message.chat.id, "Error in select where to insert data")
        bot.register_next_step_handler(msg, process_send_test_message)


def append_first_part(message):
    try:
        with connection.cursor() as cursor:
            connection.ping()
            sql = "insert INTO wishes (first_part) VALUES (%s)"
            cursor.execute(sql, (message.text))
            connection.commit()
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add('Return')
            msg = bot.send_message(message.chat.id, "Return to testing?", reply_markup=markup)
            bot.register_next_step_handler(msg, process_send_test_message)
    finally:
        connection.close()


def append_second_part(message):
    try:
        with connection.cursor() as cursor:
            connection.ping()
            sql = "insert INTO wishes (second_part) VALUES (%s)"
            cursor.execute(sql, (message.text))
            connection.commit()
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add('Return')
            msg = bot.send_message(message.chat.id, "Return to testing?", reply_markup=markup)
            bot.register_next_step_handler(msg, process_send_test_message)
    finally:
        connection.close()


def append_addition_answer(message):
    try:
        with connection.cursor() as cursor:
            connection.ping()
            sql = "insert INTO addition_answers (answer) VALUES (%s)"
            cursor.execute(sql, (message.text))
            connection.commit()
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add('Return')
            msg = bot.send_message(message.chat.id, "Return to testing?", reply_markup=markup)
            bot.register_next_step_handler(msg, process_send_test_message)
    finally:
        connection.close()


def append_poem(message):
    try:
        with connection.cursor() as cursor:
            connection.ping()
            sql = "insert INTO poems (poem) VALUES (%s)"
            cursor.execute(sql, (message.text))
            connection.commit()
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add('Return')
            msg = bot.send_message(message.chat.id, "Return to testing?", reply_markup=markup)
            bot.register_next_step_handler(msg, process_send_test_message)
    finally:
        connection.close()


def daily_send(message):
    print("done daily_send -- ")
    bot.send_message(admins[0], "end of processing, pending jobs are active {0}".format(now))
    print("testing")


@bot.message_handler(commands=['test_msg'])
def msg(*args):
    bot.send_message(admins[0], "SCHEDULED TASK at {0}".format(now))
    print("SCHEDULED TASK at {0}".format(now))

    for i in ids:
        bot.send_message(i, randomize_wishes())
        time.sleep(10)
        bot.send_message(i, randomize_addition_answers())
        time.sleep(5)
        bot.send_message(i, "И, обязательно, стишок!")
        time.sleep(20)
        bot.send_message(i, randomize_poems())
        print("done msg job to id: ", i, "at time: ", now)
    

# schedule every day send
scheduler.add_job(msg, trigger='cron', hour=6, minute=15)
scheduler.start()

# Remove webhook, it fails sometimes the set if there is a previous webhook
bot.remove_webhook()

# Set webhook
bot.set_webhook(url=config.WEBHOOK_URL_BASE+config.WEBHOOK_URL_PATH,
                certificate=open(config.WEBHOOK_SSL_CERT, 'r'))

# Build ssl context
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.load_cert_chain(config.WEBHOOK_SSL_CERT, config.WEBHOOK_SSL_PRIV)
# test main function

# Start aiohttp server
web.run_app(
    app,
    host=config.WEBHOOK_HOST,
    port=config.WEBHOOK_PORT,
    ssl_context=context,
)
