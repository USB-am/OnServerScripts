from tg_bot import start_bot, stop_bot
from tg_bot.data_base import db


def main() -> None:
	db.create_all()
	try:
		start_bot()
	except Exception as error:
		print(error)
		stop_bot()


if __name__ == '__main__':
	main()
