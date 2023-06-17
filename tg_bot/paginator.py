from telebot import types


class Paginator:
	''' Пагитатор с кнопками выбора '''

	def __init__(slef, bot: telebot.TeleBot, titles: list, current_page: int=1, list_length: int=10):
		if current_page <= 0:
			current_page = 1
		elif current_page >= len(titles):
			current_page = len(titles) - 1

		self.current_page = current_page
		self.list_length = list_length
		self.bot = bot
		self.titles = titles

		self._build_construction()

	def _build_construction(self) -> None:
		keyboard = types.InlineKeyboardMarkup()

		for element in range(self.list_length):
			pass