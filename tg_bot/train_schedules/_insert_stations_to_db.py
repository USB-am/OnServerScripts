import json

import requests

from config import SCHEDULES_API
from tg_bot.data_base import db, Station


url = 'https://api.rasp.yandex.net/v3.0/stations_list/?apikey={0}&lang=ru_RU&format=json'.format(SCHEDULES_API)


def start() -> None:
	data = json.loads(requests.get(url).text)

	for country in data.get('countries', []):
		country_title = country.get('title', '')

		for region in country.get('regions', []):
			region_title = region.get('title')


			for settlement in region.get('settlements', []):
				settlement_title = settlement_title = settlement.get('title', '')

				for station in settlement.get('stations', []):
					station_title = station.get('title', '')
					station_type = station.get('station_type', '')
					transport_type = station.get('transport_type', '')

					esr_code = station.get('codes', {}).get('esr_code')
					yandex_code = station.get('codes', {}).get('yandex_code')

					station = Station(
						yandex_code=yandex_code,
						esr_code=esr_code,
						title=station_title,
						type=station_type,
						transport=transport_type,
						settlement=settlement_title,
						region=region_title,
						country=country_title
					)
					print(station)

					db.session.add(station)
					db.session.commit()