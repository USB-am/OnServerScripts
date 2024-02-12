import logging
import datetime
from typing import List, Optional

from telebot import types

from tg_bot.bot import Bot
from .api import parse_weather, WeatherElement
from tg_bot.data_base.manager import find_else_create_user


__BOT = Bot('')


def __filter_weather_list(weather: List[WeatherElement],
	date: datetime.date) -> List[WeatherElement]:
	''' Фильтрует данные о погоде на конкретный день '''

	filtered_weather = filter(lambda w: w.start.date() == date, weather)

	return list(filtered_weather)


def __weather_list_to_str(weather: List[WeatherElement]) -> str:
	''' Конвертирует список WeatherElement'ов в красивую строку '''

	result = '\n'.join(map(str, weather))

	return result


def __get_weather_list(city, date: datetime.date) -> List[WeatherElement]:
	''' Получить погоду в городе на конкретную дату '''

	weather = parse_weather(city)

	if not weather:
		return []

	filtered_weather = __filter_weather_list(weather, date)

	return filtered_weather


def get_weather(message: types.Message) -> Optional[str]:
	''' Возвращет погоду в городе пользователя '''

	logging.debug(f'get_weather is started')

	user = find_else_create_user(message)
	now_date = datetime.datetime.now().date()
	answer = get_weather_by_city(user.city, now_date)

	return answer


def get_weather_on_date(message: types.Message, date: datetime.date) -> Optional[str]:
	''' Возвращает погоду в городе пользователя на конкретную дату '''

	logging.debug('get_weather_on_date is started')

	user = find_else_create_user(message)
	answer = get_weather_by_city(user.city, date)

	return answer


def get_weather_by_city(city: str, date: datetime.date) -> Optional[str]:
	''' Возвращает погоду в городе '''

	logging.debug('get_weather_by_city is started')

	weather = __get_weather_list(city, date)

	if not weather:
		return

	answer = 'Погода в *{city}* на {dt}:\n\n{weather}'.format(
		city=city,
		dt=date.strftime('%d.%m.%Y'),
		weather=__weather_list_to_str(weather)
	)

	return answer