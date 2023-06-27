# -*- coding: utf-8 -*-

from logger import logging
from tg_bot import bot


@logging
def main():
	bot.infinity_polling()


if __name__ == '__main__':
	main()