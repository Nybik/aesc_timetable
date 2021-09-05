#!/usr/bin/env python3

import logging
import os
import datetime
import pytz
import telegram
import random
from functools import wraps
from time import time
from prettytable import PrettyTable
from telegram.ext import Updater, CommandHandler


def get_day():
    return datetime.datetime.now(pytz.timezone('Europe/Moscow'))

def get_date():
    return get_day().date()

def get_weekday():
    return get_day().get_weekday()


TOKEN = os.environ.get('TOKEN')
# proxy_check = input("Has proxy? (y/n) ")
REQUEST_KWARGS = {}

# if proxy_check.lower() == 'y':
#     proxy_url = input("Input proxy url: ")  # with http://
#     REQUEST_KWARGS = {
#         'proxy_url': proxy_url
#     }
llinal_link = "https://zoom.us/j/93730511689?pwd=M1I1UTZRT1p1bjJIWk1SeG9hQWZEUT09"
lcalc_link = "https://zoom.us/j/91788164166"
slinear_link = "https://zoom.us/j/98331733150?pwd=MWpaMjBHT3VkYW1obldHSXVXSytFdz09"
RUSSIAN_FIRST = [
    '1-ый', '2-ой', '3-ий', '4-ый', '5-ый', '6-ой', '7-ой'
]
TIME = [
    '9:30-10:50', '11.10-12.30', '13.00-14.20', '14.40-16.00', 
    '16.20-17.40', '18.10-19.30', '19.40-21.00'
]
WEEKDAYS = [
    'Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье'
]
TIMETABLE = [
    ["Англ", f"<a href={llinal_link}>(Л) Линал</a>", f"<a href={lcalc_link}>(Л) Матан</a>", f"<a href={slinear_link}>(С) Линал</a>"],
    ["(Л) ОИМП", "(Л) Дискретка", "---", "---", "---", "---", "---"],
    ["(С+) ОИМП 213-1", "(С+) Дискретка", "(С) Матан", "---", "Англ", "Англ", "---"],
    ["(Л) ОИМП", "(С) ОИМП 213-2", "(С) ОИМП 213-2", "---", "---", "---", "---"],
    ["(С+) Оимп 231-1", "(С+) Экономика", "---", "---", "Англ", "Англ", "---"],
    ["---", "---", "---", "---", "---", "---", "---"],
    ["---", "---", "---", "---", "---", "---", "---"],
]
for i in range(len(TIMETABLE)):
    while len(TIMETABLE[i]) > 1:
        if TIMETABLE[i][-1] == "---":
            del TIMETABLE[i][-1]
        else:
            break

ERROR_MSG = 'Неверно указаны параметры для команды'
CMD_COOLDOWN = {}
CMD_LAST_USAGE = {}

logging.basicConfig(format='%(asctime)s - %(name)s - %(message)s',
                    level=logging.INFO)

updater = Updater(token=TOKEN, use_context=True, request_kwargs=REQUEST_KWARGS)

def bot_message_actions(func):
    global CMD_LAST_USAGE
    name = func.__qualname__

    def set_chat_action(update, context):
        context.bot.send_chat_action(
            chat_id=update.effective_message.chat_id, action=telegram.ChatAction.TYPING)

    def has_cooldown():
        return time() - CMD_LAST_USAGE[name] <= CMD_COOLDOWN[name]

    @wraps(func)
    def set_main_action(update, context, *args, **kwargs):
        logging.info("Trying to reply to message: {}".format(
            update.message.text))

        if has_cooldown():
            logging.info("Couldn't reply to message: {} due to cooldown".format(
                update.message.text, update))
            return lambda: None

        set_chat_action(update, context)

        result = func(update, context, *args, **kwargs)
        CMD_LAST_USAGE[name] = time()

        logging.info("Replied to message: {}".format(
            update.message.text, update))
        return result

    return set_main_action


def get_timetable(weekday):
    t = PrettyTable(['№', "Урок"])
    for i in range(len(TIMETABLE[weekday % 7])):
        t.add_row([str(i + 1), TIMETABLE[weekday % 7][i]])
    return str(t)

def get_time_timetable(weekday):
    t = PrettyTable(['Время', "Урок"])
    for i in range(len(TIMETABLE[weekday % 7])):
        t.add_row([TIME[i], TIMETABLE[weekday % 7][i]])
    return str(t)

def get_time():
    t = PrettyTable(['№', "Время"])
    for i in range(len(TIME)):
        t.add_row([str(i + 1), TIME[i]])
    return str(t)

def reply(update, context, msg):
    context.bot.send_message(chat_id=update.message.chat_id, text=msg, parse_mode=telegram.ParseMode.HTML)

@bot_message_actions
def cmd_today(update, context):
    reply(update, context, "<pre>{}<pre>".format(get_timetable(get_weekday())))

@bot_message_actions
def cmd_tomorrow(update, context):
    reply(update, context, "<pre>{}<pre>".format(get_timetable(get_weekday() + 1)))

@bot_message_actions
def cmd_any(update, context):

    valid_arg = {WEEKDAYS[i].lower() : i for i in range(len(WEEKDAYS))}
    valid_arg.update({str(i + 1) : i for i in range(0, 7)})

    if (len(context.args) < 1):
        context.bot.send_message(
            chat_id=update.message.chat_id, text=ERROR_MSG)
        return

    if context.args[0].lower() not in valid_arg:
        context.bot.send_message(
            chat_id=update.message.chat_id, text=ERROR_MSG)
        return

    weekday = max(0, valid_arg[context.args[0].lower()])

    reply(update, context, "Расписание на {}\n<pre>{}</pre>".format(WEEKDAYS[weekday], get_timetable(weekday)))

@bot_message_actions
def cmd_time(update, context):
    reply(update, context, "<pre>{}<pre>".format(get_time()))

@bot_message_actions
def cmd_time_today(update, context):
    reply(update, context, "<pre>{}<pre>".format(get_time_timetable(get_weekday())))

@bot_message_actions
def cmd_time_tomorrow(update, context):
    reply(update, context, "<pre>{}<pre>".format(get_time_timetable(get_weekday() + 1)))

@bot_message_actions
def cmd_time_any(update, context):

    valid_arg = {WEEKDAYS[i].lower() : i for i in range(len(WEEKDAYS))}
    valid_arg.update({str(i + 1) : i for i in range(0, 7)})

    if (len(context.args) < 1):
        context.bot.send_message(
            chat_id=update.message.chat_id, text=ERROR_MSG)
        return

    if context.args[0].lower() not in valid_arg:
        context.bot.send_message(
            chat_id=update.message.chat_id, text=ERROR_MSG)
        return

    weekday = max(0, valid_arg[context.args[0].lower()])

    reply(update, context, "Расписание на {}\n<pre>{}</pre>".format(WEEKDAYS[weekday], get_time_timetable(weekday)))

def addCommand(updater, name, function, cooldown=5):
    global CMD_COOLDOWN, CMD_LAST_USAGE

    print(function.__qualname__)
    CMD_COOLDOWN[function.__qualname__] = cooldown
    CMD_LAST_USAGE[function.__qualname__] = 0

    updater.dispatcher.add_handler(CommandHandler(name, function))

addCommand(updater, ["today"], cmd_today)
addCommand(updater, ["tomorrow"], cmd_tomorrow)
addCommand(updater, ["time"], cmd_time)
addCommand(updater, ["any"], cmd_any)
addCommand(updater, ["ttoday"], cmd_time_today)
addCommand(updater, ["ttomorrow"], cmd_time_tomorrow)
addCommand(updater, ["tany"], cmd_time_any)

updater.start_polling()
logging.info("Bot: {} has started".format(
    str(updater.bot.get_me()['first_name'])))
