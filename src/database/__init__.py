from typing import Any

from sqlalchemy.exc import IntegrityError

from .models import db, User
from .exceptions import DBError
from tg_bot import Message


def create_user(chat_id: int,
                name: str,
                city: str='Москва',
                from_station: int=None,
                to_station: int=None) -> User:
    ''' Создать пользователя в базе данных '''
    new_user = User(
        chat_id=chat_id,
        name=name,
        city=city,
        from_station=from_station,
        to_station=to_station)
    try:
        db.session.add(new_user)
        db.session.commit()
    except IntegrityError as err:
        db.session.rollback()
        raise DBError(f'There was a problem writing/saving to the DB.\n{err}')
    return new_user


def create_user_by_message(msg: Message) -> User:
    ''' Создать пользователя по сообщению '''
    return create_user(
        chat_id=msg.user.id,
        name=msg.user.username,
        city='Москва',
        from_station=None,
        to_station=None)


def find_user(msg: Message) -> User:
    ''' Найти пользователя по сообщению '''
    return User.query.filter_by(chat_id=msg.user.id).first()


def find_else_create_user(msg: Message) -> User:
    ''' Найти или создать пользователя '''
    user = find_user(msg)
    if user is None:
        user = create_user_by_message(msg)
    return user


def update(entry: db.Model, arg: str, value: Any) -> None:
    setattr(entry, arg, value)
    db.session.commit()
