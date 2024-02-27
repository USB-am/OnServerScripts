import logging
from typing import Union, Any

from telebot import types

from . import Station
from .manager import find_else_create_user, update
from tg_bot.bot import Bot


__BOT = Bot('')


def __change_value(message: types.Message, attribute: str,
                  success_text: str, cancel_text: str, value: Any=None) -> None:
	''' Абстрактная функция изменения значения в БД по сообщению '''

	if message.text.lower() == 'отмена':
		__BOT.send_message(message.chat.id, cancel_text)
		return

	user = find_else_create_user(message)
	old_value = getattr(user, attribute)

	if value is None:
		update(user, attribute, message.text)
	else:
		update(user, attribute, value)

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


def change_from_station(call: Union[types.CallbackQuery, types.Message]) -> None:
	''' Изменить Станцию отправления '''

	logging.debug('change_from_station is started')

	cancel_text = 'Отмена смены Станции отправления'

	if isinstance(call, types.Message):
		__BOT.send_message(call.chat.id, cancel_text)
		return

	finded_station = Station.query.filter_by(yandex_code=call.data).first()
	call.message.text = finded_station.title
	__change_value(
		message=call.message,
		attribute='from_station',
		success_text='Станция отправления изменена с {old_value} на {new_value}',
		cancel_text=cancel_text,
		value=finded_station.id
	)


def change_to_station(call: types.CallbackQuery) -> None:
	''' Изменить Станцию прибытия '''

	logging.debug('change_to_station is started')

	cancel_text = 'Отмена сметы Станции прибытия'

	if isinstance(call, types.Message):
		__BOT.send_message(call.chat.id, cancel_text)
		return

	finded_station = Station.query.filter_by(yandex_code=call.data).first()
	call.message.text = finded_station.title
	__change_value(
		message=call.message,
		attribute='to_station',
		success_text='Станция прибытия изменена с {old_value} на {new_value}',
		cancel_text=cancel_text,
		value=finded_station.id
	)
