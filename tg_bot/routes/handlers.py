import logging
from datetime import datetime, date

from telebot import types

from tg_bot.bot import Bot
from tg_bot.data_base import TelegramUser, Station
from tg_bot.data_base import handlers as DBHandlers
from tg_bot.data_base.manager import find_else_create_user
from .api import get_schedule


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


def is_valid_user_stations(user: TelegramUser) -> bool:
	''' Проверка соответствия станций у Пользователя '''

	fs = Station.query.get(user.from_station)
	ts = Station.query.get(user.to_station)

	return not (None in (fs, ts))


def user_station_select(message: types.Message, reply_text: str) -> types.Message:
	''' Выбор пользователем станции '''

	logging.debug('user_station_select is started')

	markup = types.InlineKeyboardMarkup()

	stations = Station.query.filter(Station.title.like(f'%{message.text}%'))
	for station in stations:
		btn_text = '{transport_type}{station_type} {title} ({address})'.format(
			title=station.title,
			address=f'{station.region}, {station.settlement}' \
				if station.settlement else f'{station.region}',
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


def get_routes(message: types.Message, date_: date=None) -> str:
	'''
	Получить расписание маршрутов.

	~params:
	message: types.Message - объект сообщения Telegram;
	date_: date=None - дата, на которую необходимо получить расписание.
	'''

	if date_ is None:
		date_ = datetime.now().date()

	user = find_else_create_user(message)
	from_station = Station.query.get(user.from_station)
	to_station = Station.query.get(user.to_station)

	if not is_valid_user_stations(user):
		fs = from_station.title if user.from_station else 'Неизвестно'
		ts = to_station.title if user.to_station else 'Неизвестно'
		return 'Сначало надо выбрать станции!\n' + \
			f'- Станция отправления: {fs}\n' + \
			f'- Станция прибытия: {ts}'

	schedule_json = get_schedule(from_station, to_station, date_)

	output = '{dt}\nРасписание между {from_}/{to}\n\n'.format(
		from_=from_station.title,
		to=to_station.title,
		dt=date_.strftime('%d.%m.%Y')
	)
	on_hour = datetime(1970, 1, 1)

	for i, segment in enumerate(schedule_json['segments']):
		try:
			transports = (segment['from']['transport_type'],
				          segment['to']['transport_type'])
		except KeyError:
			continue
		transport_types = ''.join(map(
			lambda tt: TRANSPORT_TYPES[tt], set(transports)
		))

		departure = datetime.fromisoformat(segment['departure'][:-6])
		arrival = datetime.fromisoformat(segment['arrival'][:-6])
		duration = datetime.fromtimestamp(segment['duration'])

		if on_hour.hour != departure.hour:
			output += f'\n{departure.strftime("%H")} часов:\n'
			on_hour = departure

		departure_str = departure.strftime('%H:%M')
		arrival_str = arrival.strftime('%H:%M')
		duration = arrival - departure

		duration_hours = int(duration.total_seconds() // 60 // 60)
		duration_minutes = int(duration.total_seconds() // 60)
		duration_str = '{days}{hours}{minutes}'.format(
			days=f'{duration.days}д ' if duration.days else '',
			hours=f'{duration_hours}ч ' if duration_hours else '',
			minutes=f'{duration_minutes}м'
		)
		output += f'{departure_str} {transport_types} {arrival_str} ⏳{duration_str}\n'

	return output.strip()
