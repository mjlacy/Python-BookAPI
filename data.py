from bson import ObjectId
from pymongo import MongoClient


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


def get_books(params):
    def convertObjIdToStr(object):
        object['_id'] = str(object['_id'])
        return object

    result = client[database][collection].find(params)
    if result is None:
        return []
    else:
        return list(map(convertObjIdToStr, result))


def get_book(obj_id):
    if not ObjectId.is_valid(obj_id):
        return None

    result = client[database][collection].find_one({"_id": ObjectId(obj_id)})
    if result is not None:
        result['_id'] = str(result['_id'])

    return result


def create_book(body):
    if '_id' in body:
        if not ObjectId.is_valid(body['_id']):
            return None
        else:
            body['_id'] = ObjectId(body['_id'])

    return client[database][collection].insert_one(body)


def update_book_full(obj_id, body):
    if not ObjectId.is_valid(obj_id):
        return None

    body.pop('_id', None)
    return client[database][collection].replace_one({"_id": ObjectId(obj_id)}, body, upsert=True)


def update_book_partial(obj_id, body):
    if not ObjectId.is_valid(obj_id):
        return None

    body.pop('_id', None)
    return client[database][collection].update_one({"_id": ObjectId(obj_id)}, {'$set': body})


def delete_book(obj_id):
    if not ObjectId.is_valid(obj_id):
        return None

    return client[database][collection].delete_one({"_id": ObjectId(obj_id)})
