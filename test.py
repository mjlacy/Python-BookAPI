from flask import json, url_for
from app import app
import copy
import data
import pytest
from bson import ObjectId
from pymongo.results import InsertOneResult, UpdateResult, DeleteResult

mimetype = 'application/json'
headers = {
    'Content-Type': mimetype,
    'Accept': mimetype
}

mock_collection = [
    {
        "_id": "5a80868574fdd6de0f4fa430",
        "author": "Leo Tolstoy",
        "bookId": 1,
        "title": "War and Peace",
        "year": 1869
    },
    {
        "_id": "5a80868574fdd6de0f4fa431",
        "author": "William Golding",
        "bookId": 2,
        "title": "Lord of the Flies",
        "year": 1954
    },
    {
        "_id": "5a80868574fdd6de0f4fa432",
        "author": "Dr.Seuss",
        "bookId": 3,
        "title": "Green Eggs and Ham",
        "year": 1960
    },
    {
        "_id": "5a80868574fdd6de0f4fa433",
        "author": "Dr.Seuss",
        "bookId": 4,
        "title": "The Cat In The Hat",
        "year": 1957
    },
]


@pytest.fixture
def client():
    return app.test_client()


def test_health_mapping():
    with app.test_request_context():
        assert url_for('health') == '/health'


def test_health(client):
    res = client.get('/health')

    assert res.data == b'ok'
    assert res.status_code == 200


def test_get_all_books_mapping():
    with app.test_request_context():
        assert url_for('get_all_books') == '/'


def test_get__all_books_exception(client, monkeypatch):
    def mock_return(params):
        raise Exception('Test Exception')

    monkeypatch.setattr(data, 'get_books', mock_return)
    res = client.get('/')

    assert res.data == b'{"error":"Test Exception"}\n'
    assert res.status_code == 500


def test_get_all_books_success(client, monkeypatch):
    def mock_return(params):
        return mock_collection

    monkeypatch.setattr(data, 'get_books', mock_return)
    res = client.get('/')
    expected_response = '{"books": ' + json.dumps(mock_collection) + '}'

    assert res.data.decode('utf-8') == expected_response
    assert res.status_code == 200


def test_get_book_author_query_success(client, monkeypatch):
    def mock_return(params):
        return list(filter(lambda book: book['author'] == params['author'], mock_collection))

    monkeypatch.setattr(data, 'get_books', mock_return)
    res = client.get('/?author=Dr.Seuss')
    expected_response = '{"books": ' + json.dumps([mock_collection[2], mock_collection[3]]) + '}'

    assert res.data.decode('utf-8') == expected_response
    assert res.status_code == 200


def test_get_book_author_and_year_query_success(client, monkeypatch):
    def mock_return(params):
        return list(filter(lambda book: book['author'] == params['author']
                                    and book['year'] == params['year'], mock_collection))

    monkeypatch.setattr(data, 'get_books', mock_return)
    res = client.get('/?author=Dr.Seuss&year=1960')
    expected_response = '{"books": ' + json.dumps([mock_collection[2]]) + '}'

    assert res.data.decode('utf-8') == expected_response
    assert res.status_code == 200


def test_get_one_book_mapping():
    with app.test_request_context():
        assert url_for('get_one_book', object_id="5a80868574fdd6de0f4fa430") == '/5a80868574fdd6de0f4fa430'


def test_get_one_book_id_not_found(client, monkeypatch):
    def mock_return(obj_id):
        return None

    monkeypatch.setattr(data, 'get_book', mock_return)
    res = client.get('/5a80868574fdd6de0f4fa433')

    assert res.data == b'{"error":"No book with an id of 5a80868574fdd6de0f4fa433 found"}\n'
    assert res.status_code == 404


def test_get_one_book_invalid_id(client):
    res = client.get('/5a80868574fdd')

    assert res.data == b'{"error":"No book with an id of 5a80868574fdd found"}\n'
    assert res.status_code == 404


def test_get_one_book_exception(client, monkeypatch):
    def mock_return(obj_id):
        raise Exception('Test Exception')

    monkeypatch.setattr(data, 'get_book', mock_return)
    res = client.get('/5a80868574fdd6de0f4fa430')

    assert res.data == b'{"error":"Test Exception"}\n'
    assert res.status_code == 500


def test_get_book_success(client, monkeypatch):
    def mock_return(obj_id):
        return mock_collection[0]

    monkeypatch.setattr(data, 'get_book', mock_return)
    res = client.get('/5a80868574fdd6de0f4fa430')

    assert res.data.decode('utf-8') == json.dumps(mock_collection[0])
    assert res.status_code == 200
    assert 'Location: /5a80868574fdd6de0f4fa430' in str(res.headers)


def test_create_book_mapping():
    with app.test_request_context():
        assert url_for('create_one_book') == '/'


def test_create_book_invalid_id(client):
    req_body = copy.copy(mock_collection[0])
    req_body['_id'] = "5a80868574fdd"
    res = client.post('/', data=json.dumps(req_body), headers=headers)

    assert res.data == b'{"error":"The id specified is not a valid id"}\n'
    assert res.status_code == 400


def test_create_book_exception(client, monkeypatch):
    def mock_return(body):
        raise Exception('Test Exception')

    monkeypatch.setattr(data, 'create_book', mock_return)
    res = client.post('/', data=json.dumps(mock_collection[0]), headers=headers)

    assert res.data == b'{"error":"Test Exception"}\n'
    assert res.status_code == 500


def test_create_book_no_id_success(client, monkeypatch):
    req_body = copy.copy(mock_collection[0])
    req_body.pop('_id')

    def mock_return(body):
        return InsertOneResult('5a80868574fdd6de0f4fa431', True)

    monkeypatch.setattr(data, 'create_book', mock_return)
    res = client.post('/', data=json.dumps(req_body), headers=headers)

    assert res.data.decode('utf-8') == json.dumps(req_body)
    assert res.status_code == 201
    assert 'Location: /5a80868574fdd6de0f4fa431' in str(res.headers)


def test_create_book_id_success(client, monkeypatch):
    def mock_return(body):
        return InsertOneResult('5a80868574fdd6de0f4fa432', True)

    monkeypatch.setattr(data, 'create_book', mock_return)
    res = client.post('/', data=json.dumps(mock_collection[0]), headers=headers)

    assert res.data.decode('utf-8') == json.dumps(mock_collection[0])
    assert res.status_code == 201
    assert 'Location: /5a80868574fdd6de0f4fa432' in str(res.headers)


def test_update_book_full_mapping():
    with app.test_request_context():
        assert url_for('update_one_book_full', object_id="5a80868574fdd6de0f4fa430") == '/5a80868574fdd6de0f4fa430'


def test_update_book_full_invalid_id(client):
    res = client.put('/5a80868574fdd', data=json.dumps(mock_collection[0]), headers=headers)

    assert res.data == b'{"error":"The id specified is not a valid id"}\n'
    assert res.status_code == 400


def test_update_book_full_exception(client, monkeypatch):
    def mock_return(obj_id, body):
        raise Exception('Test Exception')

    monkeypatch.setattr(data, 'update_book_full', mock_return)
    res = client.put('/5a80868574fdd6de0f4fa430', data=json.dumps(mock_collection[0]), headers=headers)

    assert res.data == b'{"error":"Test Exception"}\n'
    assert res.status_code == 500


def test_update_book_full_no_id_insert_success(client, monkeypatch):
    req_body = copy.copy(mock_collection[0])
    req_body.pop('_id')

    def mock_return(obj_id, body):
        return UpdateResult({'n': 1, 'nModified': 0, 'upserted': ObjectId('5a80868574fdd6de0f4fa430'),
                             'ok': 1.0, 'updatedExisting': False}, True)

    monkeypatch.setattr(data, 'update_book_full', mock_return)
    res = client.put('/5a80868574fdd6de0f4fa430', data=json.dumps(req_body), headers=headers)

    assert res.data.decode('utf-8') == json.dumps(mock_collection[0])
    assert res.status_code == 201
    assert 'Location: /5a80868574fdd6de0f4fa430' in str(res.headers)


def test_update_book_full_no_id_update_success(client, monkeypatch):
    req_body = copy.copy(mock_collection[0])
    req_body.pop('_id')

    def mock_return(obj_id, body):
        return UpdateResult({'n': 1, 'nModified': 1, 'ok': 1.0, 'updatedExisting': True}, True)

    monkeypatch.setattr(data, 'update_book_full', mock_return)
    res = client.put('/5a80868574fdd6de0f4fa430', data=json.dumps(req_body), headers=headers)

    assert res.data.decode('utf-8') == json.dumps(mock_collection[0])
    assert res.status_code == 200
    assert 'Location: /5a80868574fdd6de0f4fa430' in str(res.headers)


def test_update_book_full_id_insert_success(client, monkeypatch):
    def mock_return(obj_id, body):
        return UpdateResult({'n': 1, 'nModified': 0, 'upserted': ObjectId('5a80868574fdd6de0f4fa430'),
                             'ok': 1.0, 'updatedExisting': False}, True)

    monkeypatch.setattr(data, 'update_book_full', mock_return)
    res = client.put('/5a80868574fdd6de0f4fa430', data=json.dumps(mock_collection[0]), headers=headers)

    assert res.data.decode('utf-8') == json.dumps(mock_collection[0])
    assert res.status_code == 201
    assert 'Location: /5a80868574fdd6de0f4fa430' in str(res.headers)


def test_update_book_full_id_update_success(client, monkeypatch):
    def mock_return(obj_id, body):
        return UpdateResult({'n': 1, 'nModified': 1, 'ok': 1.0, 'updatedExisting': True}, True)

    monkeypatch.setattr(data, 'update_book_full', mock_return)
    res = client.put('/5a80868574fdd6de0f4fa430', data=json.dumps(mock_collection[0]), headers=headers)

    assert res.data.decode('utf-8') == json.dumps(mock_collection[0])
    assert res.status_code == 200
    assert 'Location: /5a80868574fdd6de0f4fa430' in str(res.headers)


def test_update_book_partial_mapping():
    with app.test_request_context():
        assert url_for('update_one_book_partial', object_id="5a80868574fdd6de0f4fa430") == '/5a80868574fdd6de0f4fa430'


def test_update_book_partial_invalid_id(client):
    res = client.patch('/5a80868574fdd', data=json.dumps(mock_collection[0]), headers=headers)

    assert res.data == b'{"error":"The id specified is not a valid id"}\n'
    assert res.status_code == 400


def test_update_book_partial_exception(client, monkeypatch):
    def mock_return(obj_id, body):
        raise Exception('Test Exception')

    monkeypatch.setattr(data, 'update_book_partial', mock_return)
    res = client.patch('/5a80868574fdd6de0f4fa430', data=json.dumps(mock_collection[0]), headers=headers)

    assert res.data == b'{"error":"Test Exception"}\n'
    assert res.status_code == 500


def test_update_book_partial_id_not_found(client, monkeypatch):
    def mock_return(obj_id, body):
        return UpdateResult({'n': 0, 'nModified': 0, 'ok': 1.0, 'updatedExisting': False}, True)

    monkeypatch.setattr(data, 'update_book_partial', mock_return)
    res = client.patch('/5a80868574fdd6de0f4fa433')

    assert res.data == b'{"error":"No book with an id of 5a80868574fdd6de0f4fa433 found to update"}\n'
    assert res.status_code == 404


def test_update_book_partial_success(client, monkeypatch):
    def mock_return(obj_id, body):
        return UpdateResult({'n': 1, 'nModified': 1, 'ok': 1.0, 'updatedExisting': True}, True)

    monkeypatch.setattr(data, 'update_book_partial', mock_return)
    res = client.patch('/5a80868574fdd6de0f4fa432', data=json.dumps(mock_collection[0]), headers=headers)

    assert res.status_code == 200
    assert 'Location: /5a80868574fdd6de0f4fa432' in str(res.headers)


def test_delete_book_mapping():
    with app.test_request_context():
        assert url_for('delete_one_book', object_id="5a80868574fdd6de0f4fa430") == '/5a80868574fdd6de0f4fa430'


def test_delete_book_id_not_found(client, monkeypatch):
    def mock_return(obj_id):
        return DeleteResult({'n': 0, 'ok': 1.0}, True)

    monkeypatch.setattr(data, 'delete_book', mock_return)
    res = client.delete('/5a80868574fdd6de0f4fa433')

    assert res.data == b'{"error":"No book with an id of 5a80868574fdd6de0f4fa433 found to delete"}\n'
    assert res.status_code == 404


def test_delete_book_invalid_id(client):
    res = client.delete('/5a80868574fdd')

    assert res.data == b'{"error":"The id specified is not a valid id"}\n'
    assert res.status_code == 400


def test_delete_book_exception(client, monkeypatch):
    def mock_return(obj_id):
        raise Exception('Test Exception')

    monkeypatch.setattr(data, 'delete_book', mock_return)
    res = client.delete('/5a80868574fdd6de0f4fa430')

    assert res.data == b'{"error":"Test Exception"}\n'
    assert res.status_code == 500


def test_delete_book_success(client, monkeypatch):
    def mock_return(obj_id):
        return DeleteResult({'n': 1, 'ok': 1.0}, True)

    monkeypatch.setattr(data, 'delete_book', mock_return)
    res = client.delete('/5a80868574fdd6de0f4fa430')

    assert res.data == b'{"message":"Object with id: 5a80868574fdd6de0f4fa430 deleted successfully"}\n'
    assert res.status_code == 200
