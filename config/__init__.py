TELEGRAM_TOKEN = '6016831935:AAEc7UlCVY_lbBN1FkI1xcZC3bW5INgmEmg'

WEATHER_API = '643bd4178a21898450416fc86b447bc4'

SCHEDULES_API = 'f5cc9cc8-8f52-4a5e-ae88-d957aede87c0'


import os

# PATHS
BASE_DIR = os.getcwd()

LOGS_DIR = os.path.join(BASE_DIR, 'logs')


# CONSTANTS
MAILING_TIMES = (
	'05:55',	# 08:55
	'08:55',	# 11:55
	'11:55',	# 14:55
	'14:55',	# 17:55
	'17:55',	# 21:55
	'20:55',	# 23:55
)