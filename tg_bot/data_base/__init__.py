from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tg_bot.db'

db = SQLAlchemy(app)


class TelegramUser(db.Model):
	''' Информация о пользователе бота '''

	__tablename__ = 'telegram_user'
	# id = db.Column(db.Integer, primary_key=True)
	chat_id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(255), nullable=False)
	city = db.Column(db.String(255), default='Москва', nullable=True)

	def __str__(self):
		return f'<TelegramUser \'{self.name}\'>'


db.create_all()