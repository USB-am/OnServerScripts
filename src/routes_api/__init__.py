import os
import json
from typing import List, Dict
from datetime import datetime
from dataclasses import dataclass

import requests

from src.database import find_station
from src.database.models import Station


TRANSPORT_EMOJI = {
    'train': '🚃',
}


@dataclass
class Route:
    from_station: Station
    to_station: Station
    start_dt: datetime
    finish_dt: datetime
    transport_type: str

    def __str__(self):
        start_dt_str = self.start_dt.strftime('%H:%M')
        finish_dt_str = self.finish_dt.strftime('%H:%M')
        difference = self.finish_dt - self.start_dt
        difference_str = ':'.join(str(difference).replace('days', 'д').split(':')[:-1])

        return f'{start_dt_str} - {finish_dt_str} ({difference_str})'


class YandexRaspAPI:
    token = os.environ['YANDEX_RASP_TOKEN']
    url = '''https://api.rasp.yandex.net/v3.0/search/?
             apikey={apikey}&
             format=json&
             from={from_}&
             to={to}&
             lang=ru_RU&
             page=1&
             date={date}&
             transfers=true'''.replace('\n', '').replace(' ', '')

    def get_routes(self, from_code: str, to_code: str, dt: str=None) -> List[Route]:
        '''
        Получить список объектов Route для маршрута между точками from_code и to_code на дату dt.

        :param from_code: yandex код городов, станций или перевозчиков.
        :param to_code: yandex код городов, станций, перевозчиков.
        :param dt: Дата, на которую необходимо получить список рейсов (YYYY-MM-DD).
                   Если значение None, возвращает на текущую дату.

        :returns: Список Route объектов с информацией о рейсах на дату dt.
        '''
        format_string = "%Y-%m-%dT%H:%M:%S%z"
        routes: List[Route] = []

        response = self._send_search_request(from_code=from_code,
                                             to_code=to_code,
                                             dt=dt.strftime(format_string))
        schedule_json = response.json()
        from_station = find_station(station_yandex_code=from_code)
        to_station = find_station(station_yandex_code=to_code)

        for segment in schedule_json.get('segments', []):
            departure = datetime.strptime(segment.get('departure'), format_string)
            arrival = datetime.strptime(segment.get('arrival'), format_string)
            transport_type = segment.get('from', {}).get('transport_type', '')
            routes.append(Route(from_station=from_station,
                                to_station=to_station,
                                start_dt=departure,
                                finish_dt=arrival,
                                transport_type=transport_type))
        return routes

    def _send_search_request(self, from_code: str, to_code: str, dt: str=None) -> Dict:
        '''
        Получить расписание из точки from_code до to_code.
        doc: https://yandex.ru/dev/rasp/doc/ru/reference/schedule-point-point

        :param from_code: yandex код городов, станций или перевозчиков.
        :param to_code: yandex код городов, станций, перевозчиков.
        :param dt: Дата, на которую необходимо получить список рейсов (YYYY-MM-DD).
                   Если значение None, возвращает на текущую дату.

        :returns: Список Route объектов с информацией о рейсах на дату dt.
        '''
        if dt is None:
            dt = datetime.now().strftime('%Y-%m-%d')
        request = self.url.format(apikey=self.token,
                                  from_=from_code,
                                  to=to_code,
                                  date=dt)

        return requests.get(request)
