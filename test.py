from flask import json, url_for
from app import app
import data
import pytest
from bson import ObjectId
from pymongo.errors import DuplicateKeyError
from pymongo.results import InsertOneResult, UpdateResult, DeleteResult

mimetype = 'application/json'
headers = {
    'Content-Type': mimetype,
    'Accept': mimetype
}

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
    def mock_return():
        raise Exception('Test Exception')

    monkeypatch.setattr(data, 'get_books', mock_return)
    res = client.get('/')
    assert res.data == b'{"message":"An error occurred while processing your request"}\n'
    assert res.status_code == 500


def test_get_all_books_success(client, monkeypatch):
    mock_collection = [
        {
            "_id": "5a80868574fdd6de0f4fa430",
            "author": "Leo Tolstoy",
            "bookId": 1,
            "name": "War and Peace",
            "year": 1869
        },
        {
            "_id": "5a80868574fdd6de0f4fa431",
            "author": "William Golding",
            "bookId": 2,
            "name": "Lord of the Flies",
            "year": 1954
        }
    ]

    def mock_return():
        return mock_collection

    monkeypatch.setattr(data, 'get_books', mock_return)
    res = client.get('/')
    expected_response = '{"books": ' + json.dumps(mock_collection) + '}'

    assert res.data.decode('utf-8') == expected_response
    assert res.status_code == 200


def test_get_one_book_mapping():
    with app.test_request_context():
        assert url_for('get_one_book', object_id="5a80868574fdd6de0f4fa430") == '/5a80868574fdd6de0f4fa430'


def test_get_one_book_invalidId(client):
    res = client.get('/5a80868574fdd')
    assert res.data == b'{"message":"The _id you specified is not a valid ObjectId, ' \
            b'it must be a 12-byte input or 24-character hex string"}\n'
    assert res.status_code == 400


def test_get_one_book_exception(client, monkeypatch):
    def mock_return():
        raise Exception('Test Exception')

    monkeypatch.setattr(data, 'get_book', mock_return)
    res = client.get('/5a80868574fdd6de0f4fa430')
    assert res.data == b'{"message":"An error occurred while processing your request"}\n'
    assert res.status_code == 500


def test_get_book_success(client, monkeypatch):
    mock_book = {
            "_id": "5a80868574fdd6de0f4fa430",
            "author": "Leo Tolstoy",
            "bookId": 1,
            "name": "War and Peace",
            "year": 1869
        }

    def mock_return(object_id):
        return mock_book

    monkeypatch.setattr(data, 'get_book', mock_return)
    res = client.get('/5a80868574fdd6de0f4fa430')

    assert res.data.decode('utf-8') == json.dumps(mock_book)
    assert res.status_code == 200


def test_create_book_mapping():
    with app.test_request_context():
        assert url_for('create_book') == '/'


def test_create_book_invalidId(client):
    req_body = {
        "_id": "5a80868574fdd",
        "author": "Leo Tolstoy",
        "bookId": 1,
        "name": "War and Peace",
        "year": 1869
    }

    res = client.post('/', data=json.dumps(req_body), headers=headers)
    assert res.data == b'{"message":"The _id you specified is not a valid ObjectId, ' \
             b'it must be a 12-byte input or 24-character hex string"}\n'
    assert res.status_code == 400


def test_create_book_duplicateKeyError(client, monkeypatch):
    req_body = {
        "_id": "5a80868574fdd6de0f4fa430",
        "author": "Leo Tolstoy",
        "bookId": 1,
        "name": "War and Peace",
        "year": 1869
    }

    def mock_return(body):
        raise DuplicateKeyError('Key already exists')

    monkeypatch.setattr(data, 'post_book', mock_return)
    res = client.post('/', data=json.dumps(req_body), headers=headers)

    assert res.data == b'{"message":"The _id you specified already exists, please choose a different one"}\n'
    assert res.status_code == 409


def test_create_book_exception(client, monkeypatch):
    req_body = {
        "_id": "5a80868574fdd6de0f4fa430",
        "author": "Leo Tolstoy",
        "bookId": 1,
        "name": "War and Peace",
        "year": 1869
    }

    def mock_return(body):
        raise Exception('Test Exception')

    monkeypatch.setattr(data, 'post_book', mock_return)
    res = client.post('/', data=json.dumps(req_body), headers=headers)
    assert res.data == b'{"message":"An error occurred while processing your request"}\n'
    assert res.status_code == 500


def test_create_book_noId_success(client, monkeypatch):
    req_body = {
        "author": "Leo Tolstoy",
        "bookId": 1,
        "name": "War and Peace",
        "year": 1869
    }

    def mock_return(body):
        return InsertOneResult('5a80868574fdd6de0f4fa431', True)

    monkeypatch.setattr(data, 'post_book', mock_return)
    res = client.post('/', data=json.dumps(req_body), headers=headers)
    assert res.data == b'{"link":"/5a80868574fdd6de0f4fa431"}\n'
    assert res.status_code == 201


def test_create_book_id_success(client, monkeypatch):
    req_body = {
        "_id": "5a80868574fdd6de0f4fa431",
        "author": "Leo Tolstoy",
        "bookId": 1,
        "name": "War and Peace",
        "year": 1869
    }

    def mock_return(body):
        return InsertOneResult('5a80868574fdd6de0f4fa432', True)

    monkeypatch.setattr(data, 'post_book', mock_return)
    res = client.post('/', data=json.dumps(req_body), headers=headers)
    assert res.data == b'{"link":"/5a80868574fdd6de0f4fa432"}\n'
    assert res.status_code == 201


def test_update_book_mapping():
    with app.test_request_context():
        assert url_for('update_book', object_id="5a80868574fdd6de0f4fa430") == '/5a80868574fdd6de0f4fa430'


def test_update_book_invalidId(client):
    req_body = {
        "author": "Leo Tolstoy",
        "bookId": 1,
        "name": "War and Peace",
        "year": 1869
    }

    res = client.put('/5a80868574fdd', data=json.dumps(req_body), headers=headers)
    assert res.data == b'{"message":"The _id you specified is not a valid ObjectId, ' \
            b'it must be a 12-byte input or 24-character hex string"}\n'
    assert res.status_code == 400


def test_update_book_exception(client, monkeypatch):
    req_body = {
        "author": "Leo Tolstoy",
        "bookId": 1,
        "name": "War and Peace",
        "year": 1869
    }

    def mock_return(body):
        raise Exception('Test Exception')

    monkeypatch.setattr(data, 'put_book', mock_return)
    res = client.put('/5a80868574fdd6de0f4fa430', data=json.dumps(req_body), headers=headers)
    assert res.data == b'{"message":"An error occurred while processing your request"}\n'
    assert res.status_code == 500


def test_update_book_noId_insert_success(client, monkeypatch):
    req_body = {
        "author": "Leo Tolstoy",
        "bookId": 1,
        "name": "War and Peace",
        "year": 1869
    }

    def mock_return(obj_id, body):
        return UpdateResult({'n': 1, 'nModified': 0, 'upserted': ObjectId('5a80868574fdd6de0f4fa432'),
                             'ok': 1.0, 'updatedExisting': False}, True)

    monkeypatch.setattr(data, 'put_book', mock_return)
    res = client.put('/5a80868574fdd6de0f4fa432', data=json.dumps(req_body), headers=headers)
    assert res.data == b'{"link":"/5a80868574fdd6de0f4fa432"}\n'
    assert res.status_code == 201

def test_update_book_noId_update_success(client, monkeypatch):
    req_body = {
        "author": "Leo Tolstoy",
        "bookId": 1,
        "name": "War and Peace",
        "year": 1869
    }

    def mock_return(obj_id, body):
        return UpdateResult({'n': 1, 'nModified': 1, 'ok': 1.0, 'updatedExisting': True}, True)

    monkeypatch.setattr(data, 'put_book', mock_return)
    res = client.put('/5a80868574fdd6de0f4fa432', data=json.dumps(req_body), headers=headers)
    assert res.data == b'{"link":"/5a80868574fdd6de0f4fa432"}\n'
    assert res.status_code == 200


def test_update_book_id_insert_success(client, monkeypatch):
    req_body = {
        "_id": "5a80868574fdd6de0f4fa432",
        "author": "Leo Tolstoy",
        "bookId": 1,
        "name": "War and Peace",
        "year": 1869
    }

    def mock_return(obj_id, body):
        return UpdateResult({'n': 1, 'nModified': 0, 'upserted': ObjectId('5a80868574fdd6de0f4fa432'),
                             'ok': 1.0, 'updatedExisting': False}, True)

    monkeypatch.setattr(data, 'put_book', mock_return)
    res = client.put('/5a80868574fdd6de0f4fa432', data=json.dumps(req_body), headers=headers)
    assert res.data == b'{"link":"/5a80868574fdd6de0f4fa432"}\n'
    assert res.status_code == 201

def test_update_book_id_update_success(client, monkeypatch):
    req_body = {
        "_id": "5a80868574fdd6de0f4fa432",
        "author": "Leo Tolstoy",
        "bookId": 1,
        "name": "War and Peace",
        "year": 1869
    }

    def mock_return(obj_id, body):
        return UpdateResult({'n': 1, 'nModified': 1, 'ok': 1.0, 'updatedExisting': True}, True)

    monkeypatch.setattr(data, 'put_book', mock_return)
    res = client.put('/5a80868574fdd6de0f4fa432', data=json.dumps(req_body), headers=headers)
    assert res.data == b'{"link":"/5a80868574fdd6de0f4fa432"}\n'
    assert res.status_code == 200


def test_delete_book_mapping():
    with app.test_request_context():
        assert url_for('delete_one_book', object_id="5a80868574fdd6de0f4fa430") == '/5a80868574fdd6de0f4fa430'


def test_delete_book_idNotFound(client, monkeypatch):
    def mock_return(obj_id):
        return []

    monkeypatch.setattr(data, 'get_book', mock_return)
    res = client.delete('/5a80868574fdd6de0f4fa433')
    assert res.data == b'{"message":"No object with an id of 5a80868574fdd6de0f4fa433 found to delete"}\n'
    assert res.status_code == 404


def test_delete_book_invalidId(client):
    res = client.delete('/5a80868574fdd')
    assert res.data == b'{"message":"The _id you specified is not a valid ObjectId, ' \
                        b'it must be a 12-byte input or 24-character hex string"}\n'
    assert res.status_code == 400


def test_delete_book_exception(client, monkeypatch):
    def mock_return():
        raise Exception('Test Exception')

    monkeypatch.setattr(data, 'delete_book', mock_return)
    res = client.delete('/5a80868574fdd6de0f4fa430')
    assert res.data == b'{"message":"An error occurred while processing your request"}\n'
    assert res.status_code == 500


def test_delete_book_success(client, monkeypatch):
    def mock_return(obj_id):
        return DeleteResult({'n': 1, 'ok': 1.0}, True)

    monkeypatch.setattr(data, 'delete_book', mock_return)
    res = client.delete('/5a80868574fdd6de0f4fa430')
    assert res.data == b'{"message":"Object with id: 5a80868574fdd6de0f4fa430 deleted successfully"}\n'
    assert res.status_code == 200