
from flask import (
    render_template, url_for, redirect, request, flash, Blueprint, abort, g
)
from .db import get_db
from .auth import login_required

bp = Blueprint('blog', __name__)


def get_post(pid, check_author=True):  # 修改、删除时要得到post， 同时检查是不是作者
    db = get_db()
    post = db.execute('select * from post where id=?', (pid,)).fetchone()
    if not post:
        abort(404)
    if check_author and g.user['id'] != post['author_id']:
        abort(403)
    return post


@bp.route('/')
def index():
    db = get_db()
    sql = '''select p.id, username, author_id, title, body, created
             from post p join user u on u.id = p.author_id
             order by created desc'''
    posts = db.execute(sql).fetchall()
    if posts is None:
        flash('暂无内容！')
    return render_template('blog/index.html', posts=posts)


@bp.route('/create', methods=['POST', 'GET'])
@login_required
def create():
    if request.method == 'POST':
        title = request.form["title"]
        body = request.form["body"]
        db = get_db()
        error = None
        if not title:
            error = 'title is Required!'

        if not error:
            db.execute('insert into post(title, body, author_id) '
                       'values(?, ?, ?)', (title, body, g.user["id"]))
            db.commit()
            return redirect(url_for('index'))

        flash(error)
    return render_template('blog/create.html')


@bp.route('/<int:pid>/update', methods=['POST', 'GET'])
@login_required
def update(pid):
    post = get_post(pid)
    if request.method == 'POST':
        title = request.form["title"]
        body = request.form["body"]
        db = get_db()
        error = None
        if not title:
            error = "title is Required!"

        if not error:
            sql = 'update post set title=?, body=? where id=?'
            db.execute(sql, (title, body, pid))
            db.commit()
            return redirect(url_for('index'))

        flash(error)
    return render_template('blog/update.html', post=post)


@bp.route('/<int:pid>/delete', methods=['POST'])
@login_required
def delete(pid):
    post = get_post(pid)
    db = get_db()
    db.execute('delete from post where id=?', (pid,))
    db.commit()
    return redirect(url_for('index'))

