from flask_pymongo import PyMongo
from bson import ObjectId

# Khởi tạo object PyMongo nhưng chưa gắn vào app ngay
mongo = PyMongo()

def init_db(app):
    mongo.init_app(app)

# Helper function để chuyển đổi ObjectId sang String (cho JSON response)
def serialize_doc(doc):
    if not doc:
        return None
    doc['_id'] = str(doc['_id'])
    return doc