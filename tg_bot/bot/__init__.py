from telebot import TeleBot


class _Singleton(type):
	_instance = None

	def __call__(cls, *args, **kwargs):
		if cls._instance is None:
			cls._instance = super(_Singleton, cls).__call__(*args, **kwargs)

		return cls._instance


class Bot(TeleBot, metaclass=_Singleton):
	''' Представление бота '''
