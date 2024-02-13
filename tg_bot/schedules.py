import time
import logging
import datetime
import multiprocessing

import schedule

from tg_bot.bot import Bot
from tg_bot.data_base import TelegramUser
from tg_bot.weather import handlers as Weather
from config import MAILING_TIMES


__BOT = Bot('')


def __mailing_weather(date: datetime.date) -> None:
	''' Рассылает погоду всем пользователям '''

	users = TelegramUser.query.all()
	for user in users:
		weather_text = Weather.get_weather_by_city(user.city, date)
		__BOT.send_message(user.chat_id, weather_text, parse_mode='Markdown')

		logging.info(f'Send {user} schedule weather.')


def weather_event_registration():
	''' Регистрация событий рассылки погоды '''

	# Today mailing
	for day_time in MAILING_TIMES[:-1]:	# Without last timestamp
		schedule.every().day.at(day_time).do(
			__mailing_weather,
			date=datetime.datetime.now().date()
		)

	# Tomorrow mailing
	schedule.every().day.at(MAILING_TIMES[-1]).do(
		__mailing_weather,
		date=datetime.datetime.now().date() + datetime.timedelta(days=1)
	)

	while True:
		schedule.run_pending()
		time.sleep(1)


def start_schedule() -> None:
	''' Создать события '''

	weather_event_registration()


def start_timer() -> None:
	''' Запустить счетчик событий '''

	schedule_process.start()


def close_timer() -> None:
	''' Закрыть счетчик событий '''

	schedule_process.termite()


schedule_process = multiprocessing.Process(target=start_schedule, args=())
