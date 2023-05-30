import telebot

from config import TELEGRAM_TOKEN
from .data_base import db
from .weather import get_weather


bot = telebot.TeleBot(TELEGRAM_TOKEN)


@bot.message_handler(commands=['help',])
def start(message):
	bot.send_message(message.chat.id, f'Подгода: /weather <название города>')


@bot.message_handler(commands=['weather',])
def send_weather(message):
	try:
		_, city = message.text.split(maxsplit=1)
	except ValueError as exc:
		bot.send_message(
			message.chat.id,
			'Некорректный запрос!\n/weather <название города>',
			parse_mode='Markdown'
		)
		return

	'''
	print(dir(message.chat), message.chat.id, sep='\n')
	print(f'Id: {message.chat.id}')
	print(f'First name: {message.chat.first_name}')
	print(f'Last name:  {message.chat.last_name}')
	print(f'Username: {message.chat.username}')
	print(f'Title: {message.chat.title}')
	print(f'Type: {message.chat.type}')
	print('\n')
	'''
	bot.send_message(message.chat.id, get_weather(city), parse_mode='Markdown')