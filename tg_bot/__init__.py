import schedule
import time
from typing import List
from datetime import datetime, timedelta
from multiprocessing import *

import telebot
from telebot import types

from config import TELEGRAM_TOKEN, MAILING_TIME
from .data_base import db, Station, TelegramUser
from .data_base import manager as DBManager
from .weather import get_weather
# from .train_schedules import get_schedules


bot = telebot.TeleBot(TELEGRAM_TOKEN)
print('TelegramBot is started!')


@bot.message_handler(commands=['start',])
def start(message: types.Message) -> None:
	''' Обработка команды /start '''

	markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
	geolocation_button = types.KeyboardButton('Сменить город')
	markup.add(geolocation_button)
	# schedule_button = types.KeyboardButton('Расписание транспорта')
	# markup.add(schedule_button)
	# print(dir(message.chat))
	# print(message.chat.first_name)
	# print(message.chat.last_name)

	DBManager.find_else_create_user(message)

	bot.send_message(
		message.chat.id,
		f'Привет, {message.chat.username}!',
		reply_markup=markup
	)


@bot.message_handler(commands=['help',])
def help(message: types.Message):
	''' Обработка команды /help '''
	bot.send_message(message.chat.id, f'Доступные команды:\nПодгода:'
		+'/weather <название города>\n'
		+'Сменить город - для получения рассылки погоды в другом городе'
	)


@bot.message_handler(commands=['weather',])
def send_weather(message: types.Message) -> None:
	try:
		_, city = message.text.split(maxsplit=1)
	except ValueError as exc:
		bot.send_message(
			message.chat.id,
			'Некорректный запрос!\n/weather <название города>',
			parse_mode='Markdown'
		)
		return

	bot.send_message(message.chat.id, get_weather(city), parse_mode='Markdown')


@bot.message_handler(content_types=['text',])
def text_reception(message: types.Message) -> None:
	''' Обработка поступающего текста '''

	if message.text.lower() == 'сменить город':
		s = bot.reply_to(message, 'Введи название города.\nДля отмены необходимо ввести "Отмена"')
		bot.register_next_step_handler(s, change_city)
	elif message.text.lower() == 'расписание транспорта':
		ask_stations(message)
	else:
		bot.send_message(message.chat.id, 'Некорректный запрос!')


def change_city(message: types.Message) -> None:
	user = DBManager.find_user(message)
	if user is None:
		bot.send_message(message.chat.id, 'Для доступа к смене города необходимо написать команду /start.')
		return
	if message.text.lower() == 'отмена':
		bot.send_message(message.chat.id, 'Отмена смены города.')
		return

	old_city = user.city
	DBManager.update(user, 'city', message.text)

	bot.send_message(message.chat.id, f'Город изменен с "{old_city}" на "{message.text}"')


def ask_stations(message: types.Message) -> None:
	markup = types.InlineKeyboardMarkup()

	unique_country_stations = Station.query.distinct(Station.country)\
		.group_by(Station.country).all()
	countries = [station.country for station in unique_country_stations]
	for country in countries:
		markup.add(types.InlineKeyboardButton(country, callback_data='country'))

	bot.send_message(message.chat.id, 'Выбери страну:', reply_markup=markup)


def start_timer() -> None:
	schedule_process.start()


def start_schedule() -> None:
	schedule.every().day.at(MAILING_TIME).do(weather_mailing)

	while True:
		schedule.run_pending()
		time.sleep(1)


def weather_mailing() -> None:
	for user in TelegramUser.query.all():
		tomorrow_date = datetime.now().date() + timedelta(days=1)
		weather_message_text = get_weather(user.city, tomorrow_date)
		bot.send_message(user.chat_id, weather_message_text, parse_mode='Markdown')


schedule_process = Process(target=start_schedule, args=())