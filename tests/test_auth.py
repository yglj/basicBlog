from flaskr import create_app
from flaskr.db import get_db
from flask import session, g
import pytest


def test_register(client, username='a', password='a'):
    assert client.get('/auth/register').status_code == 200

    response = client.post('/auth/register',
                           data={'username': username, 'password': password}
                           )
    assert 'http://localhost/auth/login' == response.headers['Location']

    with create_app().app_context():
        assert get_db().execute(
            'select * from user').fetchall() is not None


@pytest.mark.parametrize(
    ('username', 'password', 'message'),
    (('', 'a', 'needed username'.encode('utf-8')), ('a', '', 'needed password'.encode('utf-8')), ('test', 'test', '用户test已存在'.encode('utf-8')))
)
def test_invaild_register_input(client, username, password, message):
    response = client.post('/auth/register',
                           data={'username': username, 'password': password})
    assert message in response.data


def test_login(client, auth):
    assert client.get('/auth/login').status_code == 200

    response = auth.login()

    assert 'http://localhost/' == response.headers['Location']

    with client:
        with client.get('/'):
            assert 'user_id' in session
            assert g.user['username'] == 'test'


@pytest.mark.parametrize(
    ('username', 'password', 'message'),
    (('1', 'a', '用户不存在'.encode('utf-8')), ('test', 'xx', '密码错误'.encode('utf-8')))
)
def test_invaild_login_input(auth, username, password, message):
    response = auth.login(username, password)
    assert message in response.data


def test_logout(auth, client):
    auth.login()
    with client:
        auth.logout()
        assert 'user_id' not in session
