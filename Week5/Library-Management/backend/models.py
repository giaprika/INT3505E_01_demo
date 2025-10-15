from flask_sqlalchemy import SQLAlchemy
from datetime import date

db = SQLAlchemy()

class Book(db.Model):
    __tablename__ = 'books'
    book_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    genre = db.Column(db.String(100))
    published_year = db.Column(db.Integer)
    copies = db.relationship('BookCopy', backref='book', cascade='all, delete')
    authors = db.relationship('Author', secondary='book_authors', back_populates='books')

class BookCopy(db.Model):
    __tablename__ = 'book_copies'
    book_copy_id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id', ondelete='CASCADE'))
    available = db.Column(db.Boolean, default=True)
    records = db.relationship('Record', backref='book_copy', cascade='all, delete')

class Author(db.Model):
    __tablename__ = 'authors'
    author_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))
    birth_date = db.Column(db.Date)
    books = db.relationship('Book', secondary='book_authors', back_populates='authors')

class BookAuthor(db.Model):
    __tablename__ = 'book_authors'
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id', ondelete='CASCADE'), primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.author_id', ondelete='CASCADE'), primary_key=True)

class Reader(db.Model):
    __tablename__ = 'readers'
    reader_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    birth_date = db.Column(db.Date)
    join_date = db.Column(db.Date, default=date.today)
    records = db.relationship('Record', backref='reader', cascade='all, delete')

class Record(db.Model):
    __tablename__ = 'records'
    record_id = db.Column(db.Integer, primary_key=True)
    book_copy_id = db.Column(db.Integer, db.ForeignKey('book_copies.book_copy_id', ondelete='CASCADE'))
    reader_id = db.Column(db.Integer, db.ForeignKey('readers.reader_id', ondelete='CASCADE'))
    borrow_date = db.Column(db.Date, nullable=False)
    return_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='Borrowed')
