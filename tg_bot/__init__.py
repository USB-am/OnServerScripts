import logging

from telebot import types

from config import TELEGRAM_TOKEN
from .bot import Bot
from .data_base.manager import find_user, find_else_create_user

_bot = Bot(TELEGRAM_TOKEN)

from .weather import handlers as Weather
from .data_base import handlers as DBHandlers


BUTTONS_TEXT = {
	'change_city': '🚂 Сменить город',
	'show_weather': '☔️ Показать погоду',
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
	change_city_btn = types.KeyboardButton(BUTTONS_TEXT['change_city'])
	from_station_btn = types.KeyboardButton(BUTTONS_TEXT['from_station'])
	to_station_btn = types.KeyboardButton(BUTTONS_TEXT['to_station'])

	markup.add(show_weather_btn)
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

	else:
		_bot.send_message(
			message.from_user.id,
			'Неизвестный запрос.\nВведи что-нибудь нормальное да!'
		)
