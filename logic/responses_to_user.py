import enum
from typing import List

from src.tg_bot import Message
from src.tg_bot.initializer import TelegramBot
from src.weather_api import find_locality, get_weather
from src.database import find_else_create_user, update


bot  = TelegramBot()
CANCEL_TEXT = 'Отмена'


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


def weather_response(msg: Message) -> None:
    ''' Отправить пользователю погоду в его регионе '''
    user = find_else_create_user(msg)

    locality = find_locality(user.city)
    weather = get_weather(locality)
    bot.send_message(chat_id=msg.user.id,
                     message=weather,
                     reply_markup={},
                     parse_mode='Markdown')
    

def move_to_menu(msg: Message) -> None:
    ''' Перевести пользоватя в меню '''
    msg_text = 'Меню'
    chat_id = msg.user.id
    keyboard = bot.create_reply_keyboard(ReplySettingsButtons().reply_markup())
    bot.send_message(chat_id=chat_id,
                     message=msg_text,
                     reply_markup=keyboard)


def move_to_settings(msg: Message) -> None:
    ''' Перевести пользователя в настройки '''
    msg_text = 'Настройки'
    keyboard = bot.create_reply_keyboard(ReplySettingsButtons().reply_markup())
    bot.send_message(chat_id=msg.user.id,
                     message=msg_text,
                     reply_markup=keyboard)
    

def change_user_city(msg: Message) -> None:
    ''' Сменить город пользователя '''
    msg_text = f'Введи название города.\nДля отмены действия введи "{CANCEL_TEXT}"'
    bot.wait_user_message(chat_id=msg.user.id,
                          message=msg_text,
                          callback=_update_city_data)


def _update_city_data(msg: Message) -> None:
    ''' Обновить город пользователя в БД '''
    msg_text = msg.text
    chat_id = msg.user.id
    if msg_text.lower() == CANCEL_TEXT.lower():
        bot.send_message(chat_id=chat_id,
                         message='Смена города была отменена',
                         reply_markup={})
        return

    user = find_else_create_user(msg)
    old_city_title = user.city
    try:
        update(user, 'city', msg.text)
        bot.send_message(chat_id=chat_id,
                        message=f'Город был изменен с *{old_city_title}* на *{msg_text}*',
                        reply_markup={},
                        parse_mode='Markdown')
    except:
        bot.send_message(chat_id=chat_id,
                         message='Произошла ошибка при попытке смены города!\n' +
                                 'Попробуй позже или ввести другой город.',
                         reply_markup={})
