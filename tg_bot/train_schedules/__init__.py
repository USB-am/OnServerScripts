from typing import List

from tg_bot.data_base import Station


def find_station(title: str, transport: str) -> List[Station]:
	stations = Station.query.filter_by(title=title, transport=transport).all()

	return stations


def get_schedules(transport: str, station_1: str, station_2: str) -> str:
	s1 = find_station(station_1, transport)
	s2 = find_station(station_2, transport)