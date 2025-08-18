# -*- coding: utf-8 -*-

import sys

from src import tg_bot
from src.weather_api import find_locality, get_weather


tg_bot.load_config('config.json')
bot = tg_bot.TelegramAPI()
bot.listen()


@bot.command(name='test')
def test_command(msg: tg_bot.Message) -> None:
    loclaity = find_locality('Ростов-на-Дону')
    weather = get_weather(loclaity)
    bot.send_message(msg.user.id, weather, reply_markup={})


@bot.command(name='exit')
def exit_command(msg: tg_bot.Message) -> None:
    sys.exit()
