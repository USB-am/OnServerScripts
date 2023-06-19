import unittest

from tg_bot.train_schedules import yandex_rasp_api as ya_api
from tg_bot.data_base import Station


class TestRequest(unittest.TestCase):
	''' Тестирование отправки API-запроса '''

	@classmethod
	def setUpClass(cls):
		from_station = Station.query.filter_by(title='1337 км').first()
		to_station = Station.query.filter_by(title='Ростов-Главный').first()

		cls.output = ya_api._send_request(from_station, to_station)

	def test_output_type(self):
		self.assertIsInstance(self.output, dict)

	def test_output_error(self):
		is_error = self.output.get('error', True)
		self.assertTrue(is_error)


if __name__ == '__main__':
	unittest.main()