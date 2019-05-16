from flaskr.db import get_db
import pytest

def test_index(client):
    assert client.get('/').status_code == 200
    response = client.get('/')
    assert '登录'.encode('utf-8') in response.data
    assert '注册'.encode('utf-8') in response.data


@pytest.mark.parametrize('path',
                         ('/create', '/1/update', '/1/delete'))
def test_login_require(client, path):
    response = client.post(path)
    assert 'http://localhost/auth/login' in response.headers['Location']


@pytest.mark.parametrize('path',
                         ('/1/update', '/1/delete'))
def test_author_require(app, auth, client, path):
    with app.app_context():
        db = get_db()
        db.execute('update post set author_id=? where id=?', (2, 1))
        db.commit()

    auth.login()
    assert client.post(path).status_code == 403
    assert b'href=/1/update' not in client.get('/').data


@pytest.mark.parametrize('path',
                         ('/2/update', '/2/delete'))
def test_exist_require(app, client, auth, path):
    # with app.app_context():
    #     db = get_db()
    #     db.execute('update post set id=? where id=1', (2,))
    #     db.commit()

    auth.login()
    response = client.post(path)
    assert response.status_code == 404


def test_create(client, auth, app):
    auth.login()
    client.post('/create',
                data={'title': 'created', 'body': ''})
    with app.app_context():
        count = get_db().execute('select count(id) from post ').fetchone()[0]
        assert count == 2


def test_update(app, client, auth):
    auth.login()
    client.post('/1/update', data={'title': 'updated', 'body': ''})
    with app.app_context():
        post = get_db().execute('select * from post where id=?', (1,)).fetchone()
        assert 'updated' in post['title']


@pytest.mark.parametrize('path',
                         ('/create', '/1/update'))
def test_create_update_invaild(auth, client, path):
    auth.login()
    response = client.post(path, data={'title': '', 'body': ''})
    assert b"title is Required!" in response.data


def test_delete(auth, client, app):
    auth.login()
    response = client.post('/1/delete')
    assert response.headers['Location'] == 'http://localhost/'
    with app.app_context():
        post = get_db().execute('select * from post where id = 1 ').fetchone()
        assert post is None

