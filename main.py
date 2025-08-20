# -*- coding: utf-8 -*-

import sys
import enum
from typing import List

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


class TextBtnSettings(enum.Enum):
    change_city = 'Сменить город'
    back_to_menu = 'Назад'


class ReplyMarkupButtons:
    buttons: List[str] = []

    def reply_markup(self, **kwargs) -> str:
        return bot.create_reply_keyboard(keyboard=self.buttons, **kwargs)


class ReplyStartButtons(ReplyMarkupButtons):
    ''' Кнопки для главного меню '''
    buttons = [
        [TextBtn.weather.value, TextBtn.routes.value,],
        [TextBtn.settings.value,]
    ]


class ReplySettingsButtons(ReplyMarkupButtons):
    ''' Кнопки для настроек '''
    buttons = [
        [TextBtnSettings.change_city.value,],
        [TextBtnSettings.back_to_menu.value],
    ]


@bot.command(name='start')
def start_command(msg: tg_bot.Message) -> None:
    user = find_else_create_user(msg)
    reply_markup = ReplyStartButtons().reply_markup()
    bot.send_message(chat_id=msg.user.id,
                     message=f'Привет {user.name}!',
                     reply_markup=reply_markup)


@bot.text()
def text_handler(msg: tg_bot.Message) -> None:
    text = msg.text.lower()
    user = find_else_create_user(msg)

    if text == TextBtn.weather.value.lower():
        locality = find_locality(user.city)
        weather = get_weather(locality)
        msg_text = weather
        reply_markup = {}
    elif text == TextBtn.settings.value.lower():
        msg_text = 'Настройки'
        reply_markup = ReplySettingsButtons().reply_markup()
    elif text == TextBtnSettings.back_to_menu.value.lower():
        msg_text = 'Меню'
        reply_markup = ReplyStartButtons().reply_markup()

    bot.send_message(chat_id=msg.user.id,
                     message=msg_text,
                     reply_markup=reply_markup)


@bot.command(name='test')
def test_command(msg: tg_bot.Message) -> None:
    locality = find_locality('Ростов-на-Дону')
    weather = get_weather(locality)
    bot.send_message(msg.user.id, weather, reply_markup={})


@bot.command(name='exit')
def exit_command(msg: tg_bot.Message) -> None:
    sys.exit()
