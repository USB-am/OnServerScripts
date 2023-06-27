from logger import logging
from tg_bot import bot, start_timer


@logging
def main():
	start_timer()
	bot.infinity_polling()


if __name__ == '__main__':
	main()