import os
from typing import Iterable

import requests

from src.database import add_entry, save_entries
from src.database.models import Country, Region, Settlement, Station


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

    for country in response.get('countries'):
        country_title = country.get('title')
        country_code = country.get('codes', {}).get('yandex_code')
        country_entry = Country(title=country_title,
                                yandex_code=country_code)
        add_entry(country_entry)

        for region in country.get('regions', []):
            region_title = region.get('title')
            region_code = region.get('codes', {}).get('yandex_code')
            region_entry = Region(title=region_title,
                                  yandex_code=region_code,
                                  country=country_entry.id)
            add_entry(region_entry)

            for settlement in region.get('settlements', []):
                settlement_title = settlement.get('title')
                settlement_code = settlement.get('codes', {}).get('yandex_code')
                settlement_entry = Settlement(title=settlement_title,
                                              yandex_code=settlement_code,
                                              region=region_entry.id)
                add_entry(settlement_entry)

                for station in settlement.get('stations', []):
                    station_code = station.get('codes', {}).get('yandex_code')
                    station_title = station.get('title')
                    station_type = station.get('station_type')
                    station_transport = station.get('transport_type')
                    station_entry = Station(title=station_title,
                                            type=station_type,
                                            yandex_code=station_code,
                                            transport=station_transport,
                                            settlement=settlement_entry.id)
                    add_entry(station_entry)
    save_entries()
