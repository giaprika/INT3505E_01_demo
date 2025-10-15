from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt
import datetime
from functools import wraps

app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = 'mysecretkey'

books = [
    {"id": 1, "title": "Clean Code", "author": "Robert C. Martin"},
    {"id": 2, "title": "The Pragmatic Programmer", "author": "Andrew Hunt"}
]
users = {"admin": "password"}

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('x-access-token')
        if not token:
            return jsonify({"message": "Token is missing"}), 401
        try:
            jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        except:
            return jsonify({"message": "Token is invalid"}), 401
        return f(*args, **kwargs)
    return decorated


@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if username in users:
        return jsonify({"message": "User exists"}), 400
    users[username] = password
    return jsonify({"message": "User registered successfully"})

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if users.get(username) != password:
        return jsonify({"message": "Invalid credentials"}), 401
    token = jwt.encode({'user': username, 
                        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, 
                       app.config['SECRET_KEY'], algorithm="HS256")
    return jsonify({"token": token})

@app.route('/books', methods=['GET'])
@token_required
def get_books():
    response = jsonify(books)
    response.headers['Cache-Control'] = 'public, max-age=3600'
    return response

@app.route('/books', methods=['POST'])
@token_required
def add_book():
    data = request.json
    new_book = {
        "id": len(books) + 1,
        "title": data['title'],
        "author": data['author']
    }
    books.append(new_book)
    return jsonify(new_book), 201

@app.route('/books/<int:book_id>', methods=['PUT'])
@token_required
def update_book(book_id):
    data = request.json
    for book in books:
        if book["id"] == book_id:
            book["title"] = data.get("title", book["title"])
            book["author"] = data.get("author", book["author"])
            return jsonify(book)
    return jsonify({"message": "Book not found"}), 404

@app.route('/books/<int:book_id>', methods=['DELETE'])
@token_required
def delete_book(book_id):
    global books
    books = [book for book in books if book["id"] != book_id]
    return jsonify({"message": "Deleted"})

if __name__ == '__main__':
    app.run(debug=True)
