import logging
from telebot import types

from tg_bot.bot import Bot
from .manager import find_else_create_user, update


__BOT = Bot('')


def __change_value(message: types.Message, attribute: str,
                  success_text: str, cancel_text: str) -> None:
	''' Абстрактная функция изменения значения в БД '''

	if message.text.lower() == 'отмена':
		__BOT.send_message(message.chat.id, cancel_text)
		return

	user = find_else_create_user(message)
	old_value = getattr(user, attribute)

	update(user, attribute, message.text)

	__BOT.send_message(
		message.chat.id,
		success_text.format(old_value=old_value, new_value=message.text)
	)

	logging.info(f'{user} changed {attribute} from \'{old_value}\' to \'{message.text}\'')


def change_city(message: types.Message) -> None:
	''' Изменить город пользователя '''

	logging.debug('change_city is started')

	__change_value(
		message=message,
		attribute='city',
		success_text='Город изменен с {old_value} на {new_value}',
		cancel_text='Отмена смены города'
	)


def change_from_station(message: types.Message) -> None:
	''' Изменить Станцию отправления '''

	logging.debug('change_from_station is started')

	__change_value(
		message=message,
		attribute='from_station',
		success_text='Станция отправления изменена с {old_value} на {new_value}',
		cancel_text='Отмена смены Станции отправления'
	)


def change_to_station(message: types.Message) -> None:
	''' Изменить Станцию прибытия '''

	logging.debug('change_to_station is started')

	__change_value(
		message=message,
		attribute='to_station',
		success_text='Станция прибытия изменена с {old_value} на {new_value}',
		cancel_text='Отмена смены Станции прибытия'
	)
