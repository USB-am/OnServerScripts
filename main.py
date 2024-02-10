import logging

from tg_bot import start_bot, stop_bot


# Set logging level
logging.basicConfig(level=logging.INFO)


def main() -> None:
	try:
		start_bot()
	except Exception as error:
		logging.critical(error)
		stop_bot()


if __name__ == '__main__':
	main()
