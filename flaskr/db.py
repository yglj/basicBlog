# coding: utf-8
import sqlite3
from flask import g, current_app
from flask.cli import with_appcontext
import click


# 获取数据库连接
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(database=current_app.config['DATABASE'],  # key要写对，区分大写
                               detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row

    return g.db


# 关闭数据库连接
def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


# 初始化数据库
def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf-8'))  # 打开的资源是二进制字符串，必须解码为utf-8


# 命令行初始化命令
@click.command('init-db')
@with_appcontext
def init_cli_command():
    init_db()
    click.echo("database initialize finish!")


#  函数注册到应用
def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_cli_command)
