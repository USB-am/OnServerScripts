# -*- coding: utf-8 -*-

import sys
import enum
from typing import List

from src import tg_bot
tg_bot.load_config('config.json')

from src.weather_api import find_locality, get_weather
from src.database import find_else_create_user, update
from src.tg_bot.initializer import TelegramBot
from src.routes_api import YandexRaspAPI
from src.routes_api.update_stations import get_stations


bot = TelegramBot()
bot.listen()


from logic import responses_to_user as RTU


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
    reply_markup = RTU.ReplyStartButtons().reply_markup()
    bot.send_message(chat_id=msg.user.id,
                     message=f'Привет {user.name}!',
                     reply_markup=reply_markup)


# @bot.text()
# def text_handler(msg: tg_bot.Message) -> None:
#     text = msg.text.lower()
#     if text == RTU.TextBtn.weather.value.lower():
#         response = RTU.weather_response
#     elif text == RTU.TextBtn.settings.value.lower():
#         response = RTU.move_to_settings
#     elif text == RTU.TextBtnSettings.change_city.value.lower():
#         response = RTU.change_user_city
#     elif text == RTU.TextBtnSettings.back_to_menu.value.lower():
#         response = RTU.move_to_menu
#     response(msg)


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
    elif text == TextBtnSettings.change_city.value.lower():
        msg_text = 'Введи название города:'
        reply_markup = {}
        bot.wait_user_message(chat_id=msg.user.id,
                              message=msg_text,
                              callback=change_user_city)
        return
    elif text == TextBtnSettings.back_to_menu.value.lower():
        msg_text = 'Меню'
        reply_markup = ReplyStartButtons().reply_markup()

    bot.send_message(chat_id=msg.user.id,
                     message=msg_text,
                     reply_markup=reply_markup,
                     parse_mode='Markdown')


def change_user_city(msg: tg_bot.Message) -> None:
    ''' Сменить город пользователя '''
    if msg.text.lower() == 'отмена':
        bot.send_message(chat_id=msg.user.id,
                         message='Отмена смены города',
                         reply_markup=ReplySettingsButtons().reply_markup())
    elif not msg.text:
        bot.send_message(chat_id=msg.user.id,
                         message='Поле не может быть пустым',
                         reply_markup={})
    user = find_else_create_user(msg)
    old_city_name = user.city
    update(entry=user, arg='city', value=msg.text)
    bot.send_message(chat_id=msg.user.id,
                     message=f'Город был изменен с *{old_city_name}* на *{msg.text}*',
                     reply_markup={},
                     parse_mode='Markdown')


@bot.command(name='test')
def test_command(msg: tg_bot.Message) -> None:
    locality = find_locality('Ростов-на-Дону')
    weather = get_weather(locality)
    bot.send_message(msg.user.id, weather, reply_markup={})


@bot.command(name='route')
def route_command(msg: tg_bot.Message) -> None:
    # routes = get_routes()
    pass


@bot.command(name='stations')
def stations_command(msg: tg_bot.Message) -> None:
    get_stations()


@bot.command(name='exit')
def exit_command(msg: tg_bot.Message) -> None:
    sys.exit()
