from flaskr import create_app


# 测试配置能否启用
def test_config():
    assert not create_app().testing
    assert create_app({'TESTING': True}).testing


def test_hello(client):
    response = client.get('/hello/')
    assert b'hello world!' in response.data
