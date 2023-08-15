import schedule
import time
from typing import List
from datetime import datetime, timedelta
from multiprocessing import *

import telebot
from telebot import types

from config import TELEGRAM_TOKEN, MAILING_TIMES
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
	markup.add(types.KeyboardButton('Сменить город'),)
	markup.add(
		types.InlineKeyboardButton('Станция отправления', callback_data='from_'),
		types.InlineKeyboardButton('Станция прибытия', callback_data='to')
	)

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
	elif message.text.lower() == 'станция отправления':
		# ask_station(type_='from')
		s = bot.send_message(message.chat.id, 'Введи название станции:')
		bot.register_next_step_handler(s, select_station)
	elif message.text.lower() == 'станция прибытия':
		# ask_station(type_='to')
		s = bot.send_message(message.chat.id, 'Введи название станции:')
		bot.register_next_step_handler(s, select_station)
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


def ask_station(type_: str) -> None:
	s = bot.send_message(message.chat.id, 'Введи название станции:')
	bot.register_next_step_handler(s, select_station)


def select_station(message: types.Message) -> None:
	found_stations = Station.query.filter_by(title=message.text)

	'''
	markup = types.InlineKeyboardMarkup()
	buttons = [
		types.KeyboardButton(station.title)
		for station in found_stations
	]
	markup.add(*buttons)
	'''

	markup = types.InlineKeyboardMarkup(row_width=1)
	buttons = [
		types.InlineKeyboardButton(text=station.title)
	]
	markup.add(*buttons)

	bot.send_message(message.chat.id, 'Найденные станции:', reply_markup=markup)


def start_timer() -> None:
	schedule_process.start()


def start_schedule() -> None:
	# Today mailing
	for mailing_time in MAILING_TIMES[:-1]:
		schedule.every().day.at(mailing_time).do(
			weather_mailing, date=datetime.now().date()
		)

	# Tomorrow mailing
	schedule.every().day.at(mailing_time).do(
		weather_mailing, date=datetime.now().date() + timedelta(days=1)
	)

	while True:
		schedule.run_pending()
		time.sleep(1)


def weather_mailing(date: datetime.date) -> None:
	for user in TelegramUser.query.all():
		# date = datetime.now().date() + timedelta(days=1)
		weather_message_text = get_weather(user.city, date)
		bot.send_message(user.chat_id, weather_message_text, parse_mode='Markdown')


schedule_process = Process(target=start_schedule, args=())