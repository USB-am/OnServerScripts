import os
from datetime import datetime

from config import LOGS_DIR


def save_log(error: Exception) -> None:
	now_date = datetime.now().date().strftime('%Y%m%d')

	path_to_now_logs = os.path.join(LOGS_DIR, f'{now_date}.log')
	with open(path_to_now_logs, mode='a') as log_file:
		error_text = f'\n[ERROR] {error.__class__.__name__}:'
		for arg in error.args:
			error_text += f'\n\t{arg}'

		log_file.write(error_text)


def logging(func):
	def wrapper(*args, **kwargs):
		try:
			return func(*args, **kwargs)
		except Exception as error:
			save_log(error)

	return wrapper