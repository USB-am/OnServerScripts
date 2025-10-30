# -*- coding: utf-8 -*-

import sys
import threading
from typing import Dict, Callable

from src import tg_bot
from src.tg_bot.initializer import TelegramBot


tg_bot.load_config('config.json')
bot = TelegramBot()
import custom_tg_bot as CustomBot


class Schedule:
    def __init__(self):
        self._callbacks: Dict[str, Callable] = {}

    def at(self, period: str) -> object:
        '''
        Получить объект для добавления события.

        :param period: раз в сколько будет запускаться событие.
        :returns: объект для добавления события.
        '''


# class SSTelegramAPI(tg_bot.TelegramAPI):
#     ''' Надстройка над основным классом бота '''


# class Application(SSTelegramAPI, Schedule):
#   ''' Главная надстройка '''

#   def __init__(self):
#       SSTelegramAPI.__init__(self)
#       Schedule.__init__(self)


def app_exit() -> None:
    ''' Остановить приложение '''
    bot.close()
    sys.exit()


if __name__ == '__main__':
    # app = Application()
    bot.listen()
