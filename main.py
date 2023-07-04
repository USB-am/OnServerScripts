from logger import logging
from tg_bot import bot, start_timer#, stop_timer


def start():
	start_timer()
	bot.infinity_polling()


def stop():
	# stop_timer()
	bot.stop_polling()


# @logging
def main():
	while True:
		try:
			start()
		except KeyboardInterrupt:
			stop()
			break
		except Exception as error:
			print(f'[{error.__class__.__name__}] {" ".join(error.args)}')
			stop()


if __name__ == '__main__':
	main()