import logging
import datetime
from typing import List

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


def get_weather(message: types.Message) -> str:
	''' Возвращет погоду в городе пользователя '''

	logging.debug(f'get_weather is started')

	user = find_else_create_user(message)
	weather = parse_weather(user.city)
	now_date = datetime.datetime.now().date()
	now_date_weather = __filter_weather_list(weather, now_date)

	answer = 'Погода в *{city}* на {dt}:\n\n{weather}'.format(
		city=user.city,
		dt=now_date.strftime('%d.%m.%Y'),
		weather=__weather_list_to_str(now_date_weather))

	return answer
