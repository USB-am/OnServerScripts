import re
import logging

from telebot import types

from config import TELEGRAM_TOKEN
from .bot import Bot
from .data_base.manager import find_user, find_else_create_user

_bot = Bot(TELEGRAM_TOKEN)

from .weather import handlers as Weather
from .routes import handlers as Routes
from .data_base import handlers as DBHandlers


BUTTONS_TEXT = {
	'show_weather': '☔️ Показать погоду',
	'show_schedules': '🎟 Показать расписание',
	'change_city': '🚂 Сменить город',
	'from_station': '👉 Станция\nотправления',
	'to_station': '👈 Станция\nприбытия',
}


def start_bot() -> None:
	''' Запустить бота '''

	logging.info('Telegram bot is started!')
	_bot.polling(none_stop=True, interval=0)


def stop_bot() -> None:
	''' Остановить бота '''
	_bot.stop_bot()
	logging.warning('Telegram bot is stoped!')


@_bot.message_handler(commands=['start'])
def start(message: types.Message) -> None:
	''' Обработка команды /start '''

	markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

	# Создание кнопок чата
	show_weather_btn = types.KeyboardButton(BUTTONS_TEXT['show_weather'])
	show_schedules_btn = types.KeyboardButton(BUTTONS_TEXT['show_schedules'])
	change_city_btn = types.KeyboardButton(BUTTONS_TEXT['change_city'])
	from_station_btn = types.KeyboardButton(BUTTONS_TEXT['from_station'])
	to_station_btn = types.KeyboardButton(BUTTONS_TEXT['to_station'])

	markup.add(show_weather_btn)
	markup.add(show_schedules_btn)
	markup.add(change_city_btn)
	markup.add(from_station_btn, to_station_btn)

	# Создание пользователя, если его не было
	user = find_else_create_user(message)

	# Вернуть сообщение с приветствием
	_bot.send_message(
		message.from_user.id,
		f'Ну привет, {user.name}!', reply_markup=markup
	)


@_bot.message_handler(content_types=['text'])
def get_text_messages(message) -> None:
	''' Обработка поступающего текста '''

	msg = message.text.lower().strip()

	if msg == BUTTONS_TEXT['show_weather'].lower():
		weather_text = Weather.get_weather(message)

		if weather_text is None:
			_bot.send_message(
				message.from_user.id,
				'Произошла ошибка при попытке запроса погоды.\nПопробуй позже 😄'
			)
			logging.warning('Weather parser encountered an error.')
		else:
			_bot.send_message(
				message.from_user.id,
				weather_text,
				parse_mode='Markdown'
			)
			logging.info(f'Send {find_user(message)} current weather.')

	elif msg == BUTTONS_TEXT['change_city'].lower():
		session = _bot.reply_to(message,
			'Введи название города.\nДля отмены необходимо ввести "Отмена"'
		)
		_bot.register_next_step_handler(session, DBHandlers.change_city)

	elif msg == BUTTONS_TEXT['show_schedules'].lower():
		_bot.send_message(
			message.from_user.id,
			Routes.get_routes(message),
			parse_mode='Markdown'
		)

	elif msg == BUTTONS_TEXT['from_station'].lower():
		session = _bot.reply_to(message,
			'Введи название Станции отправления.\nДля отмены необходимо ввести "Отмена"'
		)
		_bot.register_next_step_handler(session, Routes.change_from_station)

	elif msg == BUTTONS_TEXT['to_station'].lower():
		session = _bot.reply_to(message,
			'Введи название Станции прибытия.\nДля отмены необходимо ввести "Отмена"'
		)
		_bot.register_next_step_handler(session, Routes.change_to_station)

	else:
		_bot.send_message(
			message.from_user.id,
			'Неизвестный запрос.\nВведи что-нибудь нормальное да!'
		)


@_bot.callback_query_handler(func=lambda call: True)
def callback_query(call: types.CallbackQuery) -> None:
	''' Обработка нажатия InlineKeyboardButton's '''

	if re.search(r's[\d]+', call.data) or re.search(r'c[\d]+', call.data):
		if 'отправления' in call.message.text:
			DBHandlers.change_from_station(call)
		elif 'прибытия' in call.message.text:
			DBHandlers.change_to_station(call)
