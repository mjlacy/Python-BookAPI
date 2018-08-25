from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from pymongo.results import InsertOneResult, UpdateResult, DeleteResult
from bson.objectid import ObjectId
from bson.errors import InvalidId


def _getClient():
    client = MongoClient('mongodb://localhost:27017', connect=False, readPreference='secondaryPreferred')
    print(client.read_preference)
    return client


client = _getClient()
database = 'books'
collection = 'books'


def get_books():
    try:
        result = client[database][collection].find()
        if result is None:
            return []
        else:
            return result
    except (InvalidId, TypeError) as ex:
        print(ex)
        return []


def get_book(object_id):
    try:
        obj_id = ObjectId(object_id)
        result = client[database][collection].find_one({"_id": obj_id})
        if result is None:
            return []
        else:
            return result
    except (InvalidId, TypeError) as ex:
        print(ex)
        return []


def post_book(body):
    try:
        if "_id" in body:
            body['_id'] = ObjectId(body['_id'])

        result = client[database][collection].insert_one(body)
        return result

    except InvalidId:
        return 400

    except DuplicateKeyError:
        return 409

    except Exception as e:
        print(e)
        return InsertOneResult(False, False)


def put_book(object_id, body):
    try:
        body.pop('_id', None)

        obj_id = ObjectId(object_id)
        result = client[database][collection].update_one({"_id": obj_id}, {'$set': body}, upsert=True)
        return result

    except Exception as e:
        print(e)
        return UpdateResult(False, False)


def delete_book(object_id):
    try:
        obj_id = ObjectId(object_id)
        result = client[database][collection].delete_one({"_id": obj_id})
        return result

    except Exception as e:
        print(e)
        return DeleteResult(False, False)