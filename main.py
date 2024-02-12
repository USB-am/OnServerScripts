import logging

from tg_bot import start_bot, stop_bot
from tg_bot.schedules import start_timer, close_timer


# Set logging level
logging.basicConfig(level=logging.INFO)


def main() -> None:
	try:
		start_timer()
		start_bot()
	except Exception as error:
		logging.critical(error)
		close_timer()
		stop_bot()


if __name__ == '__main__':
	main()
