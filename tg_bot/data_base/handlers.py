from telebot import types

from tg_bot.bot import Bot
from .manager import find_else_create_user, update


__BOT = Bot('')


def change_city(message: types.Message) -> None:
	''' Изменить город пользователя '''

	user = find_else_create_user(message)

	old_city = user.city
	update(user, 'city', message.text)

	__BOT.send_message(message.chat.id, f'Город изменен с {old_city} на {message.text}')
