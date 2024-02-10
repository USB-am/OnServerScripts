import logging

from telebot import types

from config import TELEGRAM_TOKEN
from .bot import Bot
from .data_base.manager import find_else_create_user

_bot = Bot(TELEGRAM_TOKEN)

from .weather import start
from .data_base import handlers as DBHandlers


BUTTONS_TEXT = {
	'change_city': 'Сменить город',
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

	# Создание кнопок чата
	markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
	change_city_btn = types.KeyboardButton(BUTTONS_TEXT['change_city'])
	markup.add(change_city_btn)

	# Создание пользователя, если его не было
	user = find_else_create_user(message)

	# Вернуть сообщение с приветствием
	_bot.send_message(message.from_user.id, f'Ну привет, {user.name}!', reply_markup=markup)


@_bot.message_handler(content_types=['text'])
def get_text_messages(message) -> None:
	''' Обработка поступающего текста '''

	msg = message.text.lower().strip()

	if msg == BUTTONS_TEXT['change_city'].lower():
		session = _bot.reply_to(
			message,
			'Введи название города.\nДля отмены необходимо ввести "Отмена"')
		_bot.register_next_step_handler(session, DBHandlers.change_city)
