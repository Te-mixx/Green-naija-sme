import pytest
from flaskr import app as myapp, db


@pytest.fixture()
def app():
    # myapp['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
    app = myapp

    with app.app_context():
        db.create_all()

    print('DATABASE CREATED')
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()
