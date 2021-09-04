#!/usr/bin/env python3

import logging
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


TOKEN = "1980205298:AAEGbdS-Z9ooDFm9Sd736zcV7BWF8aoMY00"
# proxy_check = input("Has proxy? (y/n) ")
REQUEST_KWARGS = {}

# if proxy_check.lower() == 'y':
#     proxy_url = input("Input proxy url: ")  # with http://
#     REQUEST_KWARGS = {
#         'proxy_url': proxy_url
#     }

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
    ["Англ", "Линал лекция", "Матан лекция", "Линал семинар", "---", "---", "---"],
    ["ОИМП лекция", "Дискретка лекция", "---", "---", "---", "---", "---"],
    ["ОИМП очно", "Дискретка очно", "Матан очно", "---", "Англ", "Англ", "---"],
    ["ОИМП лекция", "(213-2) ОИМП", "(213-2) ОИМП", "---", "---", "---", "---"],
    ["(213-1) Оимп очно", "Экономика", "---", "---", "Англ", "Англ", "---"],
    ["---", "---", "---", "---", "---", "---", "---"],
    ["---", "---", "---", "---", "---", "---", "---"],
]
for i in range(len(TIMETABLE)):
    while len(TIMETABLE[i]) > 1:
        if TIMETABLE[i][-1] == "---":
            del TIMETABLE[i][-1]
        else:
            break
# PEOPLE = [
#     "Абрамов", "Абросимов", "Акимов", "Борщев", "Буркин", "Голубев",
#     "Дубровин", "Занин", "Захарченко", "Карпеев", "Кеба", "Кравчук",
#     "Лифарь", "Мацкевич", "Морозов", "Нестеренко", "Орлова", "Пустовалов",
#     "Родионов", "Свердлов", "Симонов", "Фролов", "Чинаева",
#     "Шайдурова", "Шалагин", "Шуклин"
# ]
# FILE_SAVE = "duty.txt"
# PEOPLE_QUEUE = []
# MAX_PEOPLE_QUEUE = 20

# WRITE_CHANNEL = open(FILE_SAVE, "a+")

ERROR_MSG = 'Неверно указаны параметры для команды'
CMD_COOLDOWN = {}
CMD_LAST_USAGE = {}

LAST_DAY_USAGE = get_date() - datetime.timedelta(days=1)

logging.basicConfig(format='%(asctime)s - %(name)s - %(message)s',
                    level=logging.INFO)
updater = Updater(token=TOKEN, use_context=True, request_kwargs=REQUEST_KWARGS)


def arrange_queue():
    while len(PEOPLE_QUEUE) > MAX_PEOPLE_QUEUE:
        PEOPLE_QUEUE.pop(0)


def add_people(name, save=True):
    PEOPLE_QUEUE.append(name)
    arrange_queue()
    if save:
        WRITE_CHANNEL.write(name + " ")
        WRITE_CHANNEL.flush()
    return name


def get_random():
    return add_people(random.sample(set(PEOPLE) - set(PEOPLE_QUEUE), 1)[0])


def get_last():
    return PEOPLE_QUEUE[-2:]


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


@bot_message_actions
def cmd_today(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text="<pre>" + get_timetable(
        get_day().weekday()) + "</pre>", parse_mode=telegram.ParseMode.HTML)


@bot_message_actions
def cmd_tomorrow(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text="<pre>" + get_timetable(
        get_day().weekday() + 1) + "</pre>", parse_mode=telegram.ParseMode.HTML)


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
    context.bot.send_message(chat_id=update.message.chat_id, text=("Расписание на {}\n<pre>" +
                                                                   get_timetable(weekday) + "</pre>").format(WEEKDAYS[weekday]), parse_mode=telegram.ParseMode.HTML)


@bot_message_actions
def cmd_time(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text="<pre>" +
                             get_time() + "</pre>", parse_mode=telegram.ParseMode.HTML)

@bot_message_actions
def cmd_time_today(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text="<pre>" + get_time_timetable(
        get_day().weekday()) + "</pre>", parse_mode=telegram.ParseMode.HTML)

@bot_message_actions
def cmd_time_tomorrow(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text="<pre>" + get_time_timetable(
        get_day().weekday() + 1) + "</pre>", parse_mode=telegram.ParseMode.HTML)

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
    context.bot.send_message(chat_id=update.message.chat_id, text=("Расписание на {}\n<pre>" +
                                                                   get_time_timetable(weekday) + "</pre>").format(WEEKDAYS[weekday]), parse_mode=telegram.ParseMode.HTML)

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
addCommand(updater, ["t_today"], cmd_time_today)
addCommand(updater, ["t_tomorrow"], cmd_time_tomorrow)
addCommand(updater, ["t_any"], cmd_time_any)

updater.start_polling()
logging.info("Bot: {} has started".format(
    str(updater.bot.get_me()['first_name'])))
