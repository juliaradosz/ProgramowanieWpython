import pytest

from app.models import Book, Review, UserBookStatus


FAKE_BOOK = {
    "google_id": "OL12345W",
    "title": "The Hobbit",
    "author": "J.R.R. Tolkien",
    "description": "In a hole in the ground there lived a hobbit...",
    "cover_url": "https://example.com/cover.jpg",
    "year": "1937",
    "genre": "Fantasy",
    "publisher": "Houghton Mifflin",
    "page_count": 310,
    "author_photo": "https://example.com/author.jpg",
}


@pytest.fixture(autouse=True)
def mock_open_library(monkeypatch):
    monkeypatch.setattr(
        'app.books.routes.fetch_books_by_query',
        lambda q, max_results=12: [FAKE_BOOK],
    )
    monkeypatch.setattr(
        'app.books.routes.fetch_books_by_subject',
        lambda subj, max_results=16: [FAKE_BOOK],
    )


class TestIndex:
    def test_index_returns_200(self, client):
        response = client.get('/')
        assert response.status_code == 200

    def test_index_with_search_query(self, client):
        response = client.get('/?query=tolkien')
        assert response.status_code == 200

    def test_index_with_known_category(self, client):
        response = client.get('/?category=Fantasy')
        assert response.status_code == 200

    def test_index_with_unknown_category_falls_back(self, client):
        response = client.get('/?category=Nieistniejacy')
        assert response.status_code == 200


class TestBookDetails:
    def test_details_view_handles_api_failure(self, client, monkeypatch):
        import requests as _r

        def raise_on_get(*_a, **_kw):
            raise _r.exceptions.ConnectionError('no network')

        monkeypatch.setattr('app.books.routes.requests.get', raise_on_get)
        response = client.get('/book/NOPE123')
        assert response.status_code == 200


class TestUpdateStatus:
    def test_anonymous_cannot_update_status(self, client):
        response = client.post('/update_status', data={
            'title': 'T', 'author': 'A', 'status': 'Reading',
        })
        assert response.status_code == 302
        assert '/auth/login' in response.headers['Location']

    def test_update_status_creates_new_book_and_status(self, logged_in_client, db, user):
        logged_in_client.post('/update_status', data={
            'title': 'The Hobbit',
            'author': 'Tolkien',
            'status': 'To Read',
            'google_id': 'OL1W',
            'genre': 'Fantasy',
            'year': '1937',
            'description': 'a hobbit tale',
            'cover_url': 'https://example.com/c.jpg',
            'publisher': 'Houghton Mifflin',
            'page_count': '310',
        })

        book = Book.query.filter_by(title='The Hobbit').first()
        assert book is not None
        assert book.author == 'Tolkien'

        status = UserBookStatus.query.filter_by(user_id=user.id, book_id=book.id).first()
        assert status is not None
        assert status.status == 'To Read'

    def test_update_status_updates_existing_status(self, logged_in_client, db, user):
        book = Book(title='T', author='A')
        db.session.add(book)
        db.session.commit()
        s = UserBookStatus(user_id=user.id, book_id=book.id, status='To Read')
        db.session.add(s)
        db.session.commit()

        logged_in_client.post('/update_status', data={
            'title': 'T', 'author': 'A', 'status': 'Read',
        })

        refreshed = UserBookStatus.query.filter_by(user_id=user.id, book_id=book.id).first()
        assert refreshed.status == 'Read'
        assert UserBookStatus.query.count() == 1


class TestProfile:
    def test_anonymous_redirected_to_login(self, client):
        response = client.get('/profile')
        assert response.status_code == 302
        assert '/auth/login' in response.headers['Location']

    def test_logged_in_user_sees_profile(self, logged_in_client):
        response = logged_in_client.get('/profile')
        assert response.status_code == 200


class TestAddReview:
    def test_anonymous_cannot_review(self, client):
        response = client.post('/add_review', data={})
        assert response.status_code == 302

    def test_add_review_requires_book_in_db(self, logged_in_client, db):
        logged_in_client.post(
            '/add_review',
            data={'title': 'Nie ma', 'author': 'Nikt', 'rating': '5', 'content': 'ok'},
            headers={'Referer': 'http://localhost/'},
        )
        assert Review.query.count() == 0

    def test_add_review_creates_review(self, logged_in_client, db, user):
        book = Book(title='T', author='A')
        db.session.add(book)
        db.session.commit()

        logged_in_client.post(
            '/add_review',
            data={'title': 'T', 'author': 'A', 'rating': '4', 'content': 'good'},
            headers={'Referer': 'http://localhost/'},
        )

        review = Review.query.first()
        assert review is not None
        assert review.rating == 4
        assert review.content == 'good'
        assert review.user_id == user.id
        assert review.book_id == book.id
