import telebot

from config import TELEGRAM_TOKEN
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
		bot.send_message(message.chat.id, 'Некорректный запрос!\n/weather <название города>')
		return

	bot.send_message(message.chat.id, get_weather(city))