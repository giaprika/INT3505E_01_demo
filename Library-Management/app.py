from flask import Flask, render_template, redirect, url_for, request
from models import db, Book, Borrow
from forms import BookForm, BorrowForm

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SECRET_KEY"] = "secret"
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route("/")
def index():
    books = Book.query.all()
    return render_template("index.html", books=books)

@app.route("/add", methods=["GET", "POST"])
def add_book():
    form = BookForm()
    if form.validate_on_submit():
        book = Book(title=form.title.data, author=form.author.data)
        db.session.add(book)
        db.session.commit()
        return redirect(url_for("index"))
    return render_template("add_book.html", form=form)

@app.route("/borrow/<int:book_id>", methods=["GET", "POST"])
def borrow(book_id):
    book = Book.query.get_or_404(book_id)
    if not book.available:
        return "Sách đã được mượn"
    form = BorrowForm()
    if form.validate_on_submit():
        borrow = Borrow(book_id=book.id, borrower=form.borrower.data)
        book.available = False
        db.session.add(borrow)
        db.session.commit()
        return redirect(url_for("index"))
    return render_template("borrow.html", form=form, book=book)

@app.route("/return/<int:borrow_id>")
def return_book(borrow_id):
    borrow = Borrow.query.get_or_404(borrow_id)
    borrow.returned = True
    book = Book.query.get(borrow.book_id)
    book.available = True
    db.session.commit()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
