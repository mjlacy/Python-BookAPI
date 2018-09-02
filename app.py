from bson import ObjectId
from bson.errors import InvalidId
from data import get_books, get_book, post_book, put_book, delete_book
from flask import Flask, request, Response, json, jsonify
from flask_cors import CORS
from pymongo.errors import DuplicateKeyError

app = Flask(__name__)
CORS(app)

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

@app.route('/health')
def health():
    return 'ok'

@app.route('/', methods=['GET'])
def get_all_books():
    try:
        books = {"books": list(map(lambda book: book, get_books()))}
        return Response(JSONEncoder().encode(books), status=200, mimetype='application/json')

    except Exception as e:
        print(e)
        return jsonify(message="An error occurred while processing your request"), 500


@app.route('/<object_id>', methods=['GET'])
def get_one_book(object_id):
    try:
        obj_id = ObjectId(object_id)
        book = get_book(obj_id)
        return Response(JSONEncoder().encode(book), status=200, mimetype='application/json')

    except (InvalidId, TypeError) as ex:
        print(ex)
        return jsonify(message="The _id you specified is not a valid ObjectId, "
                               "it must be a 12-byte input or 24-character hex string"), 400

    except Exception as e:
        print(e)
        return jsonify(message="An error occurred while processing your request"), 500


@app.route('/', methods=['POST'])
def post():
    try:
        result = post_book(request.get_json())
        return jsonify(link='/' + str(result.inserted_id)), 201

    except InvalidId:
        return jsonify(message="The _id you specified is not a valid ObjectId, "
                       "it must be a 12-byte input or 24-character hex string"), 400

    except DuplicateKeyError:
        return jsonify(message="The _id you specified already exists, please choose a different one"), 409

    except Exception as e:
        print(e)
        return jsonify(message="An error occurred while processing your request"), 500


@app.route('/<object_id>', methods=['PUT'])
def put(object_id):
    try:
        obj_id = ObjectId(object_id)
        result = put_book(obj_id, request.get_json())

        if result.upserted_id is not None:
            return jsonify(link='/' + str(result.upserted_id)), 201

        return jsonify(link='/' + object_id)

    except InvalidId:
        return jsonify(message="The _id you specified is not a valid ObjectId, "
                               "it must be a 12-byte input or 24-character hex string"), 400

    except Exception as e:
        print(e)
        return jsonify(message="An error occurred while processing your request"), 500


@app.route('/<object_id>', methods=['DELETE'])
def delete(object_id):
    try:
        obj_id = ObjectId(object_id)
        if len(get_book(obj_id)) == 0:
            return jsonify(message="No object with an id of " + object_id + " found to delete"), 404

        delete_book(obj_id)
        return jsonify(message="Object with id: " + object_id + " deleted successfully"), 200

    except InvalidId:
        return jsonify(message="The _id you specified is not a valid ObjectId, "
                               "it must be a 12-byte input or 24-character hex string"), 400

    except Exception as e:
        print(e)
        return jsonify(message="An error occurred while processing your request"), 500

if __name__ == '__main__':
    app.run()