import logging
from typing import Union, List

from telebot import types
from sqlalchemy.exc import IntegrityError

from . import db, TelegramUser, Station


def find_user(message: types.Message) -> Union[TelegramUser, None]:
	''' Поиск пользователя по message.chat.id '''

	logging.debug(f'[{message.chat.id}] find_user({message.text})')
	user = TelegramUser.query.filter_by(chat_id=message.chat.id).first()

	return user


def create_user(message: types.Message) -> TelegramUser:
	''' Создание пользователя по message.chat.id '''

	logging.debug('create_user function is started')

	username = message.chat.username
	if username is None:
		username = 'Путник'

	try:
		user = TelegramUser(
			chat_id=message.chat.id,
			name=username,
			city='Москва'
		)
		db.session.add(user)
		db.session.commit()
	except IntegrityError:
		db.session.rollback()

		user = TelegramUser(
			chat_id=message.chat.id,
			name='Путник',
			city='Москва'
		)

		db.session.add(user)
		db.session.commit()

	logging.info(f'Created new user [{user.chat_id}] {user.name}')

	return user


def find_else_create_user(message: types.Message) -> TelegramUser:
	''' Поиск пользователя. Если не нашелся - создается '''

	logging.debug('find_else_create_user function is started')

	user = find_user(message)
	if user is None:
		user = create_user(message)

	return user


def update(entry: db.Model, arg: str, value: Union[int, float, str]) -> None:
	''' Обновить запись в БД '''

	logging.debug('update function is started')

	setattr(entry, arg, value)

	db.session.commit()


def find_stations(message: types.Message) -> List[Station]:
	''' Поиск станции '''

	logging.debug('find_stations function is started')

	stations = Station.query.filter_by(title=message.text).all()

	return stations