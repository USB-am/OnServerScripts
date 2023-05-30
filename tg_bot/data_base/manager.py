from typing import Union

from . import TelegramUser


def find_user(message) -> Union[TelegramUser, None]:
	''' Поиск пользователя по message.chat.id '''

	user = TelegramUser.query.filter_by(chat_id=message.chat.id)

	return user


def create_user(message) -> TelegramUser:
	''' Создание пользователя по message.chat.id '''

	user = TelegramUser(chat_id=message.chat.id, name=message.chat.username)

	return user


def find_else_create_user(message) -> TelegramUser:
	''' Поиск пользователя. Если не нашелся - создается '''

	user = find_user(message)
	if user is None:
		user = create_user(message)

	return user