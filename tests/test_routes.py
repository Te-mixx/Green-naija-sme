from flaskr.models import User
from flaskr import app


def test_home(client):
    res = client.get("/")
    assert res.status_code == 200


def test_register(client):
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

    assert response.status_code == 200
    with app.app_context():
        assert User.query.count() == 1
        assert User.query.first().email == "temisann@gmail.com"


def test_login(client):
    client.post('/register', 
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
    res = client.post("/login", data={"username": "temisann", 
                                      "email": "temisann@gmail.com"})
    assert res.status_code == 200


def test_about(client):
    res = client.get("/about")
    assert res.status_code == 200


def test_calculate(client):
    client.post('/register',
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
    res = client.post("/login", data={"username": "temisann",
                                      "email": "temisann@gmail.com"})
    res = client.get("/calculate")
    assert res.status_code == 302


def test_account(client):
    client.post('/register',
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
    res = client.post("/login", data={"username": "temisann",
                                      "email": "temisann@gmail.com"})
    res = client.get("/account")
    assert res.status_code == 302


def test_logout(client):
    res = client.get("/logout")
    assert res.status_code == 302
