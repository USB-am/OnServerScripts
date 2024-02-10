import logging
from telebot import types

from tg_bot.bot import Bot
from .manager import find_user, find_else_create_user, update


__BOT = Bot('')


def change_city(message: types.Message) -> None:
	''' Изменить город пользователя '''

	logging.debug('change_city is started')

	user = find_else_create_user(message)
	old_city = user.city

	update(user, 'city', message.text)

	__BOT.send_message(message.chat.id, f'Город изменен с {old_city} на {message.text}')
