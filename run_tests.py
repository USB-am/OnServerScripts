import unittest

from tests import yandex_rasp_api_test, find_stations_test


if __name__ == '__main__':
	yandex_tests = unittest.TestLoader().loadTestsFromModule(yandex_rasp_api_test)
	find_stations_tests = unittest.TestLoader().loadTestsFromModule(find_stations_test)
	unittest.TextTestRunner(verbosity=2).run(yandex_tests)
	unittest.TextTestRunner(verbosity=2).run(find_stations_tests)