from typing import Union

from exceptions.tg_bot_exceptions import StationNotFound
from tg_bot.data_base import Station
from .yandex_rasp_api import _send_request


def find_station(title: str) -> Union[Station, StationNotFound]:
	station = Station.query.filter_by(title=title).first()

	if station is None:
		raise StationNotFound(f'Станция "{title}" не найдена!')

	return station


# def get_schedules(station_1: str, station_2: str) -> str:
# 	from_station = find_station(station_1)
# 	to_station = find_station(station_2)