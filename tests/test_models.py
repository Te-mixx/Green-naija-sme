from flaskr.models import User


def test_models():
    user = User(username='temisann', email='temisann@gmail.com',
                company_name='green naijasme',
                company_description='An organization that provides a Decision support web application for the Carbon footprint reduction in Nigerian SMEs',
                address='12, efik street, warri, Nigeria',
                city='Warri',
                state='Edo State',
                zip='123456',
                password='password')

    assert user.email == 'temisann@gmail.com'
    assert user.company_name == 'green naijasme'
