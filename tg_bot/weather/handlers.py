import logging
from telebot import types

from tg_bot.bot import Bot
from .api import parse_weather
from tg_bot.data_base.manager import find_else_create_user


__BOT = Bot('')


def get_weather(message: types.Message) -> str:
	''' Возвращет погоду в городе пользователя '''

	logging.debug(f'get_weather is started')

	user = find_else_create_user(message)
	weather = parse_weather(user.city)

	return 'Вроде норм'
