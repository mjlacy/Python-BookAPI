from pymongo import MongoClient
from bson.objectid import ObjectId


def _getClient():
    try:
        client = MongoClient('mongodb://localhost:27017', connect=False, readPreference='secondaryPreferred')
        print(client.read_preference)
        return client
    except Exception as e:
        print("Error connecting to Mongo")
        return None


client = _getClient()
database = 'books'
collection = 'books'


def get_books():
    result = client[database][collection].find()
    if result is None:
        return []
    else:
        return result


def get_book(obj_id):
    result = client[database][collection].find_one({"_id": obj_id})
    if result is None:
        return []
    else:
        return result


def post_book(body):
    if "_id" in body:
        body['_id'] = ObjectId(body['_id'])

    result = client[database][collection].insert_one(body)
    return result


def put_book(obj_id, body):
    body.pop('_id', None)
    result = client[database][collection].update_one({"_id": obj_id}, {'$set': body}, upsert=True)
    return result


def delete_book(obj_id):
    result = client[database][collection].delete_one({"_id": obj_id})
    return result
