# Book API

Queries the book collection in a mongo database

## Routes
- GET /

- GET /{id}

- GET /health

- POST /

- PUT /{id}

- DELETE /{id}

### Example Calls

- GET localhost:5000/

- GET localhost:5000/5a80868574fdd6de0f4fa438

- POST localhost:5000/
    - Body (3 Fields):
    ```
    {
        "Name" : "War and Peace",
        "Author" : "Leo Tolstoy",
        "Year" : 1869
    }
    ```

- PUT localhost:5000/5a80868574fdd6de0f4fa439
    - Body (3 Fields):
    ```
    {
        "Name" : "War and Peace",
        "Author" : "Leo Tolstoy",
        "Year" : 1870
    }
    ```

- DELETE localhost:5000/5aa5841a740db1970dff3248

- GET localhost:5000/health

##### Example Response for `GET /5a8ddeef55235ccd5c0e5699` (4 Fields)

```
{
    "_id": "5a8ddeef55235ccd5c0e5699",
    "Name": "War and Peace",
    "Author": "Leo Tolstoy",
    "Year": 1869
}
```