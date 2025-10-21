from flask import Flask
from models import db, Book, Reader
from datetime import datetime, timedelta
import random


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.drop_all()
    db.create_all()

    # tạo sample data
    books = [Book(title=f"Book {i}", genre=random.choice(["Fiction","Science","History","Tech"]), published_year=2000+i) for i in range(10)]
    readers = [Reader(name=f"Reader {i}", email=f"reader{i}@mail.com", phone=f"090{i:06d}", address=f"Street {i}, City", birth_date=datetime(1990+i%5,5,20)) for i in range(10)]

    db.session.add_all(books)
    db.session.commit()

    print("Database initialized with sample data!")
