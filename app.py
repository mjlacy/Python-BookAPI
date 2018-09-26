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

        if book is 'Invalid':
            return jsonify(error="The id you specified is not a valid id"), 400

        return Response(json.dumps(book), status=200, mimetype='application/json')

    except Exception as e:
        print(e)
        return jsonify(error=str(e)), 500


@app.route('/', methods=['POST'])
def create_one_book():
    try:
        result = data.create_book(request.get_json())

        if result is None:
            return jsonify(error="The id you specified is not a valid id"), 400

        return jsonify(link='/' + str(result.inserted_id)), 201

    except Exception as e:
        print(e)
        return jsonify(error=str(e)), 500


@app.route('/<object_id>', methods=['PUT'])
def update_one_book(object_id):
    try:
        result = data.update_book(object_id, request.get_json())

        if result is None:
            return jsonify(error="The id you specified is not a valid id"), 400

        if result.upserted_id is not None:
            return jsonify(link='/' + str(result.upserted_id)), 201

        return jsonify(link='/' + object_id)

    except Exception as e:
        print(e)
        return jsonify(error=str(e)), 500


@app.route('/<object_id>', methods=['DELETE'])
def delete_one_book(object_id):
    try:
        if data.get_book(object_id) is None:
            return jsonify(error="No book with an id of " + object_id + " found to delete"), 404

        result = data.delete_book(object_id)

        if result is None:
            return jsonify(error="The id you specified is not a valid id"), 400

        return jsonify(message="Object with id: " + object_id + " deleted successfully"), 200

    except Exception as e:
        print(e)
        return jsonify(error=str(e)), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
