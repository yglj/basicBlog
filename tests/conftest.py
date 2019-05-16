import os
import pytest
import tempfile
from flaskr.db import init_db, get_db
from flaskr import create_app


with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf-8')


@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()

    app = create_app({
        'TESTING': True,
        'DATABASE': db_path,}
    )

    with app.app_context():
        init_db()
        db = get_db()
        db.executescript(_data_sql)

    yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


#  测试提交用户类, 用于用户登录登出动作
class authActions:
    def __init__(self, client):
        self._client = client

    def login(self, username='test', password='test'):
        response = self._client.post(
            '/auth/login',
            data={'username': username, 'password': password}
        )
        return response

    def logout(self):
        self._client.get('/auth/logout')


@pytest.fixture
def auth(client):
    return authActions(client)
