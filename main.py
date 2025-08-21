# -*- coding: utf-8 -*-

import sys

from src import tg_bot
from src.weather_api import find_locality, get_weather
from src.database import find_else_create_user, update
from src.tg_bot.initializer import TelegramBot


tg_bot.load_config('config.json')
bot = TelegramBot()
bot.listen()


from logic import responses_to_user as RTU


@bot.command(name='start')
def start_command(msg: tg_bot.Message) -> None:
    user = find_else_create_user(msg)
    reply_markup = RTU.ReplyStartButtons().reply_markup()
    bot.send_message(chat_id=msg.user.id,
                     message=f'Привет {user.name}!',
                     reply_markup=reply_markup)


@bot.text()
def text_handler(msg: tg_bot.Message) -> None:
    text = msg.text.lower()
    if text == RTU.TextBtn.weather.value.lower():
        response = RTU.weather_response
    elif text == RTU.TextBtn.settings.value.lower():
        response = RTU.move_to_settings
    elif text == RTU.TextBtnSettings.change_city.value.lower():
        response = RTU.change_user_city
    elif text == RTU.TextBtnSettings.back_to_menu.value.lower():
        response = RTU.move_to_menu
    response(msg)


@bot.command(name='test')
def test_command(msg: tg_bot.Message) -> None:
    locality = find_locality('Ростов-на-Дону')
    weather = get_weather(locality)
    bot.send_message(msg.user.id, weather, reply_markup={})


@bot.command(name='exit')
def exit_command(msg: tg_bot.Message) -> None:
    sys.exit()
