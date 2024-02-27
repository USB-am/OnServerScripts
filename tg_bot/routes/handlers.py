import logging

from telebot import types

from tg_bot.bot import Bot
from tg_bot.data_base import Station
from tg_bot.data_base import handlers as DBHandlers
from tg_bot.data_base.manager import find_else_create_user


__BOT = Bot('')


TRANSPORT_TYPES = {
	'plane': '✈',		# самолет
	'train': '🚂',		# поезд
	'suburban': '🚝',	# электричка
	'bus': '🚍',		# автобус
	'water': '⚓',		# морской транспорт
	'helicopter': '🚁',	# вертолет
}
STATION_TYPES = {
	'station': '🚉',			# станция
	'platform': '🚉',			# платформа
	'stop': '🚏',				# остановочный пункт
	'checkpoint': '🪖',			# блок-пост
	'post': '🚧',				# пост
	'crossing': '🛣',			# разъезд
	'overtaking_point': '🛣',	# обгонный пункт
	'train_station': '🏫',		# вокзал
	'airport': '🏨',			# аэропорт
	'bus_station': '🏣',		# автовокзал
	'bus_stop': '🚏',			# автобусная остановка
	'unknown': '🚏',				# станция без типа
	'port': '⚓',				# порт
	'port_point': '⚓',			# портпункт
	'wharf': '⚓',				# пристань
	'river_port': '⚓',			# речной вокзал
	'marine_station': '⚓',		# морской вокзал
}


def user_station_select(message: types.Message, reply_text: str) -> types.Message:
	''' Выбор пользователем станции '''

	logging.debug('user_station_select is started')

	markup = types.InlineKeyboardMarkup()

	stations = Station.query.filter(Station.title.like(f'%{message.text}%'))
	for station in stations:
		btn_text = '{title} {transport_type}{station_type}'.format(
			title=station.title,
			transport_type=TRANSPORT_TYPES[station.transport],
			station_type=STATION_TYPES[station.type])
		btn = types.InlineKeyboardButton(btn_text, callback_data=station.yandex_code)
		markup.add(btn)

	session = __BOT.reply_to(message, reply_text, reply_markup=markup)

	return session


def change_from_station(message: types.Message)	-> None:
	''' Диалог изменения Станции отправления '''

	logging.debug('routes.change_from_station is started')

	session = user_station_select(message, reply_text='Введи пункт отправления:')
	__BOT.register_next_step_handler(session, DBHandlers.change_from_station)


def change_to_station(message: types.Message)	-> None:
	''' Диалог изменения Станции отправления '''

	logging.debug('routes.change_to_station is started')

	session = user_station_select(message, reply_text='Введи пункт прибытия:')
	__BOT.register_next_step_handler(session, DBHandlers.change_to_station)	


def get_routes(message: types.Message) -> str:
	''' Получить расписание маршрутов '''

	user = find_else_create_user(message)
	user_station_select(message)

	return 'Пока что это не работает'
