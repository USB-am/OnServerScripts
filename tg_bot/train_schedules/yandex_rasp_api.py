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