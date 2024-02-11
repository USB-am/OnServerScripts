import logging
from telebot import types

from tg_bot.bot import Bot
from .manager import find_else_create_user, update


__BOT = Bot('')


def change_city(message: types.Message) -> None:
	''' Изменить город пользователя '''

	logging.debug('change_city is started')

	if message.text.lower() == 'отмена':
		__BOT.send_message(message.chat.id, 'Отмена смены города.')
		return

	user = find_else_create_user(message)
	old_city = user.city

	update(user, 'city', message.text)

	__BOT.send_message(
		message.chat.id,
		f'Город изменен с {old_city} на {message.text}'
	)
	logging.info(f'{user} changed city from \'{old_city}\' to \'{message.text}\'')
