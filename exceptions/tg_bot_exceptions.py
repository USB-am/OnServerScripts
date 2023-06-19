


class StationNotFound(Exception):
	''' Ошибка неудачного поиска станции '''

	def __init__(self, *args):
		if args:
			self.message = args[0]
		else:
			self.message = None

	def __str__(self):
		if self.message:
			return f'Station not found! {self.message}'
		else:
			return f'Station not found!'