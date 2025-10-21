from flask import Flask
from flask_cors import CORS
from models import db
from routes.v1.books import books_bp
from routes.v2.books_v2 import books_v2_bp
from routes.v1.readers import readers_bp
from routes.v2.readers_v2 import readers_v2_bp

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    app.register_blueprint(books_bp, url_prefix='/api/books')
    app.register_blueprint(books_v2_bp, url_prefix='/api/v2/books')
    app.register_blueprint(readers_bp, url_prefix='/api/readers')
    app.register_blueprint(readers_v2_bp, url_prefix='/api/v2/readers')

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
