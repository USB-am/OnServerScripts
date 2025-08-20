import os
from typing import Tuple
from datetime import datetime, date, time
from dataclasses import dataclass

import requests
from geopy.geocoders import Nominatim


WEATHER_URL = 'https://api.gismeteo.net/v3/weather/forecast/h1/?latitude={lat}&longitude={lon}'


@dataclass
class Locality:
    id: int
    name: str
    url: str

    def __str__(self):
        return self.name


def find_locality(address: str) -> Locality:
    '''
    Найти координаты по адресу

    :param address: адрес, координаты которого необходимо найти
    :returns: Locality object
    '''
    url = 'https://api.gismeteo.net/v2/search/cities/?query={locality}'.format(locality=address)
    resp = send_request(url).json()

    locality_data = resp['response']['items'][0]
    return Locality(id=locality_data['id'],
                    name=locality_data['name'],
                    url=locality_data['url'])


def get_coords(locality: Locality) -> Tuple[float, float]:
    '''
    Получить координаты по локации

    :param locality: локация, координаты которой будут возвращены
    :returns: кортеж координат локации (долгота, широта)
    '''
    loc = Nominatim(user_agent='Usbam', timeout=3).geocode(locality.name)
    return (loc.latitude, loc.longitude)


@dataclass
class WeatherStamp:
    timestamp: int
    temperature: float
    description: str
    humidity: int
    emoji: str

    @property
    def dt(self) -> datetime:
        return datetime.fromtimestamp(self.timestamp)
    @property
    def d(self) -> date:
        return datetime.fromtimestamp(self.timestamp).date()
    @property
    def t(self) -> time:
        return datetime.fromtimestamp(self.timestamp).time()

    def __str__(self):
        return '{hour}:00 {temperature}°C🌡  {humidity}%🌀  {emoji} {description}'.format(
            hour=str(self.dt.hour).rjust(2, '0'),
            temperature=int(self.temperature),
            humidity=self.humidity,
            emoji=self.emoji,
            description=self.description
        )


def parse_weather(weather: dict) -> WeatherStamp:
    ''' Получить данные о погоде '''
    timestamp = weather['date']['unix']
    temperature = weather['temperature']['air']['C']
    description = weather['description']
    humidity = weather['humidity']['percent']
    emoji = weather['icon']['emoji']

    return WeatherStamp(timestamp=timestamp,
                        temperature=temperature,
                        description=description,
                        humidity=humidity,
                        emoji=emoji)


def get_weather(locality: Locality, day: date=None) -> str:
    '''
    Получить погоду по локации

    :param locality: локация, погода которой будет возвращена
    '''
    if day is None:
        day = datetime.now().date()
    lat, lon = get_coords(locality)
    url = 'https://api.gismeteo.net/v3/weather/forecast/h1/?latitude={lat}&longitude={lon}'
    weather_json = send_request(url.format(lat=lat, lon=lon)).json()
    weather_data = weather_json['data']

    weather_stamp = [parse_weather(weather) for weather in weather_data]
    today_weather = filter(lambda w: w.d == day, weather_stamp)

    output = f'Погода в *{locality.name}* {day.strftime("%d.%m.%Y")}:\n\n'
    for weather in today_weather:
        output += str(weather) + '\n'

    return output.strip()


def send_request(url: str) -> requests.Response:
    ''' Отправить запрос '''
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 YaBrowser/22.11.5.715 Yowser/2.5 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'ru,en;q=0.9',
        'X-Gismeteo-Token': os.environ['WEATHER_TOKEN'],
        'Accept-Encoding': 'gzip',
    }
    response = requests.get(url=url, headers=headers)
    return response
