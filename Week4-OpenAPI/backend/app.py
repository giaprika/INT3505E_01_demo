from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from models import db
from routes.books import books_bp
from routes.authors import authors_bp
from routes.readers import readers_bp
from routes.records import records_bp
from routes.auth import auth_bp

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.config['JWT_SECRET_KEY'] = 'jwt-secret'
    jwt = JWTManager(app)

    db.init_app(app)

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(books_bp, url_prefix='/api/books')
    app.register_blueprint(authors_bp, url_prefix='/api/authors')
    app.register_blueprint(readers_bp, url_prefix='/api/readers')
    app.register_blueprint(records_bp, url_prefix='/api/records')


    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({'error': 'Missing or invalid token'}), 401

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
