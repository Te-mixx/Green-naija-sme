from flaskr.models import User
from flaskr import app


def test_home(client):
    res = client.get("/")
    print(res)
    assert res.status_code == 200


def test_registration(client, app):
    response = client.post('/register',
                           data={"username": "temisann",
                                 "email": "temisann@gmail.com",
                                 "company_name": "green naijasme",
                                 "company_description": "An organization that \
                                 provides a Decision support web application \
                                 for the Carbon footprint reduction in  \
                                 Nigerian SMEs",
                                 "address": "12, efik street, warri, Nigeria",
                                 "city": "Warri",
                                 "state": "Edo State",
                                 "zip": "123456",
                                 "password": "password"})

    with app.app_context():
        assert User.query.count() == 1
        assert User.query.first().email == "temisann@gmail.com"
