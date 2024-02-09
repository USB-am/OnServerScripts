from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tg_bot.db'

db = SQLAlchemy(app)


class TelegramUser(db.Model):
	''' Информация о пользователе бота '''

	__tablename__ = 'telegram_user'
	id = db.Column(db.Integer, primary_key=True)
	chat_id = db.Column(db.Integer, unique=True)
	name = db.Column(db.String(255), nullable=False)
	city = db.Column(db.String(255), default='Москва', nullable=True)

	def __str__(self):
		return f'<TelegramUser \'{self.name}\'>'


class Station(db.Model):
	''' Информация о станции электрички '''

	__tablename__ = 'train_station'
	id = db.Column(db.Integer, primary_key=True)
	yandex_code = db.Column(db.String(63), unique=True)
	esr_code = db.Column(db.String(63), nullable=True)
	title = db.Column(db.String(255), nullable=False)
	type = db.Column(db.String(255), nullable=True)
	transport = db.Column(db.String(63), nullable=False)
	settlement = db.Column(db.String(255), nullable=True)
	region = db.Column(db.String(255), nullable=True)
	country = db.Column(db.String(255), nullable=False)

	def __str__(self):
		return f'<{self.type.title()}Station "{self.title}" ({self.transport})>'


# db.create_all()