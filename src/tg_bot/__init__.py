# -*- coding: utf-8 -*-

import os
import json
import logging
import threading
from _io import BufferedReader
from dataclasses import dataclass
from typing import Callable, Dict, List
from datetime import datetime, timezone, timedelta

import pytz
import requests
import schedule

import settings


logger = logging.getLogger('TelegramAPI')
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s\t[%(levelname)s]: %(message)s')


class LoggerError(Exception):
    ''' Ошибка логирования '''


class TelegramConnectorException(Exception):
    ''' Ошибка подключения '''


def set_schedule_tz(timezone: str) -> None:
    ''' Установить часовой пояс для плановых функций '''

    class TZSchedule:
        def __init__(self, timezone: str):
            self.tz = pytz.timezone(timezone)

        def now(self) -> datetime:
            return datetime.now(self.tz)

    schedule.default_scheduler.now = TZSchedule(timezone).now


def add_everyday_scheduled(run_times: List[str],
                           callback: Callable,
                           interval: int=1) -> None:
    '''
    Добавить плановый ежедневный запуск.
    Примечание: на каждый запуск создается новый процесс!

    :param run_times: список с временными метками запуска
    :param callback: функция, которая будет запущена
    '''

    for run_time in run_times:
        schedule.every(interval).day.at(run_time).do(callback)


def add_debug_log(func):
    def wrapper(*args, **kwargs):
        logger.debug(f'{func.__name__}. args: {args}; kwargs: {kwargs}')
        try:
            return func(*args, **kwargs)
        except Exception as err:
            raise LoggerError(f'An exception was raised in the {func.__name__}.\n{err}')
    return wrapper


@add_debug_log
def load_config(path_to_config: str) -> None:
    ''' Загружает данные из конфига в память '''
    with open(path_to_config, 'r') as config_file:
        config = json.load(config_file)
        for key, value in config.items():
            os.environ[key] = value


def get_datetime() -> timezone:
    ''' Возвращает текущую дату с учетом часового пояса '''
    offset = settings.TIMEZONE_OFFSET
    offset_delta = timedelta(hours=offset)
    timezone_offset = timezone(offset_delta, name=f'UTC+{offset}')
    return datetime.now(timezone_offset)


@dataclass
class User:
    id: int
    is_bot: bool
    first_name: str
    last_name: str
    username: str

    def __str__(self):
        if self.username:
            return self.username
        return f'{self.first_name} {self.last_name}'


@dataclass
class Message:
    id: int
    user: User
    text: str
    date: int
    command: str = None
    is_command: bool = False

    def __post_init__(self):
        if self.text[0] == '/':
            self.command = self.text
            self.text = self.text[1:]
            self.is_command = True

    def __str__(self):
        return f'[{self.user}] {self.text}'


@dataclass
class CallbackQuery:
    user: User
    data: str

    def __str__(self):
        return f'[{self.user}] {self.data}'


class TelegramAPI:
    url = 'https://api.telegram.org/bot'

    def __init__(self):
        self.token = os.environ['TG_TOKEN']

        self.is_listen = False
        self.listen_process = None
        self.update_id = self._get_last_update_id() + 1

        self._bot_commands: Dict[str, Callable] = {}
        self._bot_callbacks: Dict[str, Callable] = {}
        self._waiting_users: Dict[int, Callable] = {}
        self._text_callback: Callable = lambda msg: None
        self._callback_query_callback: Callable = lambda query: None

    @add_debug_log
    def send_message(self, chat_id: int, message: str,
                     reply_markup: str=None, **kwargs) -> None:
        ''' Отправить сообщение пользователю chat_id '''
        self._send_request(
            url=f'{self.url}{self.token}/sendMessage?chat_id={chat_id}',
            json={
                'text': message,
                'disable_web_page_preview': True,
                'reply_markup': reply_markup,
                **kwargs
            }
        )

        logger.info(f'The bot sent a message to user {chat_id}.')

    @add_debug_log
    def send_photo(self, chat_id: int, photo: BufferedReader=None, url: str=None, text: str='') -> None:
        ''' Отправить фото пользователю chat_id '''
        if photo is None and url is None:
            raise AttributeError('No keyword arguments were passed to photo/url')

        if photo is not None:
            _json = {'caption': text}
            _files = {'photo': photo}
        elif url is not None:
            _json = {'photo': url, 'caption': text}
            _files = {}

        self._send_request(
            url=f'{self.url}{self.token}/sendPhoto?chat_id={chat_id}',
            json=_json,
            files=_files)

    def create_reply_keyboard(self, keyboard: List, resize: bool=True,
                              one_time: bool=False) -> str:
        '''
        Создать json для передачи кнопок

        :param keyboard: - список кнопок для отображения.
        :param resize: - изменять ли размер кнопок.
        :param one_time: - используется при включении ReplyKeyboardMarkup.
        :returns: сериализованный в json словарь.
        '''
        return json.dumps({
            "keyboard": keyboard,
            "resize_keyboard": resize,
            "one_time_keyboard": one_time
        })

    def create_inline_keyboard(self, buttons: List) -> str:
        '''
        Создать кнопки в 1 строку

        :param buttons: список названий кнопок.
        :returns: сериализованный в json список.
        '''
        return json.dumps({
            "inline_keyboard": buttons
        })

    @add_debug_log
    def listen(self) -> None:
        ''' Начать прослушку сообщений пользователей '''
        if self.is_listen:
            logger.debug('TelegramAPI is listen messages')
            return

        self.is_listen = True
        self.listen_process = threading.Thread(
            name='listen_process',
            target=self._listen,
            args=[],
            kwargs={})
        self.listen_process.start()

    def _listen(self) -> None:
        ''' Получает сообщения от пользователей '''
        logger.info('TelegramAPI is started')

        while self.is_listen:
            updates = self._get_updates().json().get('result', [])

            for update in updates:
                if not update:
                    continue
                if 'message' in update:
                    message = self._get_message(update)
                    if message.is_command and message.text in self._bot_commands.keys():
                        self._bot_commands[message.text](message)
                    elif not message.is_command and message.user.id in self._waiting_users:
                        self._waiting_users[message.user.id](message)
                    else:
                        self._text_callback(message)
                elif 'callback_query' in update:
                    try:
                        callback = self._get_callback(update)
                        self._bot_callbacks[callback.data](callback)
                    except KeyError:
                        self._callback_query_callback(callback)
                self.update_id = update['update_id'] + 1

            schedule.run_pending()
        self.close()

    @add_debug_log
    def _get_message(self, update: Dict) -> Message:
        ''' Получить объект сообщения '''
        message = update['message']
        message_id = message['message_id']
        message_date = message['date']

        from_user = message['from']
        user_id = from_user['id']
        user_is_bot = from_user['is_bot']
        user_first_name = from_user['first_name']
        user_last_name = from_user['last_name']
        user_username = from_user['username']

        message_from_user = User(id=user_id,
                                 is_bot=user_is_bot,
                                 first_name=user_first_name,
                                 last_name=user_last_name,
                                 username=user_username)
        try:
            message_text = message['text']
        except KeyError as err:
            logger.info(f'User {message_from_user} sent a non-text message.')
            message_text = ''
        msg = Message(id=message_id,
                      user=message_from_user,
                      text=message_text,
                      date=message_date)
        return msg

    def _get_callback(self, update: Dict) -> CallbackQuery:
        '''
        Получить объект CallbackQuery от пользователя.

        :param update: словарь с данными о нажатой кнопке
        :returns: объект CallbackQuery.
        '''
        query = update['callback_query']
        from_user = query['from']

        user = User(id=from_user['id'],
                    is_bot=from_user['is_bot'],
                    first_name=from_user['first_name'],
                    last_name=from_user['last_name'],
                    username=from_user['username'])
        data = query['data']

        return CallbackQuery(user=user, data=data)

    def _get_updates(self):
        resp = self._send_request(
            url=f'{self.url}{self.token}/getUpdates',
            params={'offset': self.update_id,
                    'timeout': settings.REQUEST_INTERVAL}
        )
        return resp

    def _send_request(self, **kwargs) -> requests.Response:
        resp = requests.post(**kwargs)
        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise TelegramConnectorException(e)
        return resp

    @add_debug_log
    def close(self):
        ''' Завершить работу бота '''
        self.is_listen = False

    def command(self, name: str) -> None:
        def decorator(func):
            self._bot_commands[name] = func
        return decorator

    def callback(self, name: str) -> None:
        def decorator(func):
            self._bot_callbacks[name] = func
        return decorator

    def text(self) -> None:
        def decorator(func):
            self._text_callback = func
        return decorator
    
    def callback_query(self) -> None:
        def decorator(func):
            self._callback_query_callback = func
        return decorator

    def _delete_from_waiting(self, message: Message, callback: Callable) -> None:
        callback(message)
        del self._waiting_users[message.user.id]

    def wait_user_message(self, chat_id: int, message: str, callback: Callable) -> None:
        ''' 
        Ожидание ввода сообщения от пользователя.

        :param chat_id: id пользователя, которому будет направлено сообщение
        :param message: текст сообщения, который будет отправлен пользователю
        :param callback: функция, которая будет вызвана после ввода пользователем текста
        '''
        self.send_message(chat_id, message, reply_markup={})
        self._waiting_users[chat_id] = lambda msg: self._delete_from_waiting(msg, callback)

    def _get_last_update_id(self) -> int:
        ''' Получить последний update_id '''
        response = self._send_request(url=f'{self.url}{self.token}/getUpdates?limit=1&offset=-1').json()
        try:
            update_id = response['result'][0]['update_id']
        except IndexError:
            update_id = 0
        return update_id
