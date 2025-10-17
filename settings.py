from datetime import timezone, timedelta

TIMEZONE: str = 'Europe/Moscow'
TIMEZONE_OFFSET: int = 3
TZ_UTC_3 = timezone(offset=timedelta(hours=3),
                    name=TIMEZONE)
REQUEST_INTERVAL: int = 3
