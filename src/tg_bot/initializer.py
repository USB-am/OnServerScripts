from src.tg_bot import TelegramAPI


class SingletonMeta(type):
    _instance = None

    def __call__(cls, *args, **kwargs):
        if not cls._instance:
            isinstance = super().__call__(*args, **kwargs)
            cls._instance = isinstance
        return cls._instance
    

class TelegramBot(TelegramAPI, metaclass=SingletonMeta):
    pass
