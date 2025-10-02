from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tg_bot.db'

db = SQLAlchemy(app)


class Country(db.Model):
    __tablename__ = 'country'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=True)
    yandex_code = db.Column(db.String(20), unique=True)

    def __str__(self):
        return self.title


class Region(db.Model):
    __tablename__ = 'region'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    yandex_code = db.Column(db.String(20), unique=True)
    country = db.Column(db.Integer, db.ForeignKey(Country.id), nullable=True)


class Settlement(db.Model):
    __tablename__ = 'settlement'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    yandex_code = db.Column(db.String(20), unique=True)
    region = db.Column(db.Integer, db.ForeignKey(Region.id), nullable=True)


class Station(db.Model):
    __tablename__ = 'station'
    id = db.Column(db.Integer, primary_key=True)
    yandex_code = db.Column(db.String(20), unique=True)
    title = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(100), nullable=True)
    transport = db.Column(db.String(20), nullable=False)
    settlement = db.Column(db.Integer, db.ForeignKey(Settlement.id), nullable=True)

    def __str__(self):
        return f'<{self.type.title()}Station "{self.title}" ({self.transport})>'


class User(db.Model):
    __tablename__ = 'telegram_user'
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, unique=True)
    name = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(255), default='Москва', nullable=True)
    from_station = db.Column(db.Integer, db.ForeignKey(Station.id), nullable=True)
    to_station = db.Column(db.Integer, db.ForeignKey(Station.id), nullable=True)

    def __str__(self):
        return f'[{self.chat_id}] {self.name}'


db.create_all()
