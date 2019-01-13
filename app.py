import data
from flask import Flask, request, Response, json, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route('/health')
def health():
    return 'ok'


@app.route('/', methods=['GET'])
def get_all_books():
    try:
        params = {}
        bookId = request.args.get('bookId')
        if bookId is not None:
            params['bookId'] = int(bookId)
        title = request.args.get('title')
        if title is not None:
            params['title'] = title
        author = request.args.get('author')
        if author is not None:
            params['author'] = author
        year = request.args.get('year')
        if year is not None:
            params['year'] = int(year)

        books = {"books": data.get_books(params)}
        return Response(json.dumps(books), status=200, mimetype='application/json')

    except Exception as e:
        print(e)
        return jsonify(error=str(e)), 500


@app.route('/<object_id>', methods=['GET'])
def get_one_book(object_id):
    try:
        book = data.get_book(object_id)

        if book is None:
            return jsonify(error="No book with an id of " + object_id + " found"), 404

        resp = Response(json.dumps(book), status=200, mimetype='application/json')
        resp.headers['Location'] = f'/{object_id}'
        resp.autocorrect_location_header = False
        return resp

    except Exception as e:
        print(e)
        return jsonify(error=str(e)), 500


@app.route('/', methods=['POST'])
def create_one_book():
    try:
        book = request.get_json()
        result = data.create_book(book)

        if result is None:
            return jsonify(error="The id specified is not a valid id"), 400

        if "_id" in book:
            book['_id'] = str(book['_id'])

        resp = Response(json.dumps(book), status=201, mimetype='application/json')
        resp.headers['Location'] = f'/{result.inserted_id}'
        resp.autocorrect_location_header = False
        return resp

    except Exception as e:
        print(e)
        return jsonify(error=str(e)), 500


@app.route('/<object_id>', methods=['PUT'])
def update_one_book_full(object_id):
    try:
        book = request.get_json()

        result = data.update_book_full(object_id, book)

        if result is None:
            return jsonify(error="The id specified is not a valid id"), 400

        if result.upserted_id is not None:
            book['_id'] = str(result.upserted_id)
            resp = Response(json.dumps(book), status=201, mimetype='application/json')
            resp.headers['Location'] = f'/{object_id}'
            resp.autocorrect_location_header = False
            return resp

        book['_id'] = object_id
        resp = Response(json.dumps(book), status=200, mimetype='application/json')
        resp.headers['Location'] = f'/{object_id}'
        resp.autocorrect_location_header = False
        return resp

    except Exception as e:
        print(e)
        return jsonify(error=str(e)), 500


@app.route('/<object_id>', methods=['PATCH'])
def update_one_book_partial(object_id):
    try:
        result = data.update_book_partial(object_id, request.get_json())

        if result is None:
            return jsonify(error="The id specified is not a valid id"), 400

        if result.matched_count == 0:
            return jsonify(error=f"No book with an id of {object_id} found to update"), 404

        resp = Response(status=200, mimetype='application/json')
        resp.headers['Location'] = f'/{object_id}'
        resp.autocorrect_location_header = False
        return resp

    except Exception as e:
        print(e)
        return jsonify(error=str(e)), 500


@app.route('/<object_id>', methods=['DELETE'])
def delete_one_book(object_id):
    try:
        result = data.delete_book(object_id)

        if result is None:
            return jsonify(error="The id specified is not a valid id"), 400

        if result.deleted_count == 0:
            return jsonify(error=f"No book with an id of {object_id} found to delete"), 404

        return jsonify(message="Object with id: " + object_id + " deleted successfully"), 200

    except Exception as e:
        print(e)
        return jsonify(error=str(e)), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
