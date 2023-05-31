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


def get_location(address: str) -> Location:
	g = Nominatim(user_agent='Usbam')
	loc = g.geocode(address)

	return loc


def get_coords(address: str) -> tuple:
	loc = get_location(address)

	return (loc.latitude, loc.longitude)


def send_request(address: str):
	try:
		lat, lon = get_coords(address)
	except AttributeError:
		return

	request = _REQUEST.format(
		lat=lat,
		lon=lon,
		API_key=WEATHER_API
	)
	try:
		data = requests.get(request).json()
	except ConnectionError:
		return

	return data


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


@dataclass
class WeatherElement:
	''' Хранилище данных о погоде в определенный период '''

	start: datetime
	temp: float
	humidity: int
	weather_icon: str
	weather_desc: str

	def __str__(self):
		return '[{start_time}] {temp}°C🌡  {humidity}%🌀  {weather_type} {weather_description}\n'.format(
			start_time=self.start.strftime('%H:%M'),
			temp=f'+{round(self.temp)}' if self.temp >= 0 else round(self.temp),
			humidity=self.humidity,
			weather_type=WEATHER_TYPES.get(self.weather_icon, ' '),
			weather_description=self.weather_desc
		)


def convert_from_json(data: dict) -> str:
	answer = 'Подгода в *{city}* на сегодня:\n\n'.format(
		city=data['city']['name']
	)
	now_date = datetime.now().strftime('%d.%m.%Y')

	for dt in data.get('list'):
		first_day = datetime.fromtimestamp(dt['dt']).strftime('%d.%m.%Y')
		elem = WeatherElement(
			start=datetime.fromtimestamp(dt['dt']),
			temp=dt['main']['temp'],
			humidity=dt['main']['humidity'],
			weather_icon=dt['weather'][0]['icon'][:-1],	# [:-1] - delete last sym ('d' or 'n')
			weather_desc=dt['weather'][0]['description']
		)

		if now_date != first_day:
			break

		answer += str(elem)

	return answer


def get_weather(city: str) -> str:
	weather_data = send_request(city)

	if weather_data is None:
		answer = 'Произошла ошибка получения данных или неправильно указано '+\
			'название города!'
	else:
		answer = convert_from_json(weather_data)

	return answer