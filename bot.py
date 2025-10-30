# -*- coding: utf-8 -*-

import re
import sys
import enum
from typing import List
from datetime import datetime, timedelta

from src import tg_bot
# tg_bot.load_config('config.json')

from src.weather_api import find_locality, get_weather
from src.database import find_else_create_user, update, find_station
from src.tg_bot.initializer import TelegramBot
from src.routes_api import YandexRaspAPI, Route, TRANSPORT_EMOJI
from src.routes_api.update_stations import update_stations
from settings import TZ_UTC_3


# bot = TelegramBot()
# bot.listen()


from logic import responses_to_user as RTU


class TextBtn(enum.Enum):
    weather = 'Погода'
    routes = 'Транспорт'
    settings = 'Настройки'


class TextBtnWeather(enum.Enum):
    weather_today = 'Погода на сегодня'
    weather_tomorrow = 'Погода на завтра'
    back_to_menu = 'Назад'


class TextBtnTransport(enum.Enum):
    from_to = 'Расписание туда'
    to_from = 'Расписание обратно'
    from_to_tomorrow = 'Расписание туда (завтра)'
    to_from_tomorrow = 'Расписание обратно (завтра)'
    back_to_menu = 'Назад'


class TextBtnSettings(enum.Enum):
    change_city = 'Сменить город'
    change_from_station = 'Станция отправления'
    change_to_station = 'Станция прибытия'
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


class ReplyWeatherButtons(ReplyMarkupButtons):
    ''' Кнопки для погоды '''
    buttons = [
        [TextBtnWeather.weather_today.value],
        [TextBtnWeather.weather_tomorrow.value],
        [TextBtnWeather.back_to_menu.value]
    ]


class ReplyTransportButtons(ReplyMarkupButtons):
    ''' Кнопки для транспорта '''
    buttons = [
        [TextBtnTransport.from_to.value, TextBtnTransport.to_from.value],
        [TextBtnTransport.from_to_tomorrow.value, TextBtnTransport.to_from_tomorrow.value],
        [TextBtnTransport.back_to_menu.value]
    ]


class ReplySettingsButtons(ReplyMarkupButtons):
    ''' Кнопки для настроек '''
    buttons = [
        [TextBtnSettings.change_city.value,],
        [TextBtnSettings.change_from_station.value, TextBtnSettings.change_to_station.value],
        [TextBtnSettings.back_to_menu.value],
    ]


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
    user = find_else_create_user(msg)

    if text == TextBtn.weather.value.lower():
        msg_text = 'Погода'
        reply_markup = ReplyWeatherButtons().reply_markup()
    elif text == TextBtn.routes.value.lower():
        msg_text = 'Транспорт'
        reply_markup = ReplyTransportButtons().reply_markup()
    elif text == TextBtn.settings.value.lower():
        msg_text = 'Настройки'
        reply_markup = ReplySettingsButtons().reply_markup()
    elif text == TextBtnWeather.weather_today.value.lower():
        locality = find_locality(user.city)
        weather = get_weather(locality)
        msg_text = weather
        reply_markup = {}
    elif text == TextBtnWeather.weather_tomorrow.value.lower():
        locality = find_locality(user.city)
        tomorrow_date = (datetime.now(tz=TZ_UTC_3) + timedelta(days=1)).date()
        weather = get_weather(locality, tomorrow_date)
        msg_text = weather
        reply_markup = {}
    elif text == TextBtnTransport.from_to.value.lower():
        msg_text = get_schedule(from_station=user.from_station,
                                to_station=user.to_station,
                                dt=datetime.now(tz=TZ_UTC_3))
        reply_markup = {}
    elif text == TextBtnTransport.to_from.value.lower():
        msg_text = get_schedule(from_station=user.to_station,
                                to_station=user.from_station,
                                dt=datetime.now(tz=TZ_UTC_3))
        reply_markup = {}
    elif text == TextBtnTransport.from_to_tomorrow.value.lower():
        msg_text = get_schedule(from_station=user.from_station,
                                to_station=user.to_station,
                                dt=datetime.now(tz=TZ_UTC_3)+timedelta(days=1),
                                filtered=False)
        reply_markup = {}
    elif text == TextBtnTransport.to_from_tomorrow.value.lower():
        msg_text = get_schedule(from_station=user.to_station,
                                to_station=user.from_station,
                                dt=datetime.now(tz=TZ_UTC_3)+timedelta(days=1),
                                filtered=False)
        reply_markup = {}
    elif text == TextBtnSettings.change_city.value.lower():
        msg_text = 'Введи название города:'
        reply_markup = {}
        bot.wait_user_message(chat_id=msg.user.id,
                              message=msg_text,
                              callback=change_user_city)
        return
    elif text == TextBtnSettings.change_from_station.value.lower():
        msg_text = 'Введи название станции отправления'
        reply_markup = {}
        bot.wait_user_message(chat_id=msg.user.id,
                              message=msg_text,
                              callback=change_user_from_station)
        return
    elif text == TextBtnSettings.change_to_station.value.lower():
        msg_text = 'Введи название станции прибытия'
        reply_markup = {}
        bot.wait_user_message(chat_id=msg.user.id,
                              message=msg_text,
                              callback=change_user_to_station)
        return
    elif text == TextBtnSettings.back_to_menu.value.lower():
        msg_text = 'Меню'
        reply_markup = ReplyStartButtons().reply_markup()
    else:
        msg_text = 'Неизвестная команда'
        reply_markup={}

    bot.send_message(chat_id=msg.user.id,
                     message=msg_text,
                     reply_markup=reply_markup,
                     parse_mode='Markdown')


def get_schedule(from_station: str, to_station: str, dt: datetime, filtered: bool=True) -> str:
    '''
    Получить расписание между станциями from_station и to_station на дату dt.

    :param from_station: - yandex код станции отправления;
    :param to_station: - yandex код станции прибытия;
    :param dt: - дата на которую необходимо получить расписание;
    :param filtered: - True, если необходимо убрать ушедший транспорт.
    :returns: строка с расписанием.
    '''
    if None in (from_station, to_station):
        msg_text = f'Чтобы получить расписание надо выбрать станции отправления и прибытия!'
    else:
        routes = get_route(from_station, to_station, dt)
        if filtered:
            routes = tuple(filter(lambda r: r.start_dt > dt, routes))
        prev_msg_text, next_msg_text = get_route_text(routes).split(':', maxsplit=1)
        dt_str = dt.strftime("%d.%m.%Y")
        msg_text = prev_msg_text + f' на {dt_str}:' + next_msg_text
    return msg_text


def get_route(station_1: str, station_2: str, dt: datetime=None) -> List[str]:
    '''
    Получить расписание транспорта между Станциями.

    :param station_1: - yandex_code станции отправления;
    :param station_2: - yandex_code станции прибытия.
    :returns: Список строк с данными о времени отправления и прибытия.
    '''
    if dt is None:
        dt = datetime.now(tz=TZ_UTC_3)
    rasp_api = YandexRaspAPI()
    routes = rasp_api.get_routes(station_1, station_2, dt)
    return routes


def get_route_text(routes: List[Route]) -> str:
    '''
    Преобразовать список Маршрутов в читаемую строку с расписанием.

    :param routes: - список Маршрутов.
    :returns: строка с расписанием маршрутов.
    '''
    if not routes:
        return 'Расписание между выбранными станциями отсутствует. ' + \
               'Возможно выбраны неправильные станции, либо сегодня рейсов не будет.'

    transport_emoji = TRANSPORT_EMOJI.get(routes[0].transport_type, '')
    from_station = routes[0].from_station
    from_station_text = f'{transport_emoji}{from_station.title}'
    to_station = routes[0].to_station
    to_station_text = f'{transport_emoji}{to_station.title}'

    output = f'Расписание между "{from_station_text}" и "{to_station_text}":\n'
    output = '\n'.join((output, *map(str, routes)))

    return output


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


def change_user_from_station(msg: tg_bot.Message) -> None:
    ''' Сменить станцию отправления пользователя '''
    if msg.text.lower() == 'отмена':
        bot.send_message(chat_id=msg.user.id,
                         message='Отмена смены станции отправления',
                         reply_markup=ReplySettingsButtons().reply_markup())
    elif not msg.text:
        bot.send_message(chat_id=msg.user.id,
                         message='Поле не может быть пустым',
                         reply_markup={})
    stations = find_station(msg.text)
    inline_buttons = bot.create_inline_keyboard([
        [{'text': station.title, 'callback_data': f'from_station {station.yandex_code}'},]
        for station in stations
    ])
    bot.send_message(chat_id=msg.user.id,
                     message='Найдены следующие станции:',
                     reply_markup=inline_buttons)


def change_user_to_station(msg: tg_bot.Message) -> None:
    ''' Сменить станцию прибытия пользователя '''
    if msg.text.lower() == 'отмена':
        bot.send_message(chat_id=msg.user.id,
                         message='Отмена смены станции прибытия',
                         reply_markup=ReplySettingsButtons().reply_markup())
    elif not msg.text:
        bot.send_message(chat_id=msg.user.id,
                         message='Поле не может быть пустым',
                         reply_markup={})
    stations = find_station(msg.text)
    inline_buttons = bot.create_inline_keyboard([
        [{'text': station.title, 'callback_data': f'to_station {station.yandex_code}'}]
        for station in stations
    ])
    bot.send_message(chat_id=msg.user.id,
                     message='Найдены следующие станции:',
                     reply_markup=inline_buttons)


@bot.callback_query()
def callback_query(query: 'CallbackQuery') -> None:
    ''' Обработчик неизвестных CallbackQuery '''
    if re.search(r'from_station s\d{7}', query.data):
        change_selected_station(query, 'from_station')
    elif re.search(r'to_station s\d{7}', query.data):
        change_selected_station(query, 'to_station')


def change_selected_station(query, station_arg: str='from_station') -> None:
    ''' Изменить станцию на выбранную пользователем '''
    user = find_else_create_user(query)
    old_user_station = find_station(station_yandex_code=getattr(user, station_arg))
    yandex_code = re.findall(r's\d{7}', query.data)[0]
    station = find_station(station_yandex_code=yandex_code)
    station_type = 'отправления' if station_arg=='from_station' else 'прибытия'

    update(entry=user, arg=station_arg, value=station.yandex_code)
    if old_user_station is None:
        msg_text = f'Станция {station_type} установлена на ' + \
                   f'"[{station.yandex_code}] {station.title}"'
    else:
        msg_text = f'Станция {station_type} изменена с "[{old_user_station.yandex_code}] ' + \
                   f'{old_user_station.title}" на "[{station.yandex_code}] {station.title}"'

    bot.send_message(query.user.id, msg_text, reply_markup={})


@bot.command(name='update_stations')
def stations_command(msg: tg_bot.Message) -> None:
    update_stations()
    bot.send_message(chat_id=msg.user.id,
                     message='Станции обновлены',
                     reply_markup={})


# @bot.command(name='exit')
# def exit_command(msg: tg_bot.Message) -> None:
#     sys.exit()
