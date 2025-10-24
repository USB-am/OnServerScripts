# -*- coding: utf-8 -*-

import threading
from typing import Dict, Callable

from src import tg_bot
tg_bot.load_config('config.json')


bot = tg_bot.TelegramAPI()


class Schedule:
    def __init__(self):
        self._callbacks: Dict[str, Callable] = {}
        
    def at(self, period: str) -> object:
        '''
        Получить объект для добавления события.
        
        :param period: раз в сколько будет запускаться событие.
        :returns: объект для добавления события.
        '''


class SSTelegramAPI(tg_bot.TelegramAPI):
    ''' Надстройка над основным классом бота '''


if __name__ == '__main__':
    tg_api = SSTelegramAPI()
