import json
from datetime import datetime

import requests
from geopy.geocoders import Nominatim
from geopy.location import Location

from config import WEATHER_API


_REQUEST = 'https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&units=metric&appid={API_key}&lang=ru'


def get_location(address: str) -> Location:
	g = Nominatim(user_agent='Usbam')
	loc = g.geocode(address)

	return loc


def get_coords(address: str) -> tuple:
	loc = get_location(address)

	return loc.latitude, loc.longitude


def send_request(address: str):
	lat, lon = get_coords(address)

	request = _REQUEST.format(
		lat=lat,
		lon=lon,
		API_key=WEATHER_API
	)
	req = requests.get(request)

	return json.loads(req.text)


def convert_from_json(data: dict) -> str:
	answer = 'Подгода в {city}:'.format(
		city=data['city']['name']
	)
	last_day = ''

	for dt in data.get('list'):
		start_day = datetime.fromtimestamp(dt['dt']).strftime('%d.%m.%Y')
		start_time = datetime.fromtimestamp(dt['dt']).strftime('%H:%M')
		temp = dt['main']['temp']
		humidity = dt['main']['humidity']
		weather_type = dt['weather'][0]['main']
		weather_desc = dt['weather'][0]['description']

		if last_day != start_day:
			answer += f'\n\n{start_day}\n'
			last_day = start_day

		answer += f'{start_time} - {round(temp, 0)}🌡 {humidity}% {weather_type} {weather_desc}\n'

	return answer


WEATHER_TYPES = {
	'sun': '☀️',
	'partly_cloudy': '🌤️',
	'clouds': '🌥️',
	'partly_rain': '🌦️',
	'rain': '🌧️',
	'snow': '❄️'
}


def get_weather(city: str) -> str:
	weather_data = send_request(city)
	answer = convert_from_json(weather_data)

	return answer