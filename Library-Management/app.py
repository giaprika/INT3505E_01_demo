from flask import Flask, request, jsonify, make_response
from models import db, Book, Borrow
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

with app.app_context():
    db.create_all()


# ---- RESTful API ----

# GET all books
@app.route("/api/books", methods=["GET"])
def get_books():
    books = Book.query.all()
    data = [{"id": b.id, "title": b.title, "author": b.author, "available": b.available} for b in books]
    
    response = make_response(jsonify(data), 200)
    response.headers["Cache-Control"] = "public, max-age=60"
    response.headers["ETag"] = str(hash(str(data)))
    return response


# GET one book
@app.route("/api/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    book = Book.query.get_or_404(book_id)
    return jsonify({"id": book.id, "title": book.title, "author": book.author, "available": book.available})


# POST create book
@app.route("/api/books", methods=["POST"])
def create_book():
    data = request.json
    if not data or "title" not in data or "author" not in data:
        return jsonify({"error": "Invalid data"}), 400
    
    book = Book(title=data["title"], author=data["author"])
    db.session.add(book)
    db.session.commit()
    return jsonify({"message": "Book created", "id": book.id}), 201


# PUT update book
@app.route("/api/books/<int:book_id>", methods=["PUT"])
def update_book(book_id):
    book = Book.query.get_or_404(book_id)
    data = request.json
    book.title = data.get("title", book.title)
    book.author = data.get("author", book.author)
    book.available = data.get("available", book.available)
    db.session.commit()
    return jsonify({"message": "Book updated"})


# DELETE book
@app.route("/api/books/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    return jsonify({"message": "Book deleted"})


# Borrow book
@app.route("/api/borrow/<int:book_id>", methods=["POST"])
def borrow_book(book_id):
    book = Book.query.get_or_404(book_id)
    if not book.available:
        return jsonify({"error": "Book not available"}), 400
    
    data = request.json
    if not data or "borrower" not in data:
        return jsonify({"error": "Borrower required"}), 400
    
    borrow = Borrow(book_id=book.id, borrower=data["borrower"])
    book.available = False
    db.session.add(borrow)
    db.session.commit()
    return jsonify({"message": "Book borrowed", "borrow_id": borrow.id})


# Return book
@app.route("/api/return/<int:borrow_id>", methods=["PUT"])
def return_book(borrow_id):
    borrow = Borrow.query.get_or_404(borrow_id)
    if borrow.returned:
        return jsonify({"error": "Book already returned"}), 400
    
    borrow.returned = True
    book = Book.query.get(borrow.book_id)
    book.available = True
    db.session.commit()
    return jsonify({"message": "Book returned"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
