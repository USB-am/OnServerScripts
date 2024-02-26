from telebot import types

from tg_bot.data_base.manager import find_else_create_user


def get_routes(message: types.Message) -> str:
	''' Получить расписание маршрутов '''

	user = find_else_create_user(message)

	return 'Пока что это не работает'
