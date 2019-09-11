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


TOKEN = input("Input token: ")
proxy_check = input("Has proxy? (y/n) ")
REQUEST_KWARGS = {}

if proxy_check.lower() == 'y':
    proxy_url = input("Input proxy url: ")  # with http://
    REQUEST_KWARGS = {
        'proxy_url': proxy_url
    }

RUSSIAN_FIRST = [
    '1-ый', '2-ой', '3-ий', '4-ый', '5-ый', '6-ой', '7-ой'
]
TIME = [
    '9:00-9:45', '9:50-10:35', '10:45-11:30', '11:50-12:35',
    '12:45-13:30', '13:35-14:20', '14:50-15:35'
]
WEEKDAYS = [
    'Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье'
]
TIMETABLE = [
    ["Всемир. история 23", "Литература 23", "Литература 23", "Алгебра 23",
        "Алгебра 23", "ЛЕКЦИЯ Алгебра 39", "История России 23"],
    ["---", "---", "Физ-ра", "Физ-ра", "Информатика 23/33",
            "Информатика 23/33", "Английский"],
    ["---", "Геометрия 23", "Геометрия 23", "ОБЖ 23",
            "Русский 23/43", "Литература", "Физ прак"],
    ["Английский", "Английский", "Обществознание",
     "ЛЕКЦИЯ Инфа 39", "Физика 23", "Физика 23", "---"],
    ["ЛЕКЦИЯ Анализ 29", "ЛЕКЦИЯ Геом. 29", "Анализ 23", "Анализ 23",
     "История др. мира 23", "Биология 23", "Мат прак 23"],
    ["Физика 23", "Физика 23", "ЛЕКЦИЯ Физика 39",
     "ЛЕКЦИЯ Физика 39", "Химия 46", "---", "---"],
    ["---", "---", "---", "---", "---", "---", "---"],
]
PEOPLE = [
    "Абрамов", "Абросимов", "Акимов", "Борщев", "Буркин", "Голубев",
    "Дубровин", "Занин", "Захарченко", "Карпеев", "Кеба", "Кравчук",
    "Лифарь", "Мацкевич", "Морозов", "Нестеренко", "Орлова", "Пустовалов",
    "Родионов", "Свердлов", "Симонов", "Фролов", "Чинаева",
    "Шайдурова", "Шалагин", "Шуклин"
]
FILE_SAVE = "duty.txt"
PEOPLE_QUEUE = []
MAX_PEOPLE_QUEUE = 20

WRITE_CHANNEL = open(FILE_SAVE, "a+")

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


for x in open(FILE_SAVE, "r+"):
    for word in x.split():
        add_people(word, save=False)


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
    if (len(context.args) < 1) or not (context.args[0].isdigit()):
        context.bot.send_message(
            chat_id=update.message.chat_id, text=ERROR_MSG)
        return
    weekday = max(0, int(context.args[0]) - 1)
    context.bot.send_message(chat_id=update.message.chat_id, text=("Расписание на {}\n<pre>" +
                                                                   get_timetable(weekday) + "</pre>").format(WEEKDAYS[weekday]), parse_mode=telegram.ParseMode.HTML)


@bot_message_actions
def cmd_time(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text="<pre>" +
                             get_time() + "</pre>", parse_mode=telegram.ParseMode.HTML)


@bot_message_actions
def cmd_clear(update, context):
    global LAST_DAY_USAGE

    if LAST_DAY_USAGE == get_date():
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text="Дежурные на сегодня - {0[0]} и {0[1]}.".format(get_last()))
        return
    if get_date().weekday() == 6:
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text="Дядь ты дурак? Сегодня воскресенье")
        return

    FIRST = get_random()
    SECOND = get_random()

    context.bot.send_message(chat_id=update.message.chat_id,
                             text="Поздравялем счастливчиков!\nДежурные на сегодня - {} и {}.".format(FIRST, SECOND))

    LAST_DAY_USAGE = get_date()
    return


def addCommand(updater, name, function, cooldown=5):
    global CMD_COOLDOWN, CMD_LAST_USAGE

    print(function.__qualname__)
    CMD_COOLDOWN[function.__qualname__] = cooldown
    CMD_LAST_USAGE[function.__qualname__] = 0

    updater.dispatcher.add_handler(CommandHandler(name, function))

# print(cmd_today.__name__)

addCommand(updater, ["today"], cmd_today)
addCommand(updater, ["tomorrow"], cmd_tomorrow)
addCommand(updater, ["time"], cmd_time)
addCommand(updater, ["any"], cmd_any)
addCommand(updater, ["clear"], cmd_clear)

updater.start_polling()
logging.info("Bot: {} has started".format(
    str(updater.bot.get_me()['first_name'])))
