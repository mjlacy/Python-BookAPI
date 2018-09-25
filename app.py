import data
from flask import Flask, request, Response, json, jsonify
from flask_cors import CORS
from bson.errors import InvalidId
from pymongo.errors import DuplicateKeyError

app = Flask(__name__)
CORS(app)


@app.route('/health')
def health():
    return 'ok'


@app.route('/', methods=['GET'])
def get_all_books():
    try:
        books = {"books": data.get_books()}
        return Response(json.dumps(books), status=200, mimetype='application/json')

    except Exception as e:
        print(e)
        return jsonify(error=str(e)), 500


@app.route('/<object_id>', methods=['GET'])
def get_one_book(object_id):
    try:
        book = data.get_book(object_id)

        if book is None:
            return jsonify(error="No book with an _id of " + object_id + " found"), 404

        return Response(json.dumps(book), status=200, mimetype='application/json')

    except InvalidId as ex:
        print(ex)
        return jsonify(error="The _id you specified is not a valid ObjectId, "
                               "it must be a 12-byte input or 24-character hex string"), 400

    except Exception as e:
        print(e)
        return jsonify(error=str(e)), 500


@app.route('/', methods=['POST'])
def create_book():
    try:
        result = data.post_book(request.get_json())
        return jsonify(link='/' + str(result.inserted_id)), 201

    except InvalidId:
        return jsonify(error="The _id you specified is not a valid ObjectId, "
                       "it must be a 12-byte input or 24-character hex string"), 400

    except DuplicateKeyError:
        return jsonify(error="The _id you specified already exists, please choose a different one"), 409

    except Exception as e:
        print(e)
        return jsonify(error=str(e)), 500


@app.route('/<object_id>', methods=['PUT'])
def update_book(object_id):
    try:
        result = data.put_book(object_id, request.get_json())

        if result.upserted_id is not None:
            return jsonify(link='/' + str(result.upserted_id)), 201

        return jsonify(link='/' + object_id)

    except InvalidId:
        return jsonify(error="The _id you specified is not a valid ObjectId, "
                               "it must be a 12-byte input or 24-character hex string"), 400

    except Exception as e:
        print(e)
        return jsonify(error=str(e)), 500


@app.route('/<object_id>', methods=['DELETE'])
def delete_one_book(object_id):
    try:
        if data.get_book(object_id) is None:
            return jsonify(error="No book with an _id of " + object_id + " found to delete"), 404

        data.delete_book(object_id)
        return jsonify(message="Object with id: " + object_id + " deleted successfully"), 200

    except InvalidId:
        return jsonify(error="The _id you specified is not a valid ObjectId, "
                               "it must be a 12-byte input or 24-character hex string"), 400

    except Exception as e:
        print(e)
        return jsonify(error=str(e)), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
