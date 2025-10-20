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


if __name__ == '__main__':
    schedule_obj = Schedule()
    # schedule_obj.add_event(name='send_weather', callback='bot.send_weather')
    # bot.listen()
