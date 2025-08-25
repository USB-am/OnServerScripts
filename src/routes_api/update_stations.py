import os

import requests

from dataclasses import dataclass
from typing import Iterable


@dataclass
class Station:
    yandex_code: str
    station_type: str
    title: str
    lat: float
    lon: float
    transport_type: str

    def __str__(self):
        return self.title


def get_stations() -> Iterable:
	url = 'https://api.rasp.yandex.net/v3.0/stations_list/?apikey={token}&lang=ru_RU&format=json'
	headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 YaBrowser/22.11.5.715 Yowser/2.5 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'ru,en;q=0.9',
        'X-Gismeteo-Token': os.environ['WEATHER_TOKEN'],
        'Accept-Encoding': 'gzip',
    }
	req = requests.get(url.format(token=os.environ['YANDEX_RASP_TOKEN']),
					   headers=headers)
	response = req.json()
	x = response['countries'][100]
	print(x, type(x), sep='\n')
