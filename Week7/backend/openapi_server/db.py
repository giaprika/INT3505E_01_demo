from __future__ import annotations
import os
from pymongo import MongoClient
from pymongo.errors import PyMongoError

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DB = os.getenv("MONGODB_DB", "library")

_client = None
_db = None


def init_db(uri=None, db_name=None):
    global _client, _db

    if MongoClient is None:
        raise RuntimeError("pymongo is not installed. Add pymongo to requirements.")

    if _client is None:
        uri = uri or MONGODB_URI
        db_name = db_name or MONGODB_DB
        _client = MongoClient(uri)
        try:
            _client.admin.command("ping")
        except PyMongoError:
            raise
        _db = _client[db_name]

    return _db


def get_client():
    if _client is None:
        init_db()
    return _client


def get_db():
    if _db is None:
        init_db()
    return _db


def get_collection(name: str):
    db = get_db()
    return db[name]


def get_next_sequence(name: str) -> int:
    client = get_client()
    db = get_db()
    counters = db['counters']
    doc = counters.find_one_and_update(
        {'_id': name},
        {'$inc': {'seq': 1}},
        upsert=True,
        return_document=True
    )
    if doc is None:
        counters.update_one({'_id': name}, {'$setOnInsert': {'seq': 1}}, upsert=True)
        doc = counters.find_one({'_id': name})
    return int(doc.get('seq', 1))


__all__ = ["init_db", "get_client", "get_db", "get_collection"]
