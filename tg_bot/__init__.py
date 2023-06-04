from typing import List

import telebot
from telebot import types

from config import TELEGRAM_TOKEN
from .data_base import db, Station
from .data_base import manager as DBManager
from .weather import get_weather
from .train_schedules import get_schedules


bot = telebot.TeleBot(TELEGRAM_TOKEN)
print('TelegramBot is started!')


@bot.message_handler(commands=['start',])
def start(message: types.Message) -> None:
	''' Обработка команды /start '''

	markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
	geolocation_button = types.KeyboardButton('Сменить город')
	markup.add(geolocation_button)
	schedule_button = types.KeyboardButton('Расписание транспорта')
	markup.add(schedule_button)

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


def ask_from_station(message: types.Message) -> List[Station]:
	stations = []

	def find_stations(station_title: types.Message) -> List[Station]:
		nonlocal stations

		if station_title.text.lower() == 'отмена':
			return

		stations = DBManager.find_stations(station_title)

	from_station_title = bot.reply_to(
		message,
		'Введи название станции "Откуда".\nДля отмены необходимо ввести "Отмена"'
	)
	bot.register_next_step_handler(from_station_title, find_stations)

	return stations


def ask_stations(message: types.Message) -> None:
	from_ = ask_from_station(message)
	print(from_)
	# print(bot.send_message(message.chat.id, from_.title))
	# to = ask_to_station(message)
	# from_ = bot.reply_to(message, 'Введи название станции "Откуда".\nДля отмены необходимо ввести "Отмена"')
	# bot.register_next_step_handler(from_, )