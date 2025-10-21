from flask import Flask
from models import db, Author, Book, BookCopy, Reader, Record
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
    authors = [Author(name=f"Author {i}", email=f"author{i}@mail.com", birth_date=datetime(1970+i,1,1)) for i in range(10)]
    books = [Book(title=f"Book {i}", genre=random.choice(["Fiction","Science","History","Tech"]), published_year=2000+i) for i in range(10)]
    copies = [BookCopy(book_id=b.book_id) for b in books]
    readers = [Reader(name=f"Reader {i}", email=f"reader{i}@mail.com", phone=f"090{i:06d}", address=f"Street {i}, City", birth_date=datetime(1990+i%5,5,20)) for i in range(10)]

    db.session.add_all(authors + books + copies + readers)
    db.session.commit()

    # records
    for i in range(10):
        rec = Record(
            book_copy_id=copies[i % len(copies)].book_copy_id,
            reader_id=readers[i % len(readers)].reader_id,
            borrow_date=datetime.now() - timedelta(days=random.randint(1,20)),
            return_date=None if i%3 else datetime.now(),
            status="returned" if i%3==0 else "borrowed"
        )
        db.session.add(rec)
    db.session.commit()

    print("Database initialized with sample data!")
