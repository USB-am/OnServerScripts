import os
from datetime import datetime
from dataclasses import dataclass
from typing import List
from pprint import pprint

import requests
from requests.exceptions import ConnectionError
from geopy.geocoders import Nominatim
from geopy.location import Location


class LocalityError(Exception):
	''' Ошибка поиска адреса '''


@dataclass
class Locality:
	id: int
	name: str
	url: str

	def __str__(self):
		return self.name


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
			weather_type=self.weather_icon,
			weather_description=self.weather_desc
		)


codes = {
	4: 'Дым',
	5: 'Мгла',
	6: 'Пыльная буря',
	7: 'Пыльная буря',
	8: 'Пыльные вихри',
	9: 'Пыльная буря',
	10: 'Дымка',
	11: 'Туман',
	12: 'Туман',
	13: 'Зарница',
	18: 'Шквалы',
	19: 'Смерч',
	20: 'Морось',
	24: 'Гололед',
	25: 'Ливень',
	27: 'Град',
	28: 'Туман',
	30: 'Пыльная буря',
	31: 'Пыльная буря',
	32: 'Пыльная буря',
	33: 'Пыльная буря',
	34: 'Пыльная буря',
	35: 'Пыльная буря',
	36: 'Поземок',
	37: 'Сильный поземок',
	38: 'Метель',
	39: 'Сильная метель',
	40: 'Туман',
	41: 'Туман',
	42: 'Туман',
	43: 'Туман',
	44: 'Туман',
	45: 'Туман',
	46: 'Туман',
	47: 'Туман',
	48: 'Туман',
	49: 'Туман',
	50: 'Небольшая морось',
	51: 'Морось',
	52: 'Морось',
	53: 'Морось',
	54: 'Сильная морось',
	55: 'Морось',
	56: 'Небольшая морось',
	57: 'Морось',
	66: 'Гололед',
	67: 'Гололед',
	68: 'Дождь со снегом',
	69: 'Дождь со снегом',
	74: 'Снегопад',
	75: 'Снегопад',
	76: 'Ледяные иглы',
	77: 'Снежные зёрна',
	78: 'Снежные кристаллы',
	79: 'Ледяной дождь',
	81: 'Ливень',
	82: 'Сильный ливень',
	83: 'Небольшие осадки',
	84: 'Ливень',
	87: 'Снежная крупа',
	88: 'Снежная крупа',
	89: 'Слабый град',
	90: 'Град',
	93: 'Град',
	94: 'Град',
	96: 'Град',
	99: 'Град',
	104: 'Мгла',
	105: 'Мгла',
	110: 'Дымка',
	111: 'Ледяные иглы',
	112: 'Зарница',
	118: 'Шквалы',
	120: 'Туман',
	122: 'Морось',
	125: 'Гололёд',
	130: 'Туман',
	131: 'Туман',
	132: 'Туман',
	133: 'Туман',
	134: 'Туман',
	135: 'Туман',
	147: 'Осадки',
	148: 'Сильные осадки',
	150: 'Морось',
	151: 'Небольшая морось',
	152: 'Морось',
	153: 'Сильная морось',
	154: 'Небольшая морось',
	155: 'Морось',
	156: 'Сильная морось',
	164: 'Гололед',
	165: 'Гололед',
	166: 'Гололед',
	174: 'Слабая ледяная крупа',
	175: 'Ледяная крупа',
	176: 'Сильная ледяная крупа',
	177: 'Снежные зерна',
	178: 'Ледяные кристалы',
	180: 'Ливневый дождь',
	189: 'Град',
	193: 'Град',
	196: 'Град',
	199: 'Смерч',
	280: 'Ливневый снег',
	380: 'Ливневые осадки',
	500: 'Осадки',
	501: 'Сильные осадки',
	528: 'Морозный туман',
	568: 'Небольшие осадки',
}


# DOCUMENTATION
# https://www.gismeteo.ru/api/#kind
# https://docs.gismeteo.net/v3/weather/
API_KEY = os.environ['GISMETEO_API_KEY']
_GET_WEATHER = 'https://api.gismeteo.net/v3/weather/forecast/h1/?latitude={lat}&longitude={lon}'
_FIND_LOCALITY_REQUEST = 'https://api.gismeteo.net/v2/search/cities/?query={locality}'
# Request headers
_HEADERS = {
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 YaBrowser/22.11.5.715 Yowser/2.5 Safari/537.36',
	'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
	'accept-language': 'ru,en;q=0.9',
	'X-Gismeteo-Token': API_KEY,
	'Accept-Encoding': 'gzip',
}
# Шаблон вывода погоды на определенный период времени
WEATHER_CHAT_OUTPUT = '[{start_time}] {temp}°C🌡  {humidity}%🌀  {weather_type} {weather_description}'


def get_location(address: str) -> Location:
	''' Получить объект локации по адресу '''

	g = Nominatim(user_agent='Usbam')
	loc = g.geocode(address)

	return loc


def get_coords(address: str) -> tuple:
	''' Получить координаты по адресу '''

	loc = get_location(address)
	print(address, loc, sep='\n')

	return (loc.latitude, loc.longitude)


def send_request(url: str) -> dict:
	r = requests.get(url, headers=_HEADERS)
	if r.status_code != 200:
		raise ConnectionError

	return r.json()


def get_locality(address: str) -> Locality:
	''' Получить данные населенного пункта '''

	r = send_request(_FIND_LOCALITY_REQUEST.format(locality=address))
	try:
		locality_data = r['response']['items'][0]	# Get first locality
	except IndexError:
		raise LocalityError(f'{address} not found!')

	return Locality(id=locality_data['id'],
	                name=locality_data['name'],
	                url=locality_data['url'])


def parse_weather(locality: str) -> List[WeatherElement]:
	'''
	Получить прогноз через GISMETEO API.

	~params:
	locality: str - населенный пункт, прогноз которого будет выведен.
	'''

	try:
		lat, lon = get_coords(locality)
	except Exception as LocalityError:
		return []
	url = _GET_WEATHER.format(lat=lat, lon=lon)
	try:
		r = send_request(url)
		weather_data = r.get('data', [])
	except ConnectionError:
		return []

	result = []
	for data in weather_data:
		try:
			# Время
			start = datetime.fromtimestamp(data['date']['unix'])
			# Температура
			temp = data['temperature']['air']['C']
			# Влажность
			humidity = data['humidity']['percent']
			# Иконка
			weather_icon = data['icon']['emoji']
			# Описание
			weather_desc = data['description']
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


if __name__ == '__main__':
	parse_weather('ростов-на-до')
