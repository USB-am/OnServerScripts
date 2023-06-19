import unittest

from exceptions.tg_bot_exceptions import StationNotFound
from tg_bot.data_base import Station
from tg_bot import train_schedules as schedule


class TestFindStations(unittest.TestCase):
	def test_corrected_output(self):
		station = schedule.find_station(title='1337 км')

		self.assertEqual(station.yandex_code, 's9613376')

	def test_uncorrected_output(self):
		random_station_title = 'aksjdskjdghukdfgkdjfgbdkfg'

		self.assertRaises(StationNotFound,
		                  schedule.find_station,
		                  title=random_station_title
		)


if __name__ == '__main__':
	unittest.main()