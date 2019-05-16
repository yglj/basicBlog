import functools
from flask import (
    Blueprint, url_for, redirect, render_template, request, session, g, flash
)
from .db import get_db
from werkzeug.security import generate_password_hash, check_password_hash

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        db = get_db()
        if not username:
            error = '需要用户名！'
        elif not password:
            error = '需要密码！'
        else:
            if db.execute(
                    'select * from user where username=? ', (username, )
            ).fetchone() is not None:
                error = '用户{}已存在！'.format(username)

        if not error:
            db.execute('insert into user(username, password) values(?, ?)',
                       (username, generate_password_hash(password))
                       )
            db.commit()
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        db = get_db()
        # if not username:
        #     error = '需要用户名！'
        # elif not password:
        #     error = '需要密码！'

        user = db.execute(
                'select * from user where username=? ', (username,)
        ).fetchone()

        if not user:
            error = '用户不存在！'
        elif not check_password_hash(user['password'], password):  # check_password_hash 第一个参数是hash值
            error = '密码错误！ {}'.format(user['password'])

        if not error:   # 用户登录后，把用户id存入session
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


@bp.before_app_request  # 在每次请求调用视图函数前加载用户信息
def load_logged_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        db = get_db()   # 每次请求前拿到用户信息，响应后g对象销毁
        g.user = db.execute('select * from user where id = ?', (user_id,)).fetchone()


@bp.route('/logout')  # 退出要清空session
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:   # 从g对象的user是否为空，判断用户是否登录
            return redirect(url_for('auth.login'))
        return view(*args, **kwargs)
    return wrapped_view


@bp.route('/test')
def test():
    return render_template('base.html')
