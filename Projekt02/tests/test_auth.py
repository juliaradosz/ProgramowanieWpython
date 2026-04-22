from app.models import Book, Review, User, UserBookStatus


class TestLogin:
    def test_get_login_returns_200(self, client):
        response = client.get('/auth/login')
        assert response.status_code == 200

    def test_valid_credentials_redirect_to_index(self, client, user):
        response = client.post('/auth/login', data={
            'username': 'kopciuszek',
            'password': 'pantofelek',
        })
        assert response.status_code == 302

    def test_wrong_password_no_login(self, client, user):
        response = client.post('/auth/login', data={
            'username': 'kopciuszek',
            'password': 'zle-haslo',
        })
        assert response.status_code == 200

    def test_nonexistent_user_no_login(self, client):
        response = client.post('/auth/login', data={
            'username': 'smok-wawelski',
            'password': 'cokolwiek',
        })
        assert response.status_code == 200

    def test_authenticated_user_redirected_away_from_login(self, logged_in_client):
        response = logged_in_client.get('/auth/login')
        assert response.status_code == 302


class TestLogout:
    def test_logout_redirects_to_index(self, logged_in_client):
        response = logged_in_client.get('/auth/logout')
        assert response.status_code == 302
        assert response.headers['Location'].endswith('/')


class TestRegister:
    def test_get_register_returns_200(self, client):
        response = client.get('/auth/register')
        assert response.status_code == 200

    def test_valid_registration_creates_user(self, client, db):
        response = client.post('/auth/register', data={
            'username': 'roszpunka',
            'email': 'roszpunka@lib.pl',
            'password': 'dlugiewlosy',
            'password2': 'dlugiewlosy',
        })
        assert response.status_code == 302
        u = User.query.filter_by(username='roszpunka').first()
        assert u is not None
        assert u.email == 'roszpunka@lib.pl'
        assert u.is_admin is False
        assert u.password_hash != 'dlugiewlosy'

    def test_password_mismatch_rejected(self, client, db):
        client.post('/auth/register', data={
            'username': 'zly',
            'email': 'zly@lib.pl',
            'password': 'jedno1',
            'password2': 'drugie2',
        })
        assert User.query.filter_by(username='zly').first() is None

    def test_short_password_rejected(self, client, db):
        client.post('/auth/register', data={
            'username': 'krotki',
            'email': 'k@lib.pl',
            'password': '123',
            'password2': '123',
        })
        assert User.query.filter_by(username='krotki').first() is None

    def test_duplicate_username_rejected(self, client, db, user):
        client.post('/auth/register', data={
            'username': 'kopciuszek',
            'email': 'inny@lib.pl',
            'password': 'dlugiewlosy',
            'password2': 'dlugiewlosy',
        })
        assert User.query.filter_by(username='kopciuszek').count() == 1

    def test_duplicate_email_rejected(self, client, db, user):
        client.post('/auth/register', data={
            'username': 'inny-user',
            'email': 'k@lib.pl',
            'password': 'dlugiewlosy',
            'password2': 'dlugiewlosy',
        })
        assert User.query.filter_by(username='inny-user').first() is None

    def test_missing_fields_rejected(self, client, db):
        client.post('/auth/register', data={
            'username': '', 'email': '', 'password': '', 'password2': '',
        })
        assert User.query.count() == 0

    def test_authenticated_user_redirected_from_register(self, logged_in_client):
        response = logged_in_client.get('/auth/register')
        assert response.status_code == 302


class TestAdminPanel:
    def test_anonymous_redirected_to_login(self, client):
        response = client.get('/auth/admin')
        assert response.status_code == 302
        assert '/auth/login' in response.headers['Location']

    def test_regular_user_redirected_out(self, logged_in_client):
        response = logged_in_client.get('/auth/admin')
        assert response.status_code == 302

    def test_admin_sees_panel(self, logged_in_admin_client):
        response = logged_in_admin_client.get('/auth/admin')
        assert response.status_code == 200


class TestAdminDelete:
    def test_admin_can_delete_review(self, logged_in_admin_client, db, user):
        book = Book(title='T', author='A')
        db.session.add(book)
        db.session.commit()
        review = Review(rating=5, content='cudne', user_id=user.id, book_id=book.id)
        db.session.add(review)
        db.session.commit()
        review_id = review.id

        response = logged_in_admin_client.get(f'/auth/delete_review/{review_id}')
        assert response.status_code == 302
        assert Review.query.get(review_id) is None

    def test_admin_delete_user_cascades_to_related_data(self, logged_in_admin_client, db, user):
        book = Book(title='T', author='A')
        db.session.add(book)
        db.session.commit()
        user_id = user.id
        review = Review(rating=5, content='ok', user_id=user_id, book_id=book.id)
        status = UserBookStatus(user_id=user_id, book_id=book.id, status='Reading')
        db.session.add_all([review, status])
        db.session.commit()

        logged_in_admin_client.get(f'/auth/delete_user/{user_id}')

        assert User.query.get(user_id) is None
        assert Review.query.filter_by(user_id=user_id).count() == 0
        assert UserBookStatus.query.filter_by(user_id=user_id).count() == 0

    def test_regular_user_cannot_delete_review(self, logged_in_client, db, admin):
        book = Book(title='T', author='A')
        db.session.add(book)
        db.session.commit()
        review = Review(rating=5, content='test', user_id=admin.id, book_id=book.id)
        db.session.add(review)
        db.session.commit()
        review_id = review.id

        logged_in_client.get(f'/auth/delete_review/{review_id}')
        assert Review.query.get(review_id) is not None
