from flask_sqlalchemy import SQLAlchemy
from datetime import date

db = SQLAlchemy()

class Book(db.Model):
    __tablename__ = 'books'
    book_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    genre = db.Column(db.String(100))
    published_year = db.Column(db.Integer)

class Reader(db.Model):
    __tablename__ = 'readers'
    reader_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    birth_date = db.Column(db.Date)
    join_date = db.Column(db.Date, default=date.today)
