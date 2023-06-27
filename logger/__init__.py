import os
from datetime import datetime

from config import LOGS_DIR


def save_log(error: Exception) -> None:
	now_date = datetime.now().date().strftime('YYYYmmdd')

	path_to_now_logs = os.path.join(LOGS_DIR, f'{now_date}.log')
	with open(path_to_now_logs, mode='a') as log_file:
		log_file.write(f'[ERROR] {error.__class__.__name__}: {error.args}')


def logging(func):
	def wrapper(*args, **kwargs):
		try:
			return func(*args, **kwargs)
		except Exception as error:
			save_log(error)

	return wrapper