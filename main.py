# -*- coding: utf-8 -*-

import sys
import enum
from typing import Callable

import schedule

from src import tg_bot
from src.tg_bot.initializer import TelegramBot
from src.database import get_all_users


tg_bot.load_config('config.json')
bot = TelegramBot()
import custom_tg_bot as CustomBot


class Unit(enum.Enum):
    ''' Единица времени '''
    seconds = 'seconds'
    minutes = 'minutes'
    hours = 'hours'
    days = 'days'
    weeks = 'weeks'
    monday = 'monday'
    tuesday = 'tuesday'
    wednesday = 'wednesday'
    thursday = 'thursday'
    friday = 'friday'
    saturday = 'saturday'
    sunday = 'sunday'


class Schedule:
    def add_repeat_job(self, callback: Callable, interval: int=1,
                       unit: str=Unit.days.value, tags: tuple=(),
                       **kwargs) -> None:
        '''
        Добавить повторяющееся событие, которое будет выполняться
        каждые interval раз в unit.

        :param callback: событие, которое будет вызвано;
        :param interval: интервал, с которым будет вызвано событие;
        :param unit: единица интервала, с которым будет вызвано событие;
        :param tags: теги, для быстрого нахождения события в будущем;
        :param **kwargs: аргументы для вызова события callback.
        :returns: None
        '''

        new_job = schedule.every(interval)
        new_job.unit = unit
        new_job.do(callback, **kwargs).tag(*tags)

    def add_repeat_at_job(self, callback: Callable, at_time: str,
                          unit: str=Unit.days.value, tags: tuple=(),
                          **kwargs) -> None:
        '''
        Добавить повторяющееся событие, которое будет выполняться
        раз в unit во вреия at_time.

        :param callback: событие, которое будет вызвано;
        :param at_time: время в формате "HH:MM:SS", в которое будет вызвано событие;
        :param unit: единица интервала, с которым будет вызвано событие;
        :param tags: теги, для быстрого нахождения события в будущем;
        :param **kwargs: аргументы для вызова события callback.
        :returns: None
        '''

        new_job = schedule.every()
        new_job.unit = unit
        new_job.at(at_time)
        new_job.do(callback, **kwargs).tag(*tags)

    def add_once_job(self, callback: Callable, interval: int=1,
                     unit: str=Unit.days.value, tags: tuple=(),
                     **kwargs) -> schedule.CancelJob:
        '''
        Добавить событие которое будет выполнено 1 раз через interval времени.

        :param callback: событие, которое будет вызвано;
        :param interval: интервал, через который будет вызвано событие;
        :param unit: единица интервала, с которым будет вызвано событие;
        :param tags: теги, для быстрого нахождения события в будущем;
        :param **kwargs: аргументы для вызова события callback.
        :returns: объект для удаления из планировщика задач
        '''

        self.add_repeat_job(callback, interval, unit, tags, **kwargs)
        return schedule.CancelJob

    def add_once_at_job(self, callback: Callable, at_time: str,
                        unit: str=Unit.days.value, tags: tuple=(),
                        **kwargs) -> schedule.CancelJob:
        '''
        Добавить событие которое будет выполнено 1 раз в at_time.

        :param callback: событие, которое будет вызвано;
        :param at_time: время в формате "HH:MM:SS", в которое будет вызвано событие;
        :param unit: единица интервала, с которым будет вызвано событие;
        :param tags: теги, для быстрого нахождения события в будущем;
        :param **kwargs: аргументы для вызова события callback.
        :returns: объект для удаления из планировщика задач
        '''

        self.add_repeat_at_job(callback, at_time, unit, tags, **kwargs)
        return schedule.CancelJob


class Callbacks:
    def send_message_all_users(self, message_text: str) -> Callable:
        ''' Отправить сообщение всем пользователям '''
        for user in get_all_users():
            bot.send_message(chat_id=user.chat_id,
                             message=message_text,
                             reply_markup={},
                             parse_mode='Markdown')


jobs = Schedule()


def bot_start() -> None:
    ''' Начать работу бота '''
    if not bot.is_listen:
        bot.listen()
    else:
        print('Бот уже запущен')


def bot_stop() -> None:
    ''' Остановить работу бота '''
    if bot.is_listen:
        bot.close()
    else:
        print('Бот уже остановлен')


def app_exit() -> None:
    ''' Остановить приложение '''
    bot.close()
    sys.exit()


def help() -> None:
    '''
    Выводит строку с командами, используемыми в терминале.

    Т.к. запуск осуществляется через команду "python -i main.py", а данная
    функция будет выполняться только через терминал,
    вместо return используется print.
    '''
    cmds = (bot_start, bot_stop, app_exit,)
    output = 'Доступные команды:'
    for cmd in cmds:
        output += '\n' + cmd.__name__ + ' - ' + cmd.__doc__

    print(output)


if __name__ == '__main__':
    bot_start()
