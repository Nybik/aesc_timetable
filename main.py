#!/usr/bin/env python3

import logging, telegram, datetime, pytz
from prettytable import PrettyTable
from telegram.ext import Updater, CommandHandler
TOKEN=input("Input token: ")
proxy_check=input("Has proxy? (y/n) ")
REQUEST_KWARGS={}
if proxy_check.lower() == 'y': 
	proxy_url=input("Input proxy url: ") #with http://
	REQUEST_KWARGS={
	    'proxy_url': proxy_url,
	}
RUSSIAN_FIRST=[
	'1-ый', '2-ой', '3-ий', '4-ый', '5-ый', '6-ой', '7-ой'
]
TIME=[
	'9:00-9:45', '9:50-10:35', '10:45-11:30', '11:50-12:35', '12:45-13:30', '13:35-14:20', '14:50-15:35'
]
TIMETABLE=[
	["Всемирная история 23", "Литература 23", "Литература 23", "Алегбра 23", "Алегбра 23", "ЛЕКЦИЯ Алгебра 39", "История России 23"],
	["---", "---", "Физ-ра", "Физ-ра", "Информатика 23/33", "Информатика 23/33", "Английский"],
	["---", "Геометрия 23", "Геометрия 23", "ОБЖ 23", "Русский 23/43", "Литература", "Физ прак"],
	["Английский", "Английский", "Обществознание", "ЛЕКЦИЯ Инфа 39", "Физика 23", "Физика 23", "---"],
	["ЛЕКЦИЯ Анализ 29", "ЛЕКЦИЯ Геом. 29", "Анализ 23", "Анализ 23", "История др. мира 23", "Биология 23", "Мат прак 23"],
	["Физика 23", "Физика 23", "ЛЕКЦИЯ Физика 39", "Физика 39", "Химия 46", "---", "---"],
	["---", "---", "---", "---", "---", "---", "---"],
]
# logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#                      level=logging.INFO)
updater = Updater(token=TOKEN, use_context=True, request_kwargs=REQUEST_KWARGS)
# str = ""
# for i in range(len(TIMETABLE[0 % 7])):
	# str += (RUSSIAN_FIRST[i] + " урок: " + TIMETABLE[0 % 7][i] + "\t\n") 
# print(str)
# exit(0)
def get_day():
	return datetime.datetime.now(pytz.timezone('Europe/Moscow'))

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

# print(get_timetable(0))
# print(get_day())

def cmd_today(update, context):
	print("TRYING TO REPLY cmd_today")
	context.bot.send_message(chat_id=update.message.chat_id, text="<pre>"+get_timetable(get_day().weekday())+"</pre>", parse_mode=telegram.ParseMode.HTML)
	print("REPLAYED cmd_today")

def cmd_tomorrow(update, context):
	print("TRYING TO REPLY cmd_tomorrow")
	context.bot.send_message(chat_id=update.message.chat_id, text="<pre>"+get_timetable(get_day().weekday() + 1)+"</pre>", parse_mode=telegram.ParseMode.HTML)
	print("REPLAYED cmd_tomorrow")

def cmd_time(update, context):
	print("TRYING TO REPLY cmd_time")
	context.bot.send_message(chat_id=update.message.chat_id, text="<pre>"+get_time()+"</pre>", parse_mode=telegram.ParseMode.HTML)
	print("REPLAYED cmd_time")

# def add_cmd(dispatcher, cmd_name, cmd_func):
# 	dispatcher.add_handler(CommandHandler(cmd_name, cmd_func))

def go(updater):
	updater.start_polling()

updater.dispatcher.add_handler(CommandHandler("today", cmd_today))
updater.dispatcher.add_handler(CommandHandler("tomorrow", cmd_tomorrow))
updater.dispatcher.add_handler(CommandHandler("time", cmd_time))
updater.start_polling()
print("BOT Started")
# logging.info("Started bot")
# add_cmd(dispatcher, "hello", cmd_hello)
# go(updater)
# dispatcher.add_handler(CommandHandler())
# print(get_day())
# updater.start_polling()
# print(bot.get_me())
