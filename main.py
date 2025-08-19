# -*- coding: utf-8 -*-

import sys
import enum

from src import tg_bot
from src.weather_api import find_locality, get_weather
from src.database import find_else_create_user


tg_bot.load_config('config.json')
bot = tg_bot.TelegramAPI()
bot.listen()


class TextBtn(enum.Enum):
	weather = 'Погода'
	routes = 'Транспорт'
	settings = 'Настройки'


@bot.command(name='start')
def start_command(msg: tg_bot.Message) -> None:
	user = find_else_create_user(msg)
	btns = [
		[TextBtn.weather.value, TextBtn.routes.value,],
		[TextBtn.settings.value,]
	]
	reply_markup = bot.create_reply_keyboard(keyboard=btns)
	bot.send_message(chat_id=msg.user.id,
					 message=f'Привет {user.name}!',
					 reply_markup=reply_markup)


@bot.command(name=TextBtn.weather.value)
def get_weather_command(msg: tg_bot.Message) -> None:
	user = find_else_create_user(msg)
	locality = find_locality(user.city)
	weather = get_weather(locality)
	bot.send_message(msg.user.id, weather, reply_markup={})


@bot.command(name='test')
def test_command(msg: tg_bot.Message) -> None:
    locality = find_locality('Ростов-на-Дону')
    weather = get_weather(locality)
    bot.send_message(msg.user.id, weather, reply_markup={})


@bot.command(name='exit')
def exit_command(msg: tg_bot.Message) -> None:
    sys.exit()
