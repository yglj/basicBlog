import sqlite3
from flaskr.db import get_db
import pytest

# 测试查询异常数据库是否关闭
def test_close_db(app):
    with app.app_context():
        db = get_db()
        assert db == get_db()    # 只建立一个连接

    with pytest.raises(sqlite3.ProgrammingError) as e:  # pytest.raises() 接受异常类交由pytest
        db.execute('select 1')
        assert 'closed' in str(e)


# 测试命令行初始化数据库成功
def test_init_db(monkeypatch, app, runner):
    class Recored:
        init_ok = False

    def fake_test_initdb():
        Recored.init_ok = True

    monkeypatch.setattr('flaskr.db.init_db', fake_test_initdb)
    click_info = runner.invoke(args=['init-db'])
    assert Recored.init_ok
    assert 'initialize' in click_info.output
