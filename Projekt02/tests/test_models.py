import pytest
from sqlalchemy.exc import IntegrityError

from app.models import Book, Review, User, UserBookStatus, load_user


class TestUserModel:
    def test_create_user(self, db):
        u = User(username='t', email='t@e.pl', password_hash='h')
        db.session.add(u)
        db.session.commit()
        assert u.id is not None

    def test_is_admin_defaults_false(self, db):
        u = User(username='x', email='x@e.pl', password_hash='h')
        db.session.add(u)
        db.session.commit()
        assert u.is_admin is False

    def test_username_must_be_unique(self, db):
        db.session.add(User(username='dup', email='a@e.pl', password_hash='h'))
        db.session.commit()
        db.session.add(User(username='dup', email='b@e.pl', password_hash='h'))
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()

    def test_email_must_be_unique(self, db):
        db.session.add(User(username='a', email='same@e.pl', password_hash='h'))
        db.session.commit()
        db.session.add(User(username='b', email='same@e.pl', password_hash='h'))
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()

    def test_load_user_returns_correct_user(self, app, user):
        with app.app_context():
            loaded = load_user(user.id)
            assert loaded is not None
            assert loaded.username == 'kopciuszek'

    def test_load_user_returns_none_for_missing_id(self, app):
        with app.app_context():
            assert load_user(99999) is None


class TestBookModel:
    def test_create_book(self, db):
        b = Book(title='Title', author='Author')
        db.session.add(b)
        db.session.commit()
        assert b.id is not None

    def test_google_id_can_be_null(self, db):
        b = Book(title='Title', author='Author', google_id=None)
        db.session.add(b)
        db.session.commit()
        assert b.google_id is None

    def test_optional_fields_persist(self, db):
        b = Book(
            title='Title', author='Author',
            genre='Fantasy', year='1937',
            description='desc', cover_url='url',
            publisher='pub', page_count='310',
        )
        db.session.add(b)
        db.session.commit()
        fresh = Book.query.get(b.id)
        assert fresh.genre == 'Fantasy'
        assert fresh.page_count == '310'


class TestReviewModel:
    def test_review_backref_to_author_and_book(self, db, user):
        b = Book(title='T', author='A')
        db.session.add(b)
        db.session.commit()
        r = Review(rating=5, content='great', user_id=user.id, book_id=b.id)
        db.session.add(r)
        db.session.commit()
        assert r.author.username == 'kopciuszek'
        assert r.book.title == 'T'

    def test_user_reviews_dynamic_relation(self, db, user):
        b = Book(title='T', author='A')
        db.session.add(b)
        db.session.commit()
        db.session.add(Review(rating=3, content='meh', user_id=user.id, book_id=b.id))
        db.session.commit()
        assert user.reviews.count() == 1

    def test_book_reviews_dynamic_relation(self, db, user):
        b = Book(title='T', author='A')
        db.session.add(b)
        db.session.commit()
        db.session.add(Review(rating=4, content='nice', user_id=user.id, book_id=b.id))
        db.session.commit()
        assert b.reviews.count() == 1

    def test_timestamp_is_set(self, db, user):
        b = Book(title='T', author='A')
        db.session.add(b)
        db.session.commit()
        r = Review(rating=5, content='ok', user_id=user.id, book_id=b.id)
        db.session.add(r)
        db.session.commit()
        assert r.timestamp is not None


class TestUserBookStatusModel:
    def test_create_status(self, db, user):
        b = Book(title='T', author='A')
        db.session.add(b)
        db.session.commit()
        s = UserBookStatus(user_id=user.id, book_id=b.id, status='Reading')
        db.session.add(s)
        db.session.commit()
        assert s.id is not None
        assert s.user.username == 'kopciuszek'
        assert s.book.title == 'T'

    @pytest.mark.parametrize('value', ['To Read', 'Reading', 'Read'])
    def test_accepts_expected_status_values(self, db, user, value):
        b = Book(title=f'T-{value}', author='A')
        db.session.add(b)
        db.session.commit()
        s = UserBookStatus(user_id=user.id, book_id=b.id, status=value)
        db.session.add(s)
        db.session.commit()
        assert s.status == value
