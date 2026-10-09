"""Tests for the books CRUD API. Each test follows Arrange / Act / Assert."""


class TestCreateBook:
    """POST /books"""

    def test_create_book_success(self, client):
        payload = {"title": "Python Basics", "author": "John Doe", "price": 29.99}
        response = client.post("/books", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Python Basics"
        assert data["author"] == "John Doe"
        assert data["price"] == 29.99
        assert "id" in data
        assert "created_at" in data

    def test_create_book_missing_title(self, client):
        response = client.post("/books", json={"author": "John Doe", "price": 29.99})
        assert response.status_code == 422

    def test_create_book_negative_price(self, client):
        payload = {"title": "Free Book", "author": "Author", "price": -5.00}
        response = client.post("/books", json=payload)
        assert response.status_code == 422

    def test_create_book_empty_title(self, client):
        payload = {"title": "", "author": "Author", "price": 10.00}
        response = client.post("/books", json=payload)
        assert response.status_code == 422

    def test_duplicate_title_returns_409(self, client, sample_book):
        response = client.post("/books", json={
            "title": "Test Book", "author": "Someone Else", "price": 5.00
        })
        assert response.status_code == 409


class TestReadBooks:
    """GET /books and GET /books/{id}"""

    def test_list_books_empty(self, client):
        response = client.get("/books")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_books_with_data(self, client, sample_book):
        response = client.get("/books")
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_get_book_by_id(self, client, sample_book):
        response = client.get(f"/books/{sample_book['id']}")
        assert response.status_code == 200
        assert response.json()["title"] == "Test Book"

    def test_get_book_not_found(self, client):
        response = client.get("/books/9999")
        assert response.status_code == 404


class TestUpdateBook:
    """PATCH /books/{id}"""

    def test_patch_book_title(self, client, sample_book):
        response = client.patch(f"/books/{sample_book['id']}", json={"title": "Updated Title"})
        assert response.status_code == 200
        assert response.json()["title"] == "Updated Title"
        assert response.json()["author"] == "Test Author"

    def test_patch_nonexistent_book(self, client):
        response = client.patch("/books/9999", json={"title": "Nope"})
        assert response.status_code == 404


class TestDeleteBook:
    """DELETE /books/{id}"""

    def test_delete_book(self, client, sample_book):
        response = client.delete(f"/books/{sample_book['id']}")
        assert response.status_code == 204
        follow_up = client.get(f"/books/{sample_book['id']}")
        assert follow_up.status_code == 404

    def test_delete_nonexistent_book(self, client):
        response = client.delete("/books/9999")
        assert response.status_code == 404
