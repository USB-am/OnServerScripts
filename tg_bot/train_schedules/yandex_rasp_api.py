from datetime import datetime, timedelta

import requests

from tg_bot.data_base import Station
from config import SCHEDULES_API


REQUEST = 'https://api.rasp.yandex.net/v3.0/search/?' + \
	'apikey={API_KEY}&' + \
	'from={from_}&' + \
	'to={to}&' + \
	'lang=ru_RU&' + \
	'date={date}&' + \
	'offset={offset}&' + \
	'limit=100'


def _send_request(from_station: Station, to_station: Station, offset: int=0) -> dict:
	now_date = (datetime.now() + timedelta(days=1)).date().strftime('%Y-%m-%d')
	req = REQUEST.format(
		API_KEY=SCHEDULES_API,
		from_=from_station.yandex_code,
		to=to_station.yandex_code,
		date=now_date,
		offset=offset
	)
	output = requests.get(req).json()

	return output


def __rfc3339_to_datetime(rfc3339: str) -> datetime:
	return datetime.fromisoformat(rfc3339)


def _get_schedule_json_times(yandex_api_json: dict) -> list:
	segments = yandex_api_json.get('segments', [])

	for segment in segments:
		departure_str = segment.get('departure', '')
		departure_datetime = __rfc3339_to_datetime(departure_str)

		arrival_str = segment.get('arrival', '')
		arrival_datetime = __rfc3339_to_datetime(arrival_str)

		print(departure_datetime.time(), arrival_datetime.time(), sep=' -> ')
	# print(dir(departure_datetime))
	# file = open('yandex_api_json.json', mode='w')
	# json.dump(yandex_api_json, file, indent=1, ensure_ascii=True)
	# file.close()


def get_schedules(from_station: Station, to_station: Station) -> list:
	schedule_json = _send_request(from_station, to_station)
	times = _get_schedule_json_times(schedule_json)