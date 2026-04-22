import os
import sys

import pytest
from werkzeug.security import generate_password_hash

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app import create_app, db as _db
from app.models import User
from config import Config


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SECRET_KEY = 'test-secret-key'
    WTF_CSRF_ENABLED = False
    PROPAGATE_EXCEPTIONS = False


@pytest.fixture
def app():
    flask_app = create_app(TestingConfig)
    with flask_app.app_context():
        _db.create_all()
        yield flask_app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def db(app):
    return _db


@pytest.fixture
def user(db):
    u = User(
        username='kopciuszek',
        email='k@lib.pl',
        password_hash=generate_password_hash('pantofelek'),
        is_admin=False,
    )
    db.session.add(u)
    db.session.commit()
    return u


@pytest.fixture
def admin(db):
    a = User(
        username='admin',
        email='admin@lib.pl',
        password_hash=generate_password_hash('puchatek123'),
        is_admin=True,
    )
    db.session.add(a)
    db.session.commit()
    return a


@pytest.fixture
def logged_in_client(client, user):
    client.post('/auth/login', data={
        'username': 'kopciuszek',
        'password': 'pantofelek',
    })
    return client


@pytest.fixture
def logged_in_admin_client(client, admin):
    client.post('/auth/login', data={
        'username': 'admin',
        'password': 'puchatek123',
    })
    return client
