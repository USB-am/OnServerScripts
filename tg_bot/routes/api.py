import datetime
from typing import Dict

import requests

from tg_bot.data_base import db, Station
from config import SCHEDULES_API


# Documentation:
# https://yandex.ru/dev/rasp/doc/reference/schedule-point-point.html

_REQUEST = 'https://api.rasp.yandex.net/v3.0/search/?' + \
	'apikey={API_KEY}&' + \
	'from={from_}&' + \
	'to={to}&' + \
	'lang=ru_RU&' + \
	'date={date}&' + \
	'offset={offset}&' + \
	'limit=100&' + \
	'transfers=true'
# Request headers
_HEADERS = {
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 YaBrowser/22.11.5.715 Yowser/2.5 Safari/537.36',
	'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
	'accept-language': 'ru,en;q=0.9',
}


def __rfc3339_to_datetime(rfc3339: str) -> datetime.datetime:
	return datetime.fromisoformat(rfc3339)


def get_schedule(from_: Station, to: Station, date_: datetime.date,
                 offset: int=0) -> Dict:
	''' Получить расписания между Станциями '''

	from_code = from_.yandex_code
	to_code = to.yandex_code

	url = _REQUEST.format(
		API_KEY=SCHEDULES_API,
		from_=from_code,
		to=to_code,
		date=date_.strftime('%Y-%m-%d'),
		offset=offset
	)
	schedules = requests.get(url, headers=_HEADERS).json()

	return schedules


def parse_all_stations() -> Dict:
	''' Получить все станции yandex.api '''

	url = 'https://api.rasp.yandex.net/v3.0/stations_list/?' + \
		f'apikey={SCHEDULES_API}&' + \
		'lang=ru_RU&' + \
		'format=json'
	response = requests.get(url, headers=_HEADERS)

	return response.json()


def create_stations() -> None:
	''' Сохранить все станции yandex.api в .json и базу данных '''
	import json

	x = parse_all_stations()
	with open('stations.json', mode='w') as fp:
		json.dump(x, fp, indent=2)#, ensure_ascii=True)
	print('function json.dump is finished')

	with open('stations.json', mode='r') as fp:
		data = json.load(fp)

		for country in data['countries']:
			country_title = country['title']

			for region in country['regions']:
				region_title = region['title']
				
				for settlement in region['settlements']:
					settlement_title = settlement['title']

					for station in settlement['stations']:
						station_title = station['title']
						yandex_code = station['codes'].get('yandex_code')
						esr_code = station['codes'].get('esr_code')
						type_ = station['station_type']
						transport_type = station['transport_type']

						new_station = Station(
							yandex_code=yandex_code,
							esr_code=esr_code,
							title=station_title,
							type=type_,
							transport=transport_type,
							settlement=settlement_title,
							region=region_title,
							country=country_title
						)
						db.session.add(new_station)

		db.session.commit()

	print('function json.load is finished')
