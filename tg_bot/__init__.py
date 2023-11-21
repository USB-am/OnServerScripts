import time
from typing import List
from datetime import datetime, timedelta
from multiprocessing import *
from enum import Enum

import schedule
import telebot
from telebot import types

from config import TELEGRAM_TOKEN, MAILING_TIMES
from .data_base import db, Station, TelegramUser
from .data_base import manager as DBManager
from .weather import get_weather
# from .train_schedules import get_schedules
from .train_schedules import TRANSPORT_EMOJIES, TYPES_EMOJIES


bot = telebot.TeleBot(TELEGRAM_TOKEN)
print('TelegramBot is started!')


class StationStatus(Enum):
	from_ = 'станция отправления'
	to = 'станция прибытия'


@bot.message_handler(commands=['start',])
def start(message: types.Message) -> None:
	''' Обработка команды /start '''

	markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
	markup.add(types.KeyboardButton('Сменить город'),)
	markup.add(
		types.InlineKeyboardButton(StationStatus.from_.value.capitalize()),#, callback_data=StationStatus.from_),
		types.InlineKeyboardButton(StationStatus.to.value.capitalize()),#, callback_data=StationStatus.to)
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
	elif message.text.lower() == StationStatus.from_.value:
		s = bot.send_message(message.chat.id, 'Введи название станции:')
		bot.register_next_step_handler(s, select_station, StationStatus.from_)
	elif message.text.lower() == StationStatus.to.value:
		s = bot.send_message(message.chat.id, 'Введи название станции:')
		bot.register_next_step_handler(s, select_station, StationStatus.to)
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
	bot.register_next_step_handler(s, select_station, type_)


def select_station(message: types.Message, type_: str) -> None:
	found_stations = Station.query.filter(Station.title.like(f'%{message.text}%'))\
		.order_by(Station.transport, Station.title).all()

	markup = types.InlineKeyboardMarkup(row_width=1)
	buttons = []
	for station in found_stations:
		emj = TRANSPORT_EMOJIES.get(station.transport, '❓')
		geo = getattr(station, 'settlement', getattr(station, 'region', getattr(station, 'country', '')))
		geo = f' ({geo})' if geo else ''
		t = TYPES_EMOJIES.get(station.type, '')
		btn_text = f'{emj}{t}{geo} {station.title}'
		btn = types.InlineKeyboardButton(text=btn_text, callback_data=f'{type_.value}~{station.yandex_code}')
		buttons.append(btn)
	markup.add(*buttons)

	s = bot.send_message(message.chat.id, 'Найденные станции:', reply_markup=markup)
	bot.register_next_step_handler(s, change_station, type_)


@bot.callback_query_handler(func=lambda call: True)
def change_station(call: types.CallbackQuery) -> None:
	t, data = call.data.split('~')
	if t == StationStatus.from_.value:
		bot.send_message(call.message.chat.id, f'Тыкнута станция отправления "{data}"')
	elif t == StationStatus.to.value:
		bot.send_message(call.message.chat.id, f'Тыкнута станция прибытия "{data}"')


def start_timer() -> None:
	schedule_process.start()


def start_schedule() -> None:
	# Today mailing
	for mailing_time in MAILING_TIMES[:-1]:
		schedule.every().day.at(mailing_time).do(
			weather_mailing, date=datetime.now().date()
		)

	# Tomorrow mailing
	schedule.every().day.at(MAILING_TIMES[-1]).do(
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