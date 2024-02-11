import logging
import enum
from typing import Optional, List
from datetime import datetime
from dataclasses import dataclass

import requests
from requests.exceptions import ConnectionError
from geopy.geocoders import Nominatim
from geopy.location import Location

from config import WEATHER_API


# DOCUMENTATION:
# https://openweathermap.org/forecast5
_REQUEST = 'https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&units=metric&appid={API_key}&lang=ru'
# Шаблон вывода погоды на определенный период времени
WEATHER_CHAT_OUTPUT = '[{start_time}] {temp}°C🌡  {humidity}%🌀  {weather_type} {weather_description}'
# weather_code: emoji
WEATHER_TYPES = {
	'01': '☀️',
	'02': '🌤',
	'03': '☁️',
	'04': '🌤',
	'09': '🌧',
	'10': '🌦',
	'11': '⛈',
	'13': '🌨',
	'50': '🌁'
}


def get_location(address: str) -> Location:
	''' Получить объект локации по адресу '''

	g = Nominatim(user_agent='Usbam')
	loc = g.geocode(address)

	return loc


def get_coords(address: str) -> tuple:
	''' Получить координаты по адресу '''

	loc = get_location(address)

	return (loc.latitude, loc.longitude)


def send_request(address: str) -> Optional[list]:
	''' Отправить запрос к API openweathermap '''

	try:
		lat, lon = get_coords(address)
	except AttributeError:
		logging.warning(f'The address "{address}" coordinates cannot be determined')
		return

	request = _REQUEST.format(
		lat=lat,
		lon=lon,
		API_key=WEATHER_API
	)
	try:
		data = requests.get(request).json()
	except ConnectionError:
		logging.warning(f'The API request was not completed')
		return

	return data


class StatusCode(enum.Enum):
	''' Статусы ответа API '''

	ok = '200'


@dataclass
class WeatherElement:
	''' Хранилище данных о погоде в определенный период времени '''

	start: datetime
	temp: float
	humidity: int
	weather_icon: str
	weather_desc: str

	def __str__(self):
		return WEATHER_CHAT_OUTPUT.format(
			start_time=self.start.strftime('%H:%M'),
			temp=f'+{round(self.temp)}' if self.temp >= 0 else round(self.temp),
			humidity=self.humidity,
			weather_type=WEATHER_TYPES.get(self.weather_icon, ' '),
			weather_description=self.weather_desc
		)


def parse_weather(city: str) -> List[WeatherElement]:
	''' Обращается к API openweathermap и возвращает погоду '''

	response = send_request(city)
	if response['cod'] != StatusCode.ok.value:
		return []

	result = []
	for timestamp in response.get('list', []):
		try:
			# Время
			start = datetime.fromtimestamp(timestamp['dt'])
			# Температура
			temp = timestamp['main']['temp']
			# Влажность
			humidity = timestamp['main']['humidity']
			# Иконка
			weather_icon = timestamp['weather'][0]['icon'][:-1]	# Delete last symbol ('d' or 'n')
			# Описание
			weather_desc = timestamp['weather'][0]['description']
		except Exception as parse_error:
			logging.warning(f'Error when trying to parse weather!\n' +
			                 '{parse_error}')
			continue

		result.append(WeatherElement(
			start=start,
			temp=temp,
			humidity=humidity,
			weather_icon=weather_icon,
			weather_desc=weather_desc
		))

	return result
