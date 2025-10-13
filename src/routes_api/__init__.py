import os
from typing import List, Dict
from datetime import datetime
from dataclasses import dataclass

import requests

from .update_stations import get_stations, Station


@dataclass
class Route:
    from_station: Station
    to_station: Station

    def __str__(self):
        return f'{self.from_station} → {self.to_station}'


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
        response = self._send_search_request(from_code, to_code, dt)
        x = response.keys()
        print(x)
    
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

        return requests.get(request).json()
