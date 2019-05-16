# Tutorial

这个教程将会从到尾创建一个最基本的博客应用，名字叫Flaskr。

用户可以注册，登录，发贴，并可以编辑或者删除自己的帖子。

这个教程不包含所有特性，更多内容请深入更多的文档。

只使用Flask和Python，你可以使用扩展库做一些简单的任务。

[Extensions](http://flask.pocoo.org/docs/1.0/extensions/#extensions)



Flask非常灵活，它不需要你使用任何特别的工程或代码布局， 它不要求您使用任何特定项目或代码布局。 但是，首次启动时，使用更结构化的方法会很有帮助。 这意味着该教程需要预先考虑一些样板，但这样做是为了避免新开发人员遇到的许多常见陷阱，并创建一个易于扩展的项目。 一旦你对Flask更加舒适，你可以走出这个结构并充分利用Flask的灵活性。

https://github.com/pallets/flask/tree/1.0.2/examples/tutorial

#Project  Layout

创建一个目录  flask-blog, 并进入目录设置一个python虚拟环境

但是，随着项目变得越来越大，将所有代码保存在一个文件中变得势不可挡。 Python项目使用包将代码组织成多个模块，可以在需要的地方导入。

这个工程目录包含:

- `flaskr/`, 一个包含应用代码和文件的python包。
- `tests/`,一个包含测试模块的目录.
- `venv/`, 安装了Flask和其他依赖的python虚拟环境。
- Installation files 告诉python如何安装你的应用.
- 版本控制配置,例如git。 You should make a habit of using some type of version control for all your projects, no matter the size.
- 其他可能添加的工程文件。

工程目录结构:

```
/home/user/Projects/flask-tutorial
├── flaskr/
│   ├── __init__.py
│   ├── db.py
│   ├── schema.sql
│   ├── auth.py
│   ├── blog.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── auth/
│   │   │   ├── login.html
│   │   │   └── register.html
│   │   └── blog/
│   │       ├── create.html
│   │       ├── index.html
│   │       └── update.html
│   └── static/
│       └── style.css
├── tests/
│   ├── conftest.py
│   ├── data.sql
│   ├── test_factory.py
│   ├── test_db.py
│   ├── test_auth.py
│   └── test_blog.py
├── venv/
├── setup.py
└── MANIFEST.in
```

如果你使用版本控制，根据你自己的需要，把要忽略的文件写在.gitignore。

`.gitignore`

```
venv/

*.pyc
__pycache__/

instance/

.pytest_cache/
.coverage
htmlcov/

dist/
build/
*.egg-info/
```

#Application Setup

一个Flask应用就是一个Flask类实例，关于应用的一切，例如配置和URLs，将会被注册到这个类。

最直接的方式是在代码顶部创建一个全局Flask实例，随着项目增长，会导致一些问题

工厂模式创建：在函数内部创建Flask实例，此函数叫做应用程序工厂。应用程序需要的任何配置、注册、和其他设置都在函数内部进行，然后返回应用程序。

##The Application Factory

开始编码，创建flaskr目录，增加一个`__init__.py`文件。这个文件有两个作用：它将包含应用工厂；

告诉Python解释器flaskr目录将被当做一个包。

`mkdir flaskr`

`flaskr/__init__.py`

```python
import os

from flask import Flask


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    return app
```

`create_app`是应用工厂函数。

1. `app = Flask(__name__,  instance_relative_config=True)`

   创建Flask应用实例

   - `__name__` 是当前Python模块的名字。应用需要`__name__`告诉它在哪里设置一些路径。
   - `instance_relative_config=True` 告诉应用配置文件应该相对实例文件来寻找。实例文件夹位于flask包的外部，可以保存本地数据而不应提交给版本控制，例如秘钥配置、数据库文件。

2. `app.config.from_mapping()`为应用设置默认配置：

   - [`SECRET_KEY`](http://flask.pocoo.org/docs/1.0/config/#SECRET_KEY)  Flask 和扩展程序 使用它保证数据安全。它被设为“dev”以方便在开发过程中使用，但在部署应该使用随机值。
   - `DATABASE` 数据库文件保存路径。在 [`app.instance_path`](http://flask.pocoo.org/docs/1.0/api/#flask.Flask.instance_path)路径下, 这是Flask为实例文件夹选择的路径。

3. `app.config.from_pyfile()`使用从实例文件夹中的config.py文件获取的值覆盖默认配置（如果存在）。

   例如，在部署时，可用于设置真正的SECRET_KEY。


   - `test_config` 也可通过工厂设置，并将替代实例配置。在编写测试后使用它可以独立于应用配置。

4. [`os.makedirs()`](https://docs.python.org/3/library/os.html#os.makedirs)确保 [`app.instance_path`](http://flask.pocoo.org/docs/1.0/api/#flask.Flask.instance_path)路径存在。 Flask不会自动创建实例文件夹，但它是必要的，因为项目会在实例目录下创建SQLite数据库文件。

5. [`@app.route()`](http://flask.pocoo.org/docs/1.0/api/#flask.Flask.route) 创建一个简单的路由，查看应用程序的正常工作。它会在 URL `/hello` 和一个返回响应函数之间创建一个连接。

##Run  The Application

使用Flask命令运行程序，在终端，告诉它去哪找你的应用程序，然后在开发模式下运行它。

开发模式显示一个交互调试器，当网页抛出异常或者代码变动时就会重启服务器。

For Linux  and Mac:

```
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run
```

For Windows cmd,use set instead of export.

在浏览器访问http://127.0.01:5000/hello 

#Define and Access the Database

这个应用将使用SQLite数据库存储用户和博文，Python在sqlite3模块中内置了对SQLite的支持。

SQLite很方便，因为它不需要设置单独的数据库服务器并且内置于Python。但是，如果尝试把并发请求同时写入数据库，则每次顺序执行写入将变的很慢，小应用程序不会注意到这一点。一旦数据量变大，可切换到其他数据库。

在Web应用程序中，数据库连接通常与请求相关联。它在处理请求时在某个时刻创建，并在发送响应之前关闭。

`flaskr/db.py`

```python
import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()
```

[`g`](http://flask.pocoo.org/docs/1.0/api/#flask.g)是每个请求唯一存在的特殊对象，用于存储请求期间可能被多个函数访问的数据。如果在同一个请求中第二次调用get_db，这个数据库连接会被存储并被重用，而不是创建新的连接。

[`current_app`](http://flask.pocoo.org/docs/1.0/api/#flask.current_app)是另一个应用处理请求的特殊对象。使用应用程序工厂创建应用，编写其他代码时没有应用程序对象，当应用程序被创建去处理请求时用current_app去调用get_db。

[`sqlite3.connect()`](https://docs.python.org/3/library/sqlite3.html#sqlite3.connect) 建立与配置键中`DATABASE` 指向的文件的连接. 在初始化数据库之前这个文件不会存在。

[`sqlite3.Row`](https://docs.python.org/3/library/sqlite3.html#sqlite3.Row)告诉连接返回的每行结果象一个dicts数据类型，允许通过字段名访问列。

`close_db` 检查数据库连接是关闭，如果g.db设置的数据库连接存在，则关闭。在后面会设置应用程序在每次请求后调用它关闭连接。

##Create the Tables

在SQLite,数据被存在表和列中。在存储相关数据之前要创建相关表。 Flaskr存储用户在 `user` table,  posts在`post` table。创建一个带有SQL命令的文件去创建空表:

`flaskr/schema.sql`

```
DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE post (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  FOREIGN KEY (author_id) REFERENCES user (id)
);
```

Add the Python functions that will run these SQL commands to the `db.py` file:

`flaskr/db.py`

```python
def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')
```

[`open_resource()`](http://flask.pocoo.org/docs/1.0/api/#flask.Flask.open_resource) 在 `flaskr` 包下打开相关文件, 当你部署之后不需要知道它在哪个位置。执行从文件中读取的数据库命令。

[`click.command()`](http://click.pocoo.org/api/#click.command) 定义一个命令行命令叫 `init-db` ，它会调用init_db函数并返回命令行信息给用户。阅读 [Command Line Interface](http://flask.pocoo.org/docs/1.0/cli/#cli)学会写更多的命令行命令.

##Register with the Application

`close_db` and `init_db_command` 功能函数需要注册到应用实例, 否则将不会被应用使用。由于使用的是工厂函数，在编写该函数时应用还不能用。所以要编写一个拿到应用实例（传参）并对需要注册的函数进行注册的函数。

`flaskr/db.py`

```python
def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
```

[`app.teardown_appcontext()`](http://flask.pocoo.org/docs/1.0/api/#flask.Flask.teardown_appcontext) 告诉Flask 在返回响应后清理时调用该函数。

[`app.cli.add_command()`](http://click.pocoo.org/api/#click.Group.add_command) 添加一个可以使用flask命令调用的新命令。

在工厂里导入并调用这个函数。 

`flaskr/__init__.py`

```
def create_app():
    app = ...
    # existing code omitted

    from . import db
    db.init_app(app)

    return app
```

##Initialize the Database File

使用 `flask` 命令调用 `init-db` ，初始化数据库文件。

注意：如果已经运行服务器，则可以停止服务器，也可以在新终端中运行此命令。如果您使用新终端，请记住更改到项目目录并激活env。还需要设置FLASK_APP和FLASK_ENV。

Run the `init-db` command:

```
flask init-db
Initialized the database.
```

 `flaskr.sqlite` 文件将出现在 `instance` 目录下。

# Blueprints and Views

视图函数是应用用于响应请求的代码。 Flask 使用模式将传入的请求URL与应该处理它的视图函数相匹配。Flask把视图函数返回的数据变为http响应 。Flask 也可以基于名称和参数生成新的URL，把它转向另一个视图函数。

## Create a Blueprint

   	 蓝图是一种组织一组相关视图和其他代码的方法。它们不是直接在应用程序中注册视图和其他代码，而是使用蓝图进行注册。然后在工厂函数中将蓝图注册到应用程序。

​	Flaskr将有两个蓝图，一个用于身份验证功能，另一个用于博客帖子功能。每个蓝图的代码都将在一个单独的模块中。由于博客需要身份验证，因此可以先编写身份验证。

`flaskr/auth.py`

```python
import functools
from flask import (
	Blueprint, flash, g, redirect,  render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_perfix='/auth')
```

这里创建一个叫 `'auth'`的蓝图。如同一个应用对象，蓝图需要知道在哪里定义了它，所第二个参数需要指定位置。  `url_prefix`将会添加到所有关联到蓝图的URL之前。 

 [`app.register_blueprint()`](http://flask.pocoo.org/docs/1.0/api/#flask.Flask.register_blueprint)使用工厂导入并注册蓝图。

`flaskr/__init__.py`

```python
def create_app()
	app = ...
	#	existing code omitted
    
	from . improt auth
	app.register_blueprint(auth.bp)
```

用户蓝图需要注册新用户、登录、登出的视图。

## The First View: Register

当用户访问 `/auth/register` URL, `register` 视图将返回一个 带有表单的[HTML](https://developer.mozilla.org/docs/Web/HTML)以供用户填写。 用户提交表单后,它将验证用户输入并再次显示带有错误消息的表单或是创建新用户并转到登录页面。

`flaskr/auth.py`

```python
@bp.route('/register', methods=('GET', 'POST'))
def register():
    error = None
    if request.method == "POST":
        name = request.form["username"]
        password = request.form["username"]
        if not username:
            error = "Username is required"
        elif not password:
            error = "Password is required"
        else:
            db = get_db()
            if db.execute(
            	'select id form userwhere username = ?' % (username,)
            ).fetchone() is not None:
                error = 'User {} already registered'.format(username)
         if error is None:
            password_hash = generate_password_hash(password)
            db.execute("insert into user(username, password) values(?, ?)", (username, password_hash))
            db.commit()
        	return redirect(url_for('login'))
        
        flash(error)
        
    return render_template('register.html')
```

 `register` 视图函数做了这几件事:

1. [`@bp.route`](http://flask.pocoo.org/docs/1.0/api/#flask.Blueprint.route) 将 URL `/register`关联到 `register` 视图函数。当应用接受到“`auth/register`的请求时，它会调用`register` 视图并返回值作为响应内容。

2. 如果用户递交表单， [`request.method`](http://flask.pocoo.org/docs/1.0/api/#flask.Request.method)方法为`'POST'`. 这种情况下，开始校验用户输入。

3. [`request.form`](http://flask.pocoo.org/docs/1.0/api/#flask.Request.form)是一种特殊类型的 [`dict`](https://docs.python.org/3/library/stdtypes.html#dict) 映射，用于提交存放表单提交的键和值。

4. 验证`username` and `password`不为空。

5. 验证 `username`是否已经被注册，通过查询数据库得到返回值来检查。 [`db.execute接收`](https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection.execute)一个 使用`?` 占位符来代替用户输入的SQL 查询字符串，对于任意用户输入，放到元组里来替换占位符。 数据库库将负责转义值，因此您不容易受到SQL注入攻击。

   [`fetchone()`](https://docs.python.org/3/library/sqlite3.html#sqlite3.Cursor.fetchone) 返回查询中的一行。若查询无返回结果，他会返回None。

    [`fetchall()`](https://docs.python.org/3/library/sqlite3.html#sqlite3.Cursor.fetchall) 被用于返回所有查询结果。

6. 如果验证成功， 向数据库插入新的用户数据。安全考虑，密码不应该直接存储到数据库，而是使用,[`generate_password_hash()`](http://werkzeug.pocoo.org/docs/utils/#werkzeug.security.generate_password_hash) 生成安全的被哈希运算过的密码值, 这个hash值会被存到数据库。在做完修改数据的查询后,调用 [`db.commit()`](https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection.commit) 保存更改。

7. 存储用户后,会重定向到登录页。  [`url_for()`](http://flask.pocoo.org/docs/1.0/api/#flask.url_for) 基于视图函数名字生成 关于登录视图的URL 。这比直接编写URL更好，因为它允许您之后更改URL时不需要更改链接到它的所有代码。 

8. 如果验证成功失败, error的信息将展示给用户。 [`flash()`](http://flask.pocoo.org/docs/1.0/api/#flask.flash) 存储在渲染模板是可以重写的信息。

9. 用户开始导航到 `auth/register`, 或者验证出错, 一个HTML 注册页将重新展示给用户。[`render_template()`](http://flask.pocoo.org/docs/1.0/api/#flask.render_template) 渲染包含html的模板。

## Login

该视图遵循与上面的注册视图相同的模式。

`flaskr/auth.py`

```python
@bp.route('/login', methods=['POST', 'GET'])
def login():
	if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        db = get_db()
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()
        if not username:
            error = 'Username is Required'
        elif not password:
	        error = 'Password is Required'
        else:
            if not user:
                error = '用户名或密码不存在 | Incorrect username'
            elif not check_password_hash(password, user['password']):
                error = '密码错误！| Incorrect password'
        if not error:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))
        flash(error)
    return render_template('login.html')
```

和 `register` view有几个不同的地方:

1. 首次查询用户是把它存储到变量中以供之后使用。
2. [`check_password_hash()`](http://werkzeug.pocoo.org/docs/utils/#werkzeug.security.check_password_hash)安全地比较存储的哈希值和按相同方式哈希运算提交的密码。如果匹配，则密码有效。
3. [`session`](http://flask.pocoo.org/docs/1.0/api/#flask.session) 是一个跨请求存储数据的 [`dict`](https://docs.python.org/3/library/stdtypes.html#dict) ，验证成功后用户的`id` 将存储在新会话中。然后这些数据被存在发往浏览器的cookie中，浏览器将其在后续请求中发回， Flask会安全地对cookie数据签名，以便不会被篡改。

现在用户的id存储在会话中，它将在后续请求中使用。在每个请求开始时，如果用户已登录，则应加载其信息并使其可供其他视图使用。

`flaskr/auth.py`

```python
@bp.before_app_request
def load_logged_in_user():
	if 'user_id' in session:
        db = get_db()
        g.user = db.execute('select * from user where id = ?', (session['user_id'],)
                           ).fetchone()
     else:
        g.user = None
```

[`bp.before_app_request()`](http://flask.pocoo.org/docs/1.0/api/#flask.Blueprint.before_app_request), 注册一个在视图函数调用前运行的函数，无论请求什么url。`load_logged_in_user` 检查用户id是否存储在会话中并从数据库获取该用户数据，并将其存储在g.user中，其生存周期为整个请求长度。如果数据里没有那个id，则g.user返回None。

## Logout

登出时要删除[`session`](http://flask.pocoo.org/docs/1.0/api/#flask.session)的用户ID。  `load_logged_in_user` 在之后的请求不再加载用户信息。

`flaskr/auth.py`

```python
@bp.route('/logout')
def logout():
	session.clear()
    return redirect(url_for('index'))
```

## Require Authentication in Other Views

创建、编辑、删除博客文章需要用户登录。一个装饰器用于检查用户登录提供给需要的每个视图。

`flaskr/auth.py`

```python
def login_required(view):
    @functools.wraps(viw)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
	    return view(*args, **kwargs)
    return wrapped_view
```

这个装饰器返回一个新的视图函数，它包装了它应用的原始视图。新函数检查用户是否已加载，否则重定向到登录页面。如果加载了用户，则调用原始视图并继续正常。在编写博客视图时，您将使用此装饰器。

## Endpoints and URLs

 url_for（）函数根据名称和参数生成视图的URL。与视图关联的名称也称为端点，默认情况下它与视图函数的名称相同。

例如，在教程前面添加到app工厂的hello（）视图具有名称'hello'并且可以与url_for（'hello'）链接。如果它接受了一个参数，你将在后面看到，它将链接到使用url_for（'hello'，who ='World'）。

当使用蓝图时，蓝图的名称前面加上名称函数，所以你上面写的登录函数的端点是'auth.login'，因为你把它添加到'auth'蓝图中。



# Templates

当你写完用户视图后运行服务器，尝试访问任何地址, 你都会看到 `TemplateNotFound` 错误。 这是因为视图函数会调用 [`render_template()`](http://flask.pocoo.org/docs/1.0/api/#flask.render_template), 但是模板还不存在。 模板文件放在flaskr包 `templates` 下。

模板文件包含静态数据和动态数据的占位符。使用特定数据呈现模板以生成最终文档。 Flask使用Jinja模板库来渲染模板。

在应用程序中，您将使用模板呈现HTML，该HTML将显示在用户的浏览器中。在Flask中，Jinja被配置为自动显示在HTML模板中呈现的任何数据。这意味着呈现用户输入是安全的。他们输入的某些字符可能会弄乱HTML，例如“<”和">"使用安全值进行转义，这些转义过的值在浏览器中看起来相同但不会产生不良影响。

Jinja语法看起来象Python。特殊分隔符用于区分Jinja语法与模板中的静态数据。 任何在`{{` 和`}}` 之间的内容都是输出到最终文档的表达式。 `{%` 和`%}` 表示控制流语句，象 `if` 和`for` 。与Python不同，块由开始和结束标记而不是缩进表示，因为块内的静态文本可能会更改缩进。

## The Base Layout

应用程序中的每个页面将围绕不同的主体具有相同的基本布局。每个模板不是在整个模板中编写全部HTML结构，而是扩展基本模板并覆盖特定部分。

`flaskr/templates/base.html`

```html
<!doctype html>
<title>{% block title %}{% endblock %} - Flaskr</title>
<link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
<nav>
  <h1>Flaskr</h1>
  <ul>
    {% if g.user %}
      <li><span>{{ g.user['username'] }}</span>
      <li><a href="{{ url_for('auth.logout') }}">Log Out</a>
    {% else %}
      <li><a href="{{ url_for('auth.register') }}">Register</a>
      <li><a href="{{ url_for('auth.login') }}">Log In</a>
    {% endif %}
  </ul>
</nav>
<section class="content">
  <header>
    {% block header %}{% endblock %}
  </header>
  {% for message in get_flashed_messages() %}
    <div class="flash">{{ message }}</div>
  {% endfor %}
  {% block content %}{% endblock %}
</section>
```

[`g`](http://flask.pocoo.org/docs/1.0/api/#flask.g)在模板中自动可用。基于设置了g.user(从LOAD_LOGLOGIN_USER)，登录用户将显示用户名和注销链接，否则将显示注册和登录链接。URL_for()也是自动可用的，用于生成视图的URL，而不是手动写出它们。

在页面标题之后，并且在内容之前，模板循环通过get_flash_messages()返回的每个消息。在视图中使用Flash()以显示错误消息，而这是将显示错误消息的代码。

这里定义的三个块将在其他模板中被覆盖：

1. `{% block title %}` 将更改浏览器选项卡和窗口标题中显示的标题。
2. `{% block header %}`与标题相似，但将更改页面上显示的标题。
3. `{% block content %}`是每个页面的具体内容，例如登录表单或博客帖子。

基本模板直接位于模板目录中。为了保持组织性，蓝图模板将放置在与蓝图同名的目录中。

## Register

`flaskr/templates/auth/register.html`

```html
{% extends 'base.html' %}

{% block header %}
  <h1>{% block title %}Register{% endblock %}</h1>
{% endblock %}

{% block content %}
  <form method="post">
    <label for="username">Username</label>
    <input name="username" id="username" required>
    <label for="password">Password</label>
    <input type="password" name="password" id="password" required>
    <input type="submit" value="Register">
  </form>
{% endblock %}
```

`{% extends 'base.html' %}`告诉Jinja，这个模板应该替换基模板中的块。所有呈现的内容必须出现在覆盖基模板中的块的{% block %}标记中。

A useful pattern used here is to place `{% block title %}` inside `{% block header %}`.这将设置标题块，然后将其值输出到标头块中，以便窗口和页面共享相同的标题，而无需编写两次。

The `input` tags are using the `required` attribute here. 这告诉浏览器在填写这些字段之前不要提交表单。如果用户使用的是不支持该属性的旧浏览器，或者是使用浏览器以外的其他工具来发出请求，则仍然希望验证flask视图中的数据。始终充分验证服务器上的数据非常重要，即使客户机也进行了一些验证。

## Log In

这与注册模板相同，除了标题和提交按钮外。

`flaskr/templates/auth/login.html`

```html
{% extends 'base.html' %}

{% block header %}
  <h1>{% block title %}Log In{% endblock %}</h1>
{% endblock %}

{% block content %}
  <form method="post">
    <label for="username">Username</label>
    <input name="username" id="username" required>
    <label for="password">Password</label>
    <input type="password" name="password" id="password" required>
    <input type="submit" value="Log In">
  </form>
{% endblock %}
```

## Register A User

既然已经编写了身份验证模板，就可以注册用户了。 Make sure the server is still running (`flask run` if it’s not), then go to <http://127.0.0.1:5000/auth/register>.

尝试点击“注册”按钮，而不填写表单，并看到浏览器显示错误信息。尝试从Regier.html模板中删除 `required` 属性，然后再次单击“Register”。现在不是浏览器显示错误，页面将重新加载，并将显示来自flash()视图中的错误。

填写用户名和密码，您将被重定向到登录页面。尝试输入一个不正确的用户名，或正确的用户名和错误的密码。如果您登录，将得到一个错误，因为还没有可重定向的索引视图。



# Static Files

身份验证视图和模板可以工作，但它们现在看起来非常简单。可以添加一些CSS来将样式添加到您构建的html布局中。样式不会改变，所以它是一个静态文件，而不是模板。

Flask自动添加一个static视图，该视图相对于flaskr/static目录采取路径并为其服务。html模板已经有到style.css文件的链接：

```
{{ url_for('static', filename='style.css') }}
```

除了CSS，其他类型的静态文件可能是带有javascript函数的文件或log图像。它们都放在flaskr/静态目录下，并使用url_for('static', filename='...')。

本教程不关注如何编写CSS，因此您只需将以下内容复制到flaskr/静态/style.css文件中：`flaskr/static/style.css` file:

`flaskr/static/style.css`

```
html { font-family: sans-serif; background: #eee; padding: 1rem; }
body { max-width: 960px; margin: 0 auto; background: white; }
h1 { font-family: serif; color: #377ba8; margin: 1rem 0; }
a { color: #377ba8; }
hr { border: none; border-top: 1px solid lightgray; }
nav { background: lightgray; display: flex; align-items: center; padding: 0 0.5rem; }
nav h1 { flex: auto; margin: 0; }
nav h1 a { text-decoration: none; padding: 0.25rem 0.5rem; }
nav ul  { display: flex; list-style: none; margin: 0; padding: 0; }
nav ul li a, nav ul li span, header .action { display: block; padding: 0.5rem; }
.content { padding: 0 1rem 1rem; }
.content > header { border-bottom: 1px solid lightgray; display: flex; align-items: flex-end; }
.content > header h1 { flex: auto; margin: 1rem 0 0.25rem 0; }
.flash { margin: 1em 0; padding: 1em; background: #cae6f6; border: 1px solid #377ba8; }
.post > header { display: flex; align-items: flex-end; font-size: 0.85em; }
.post > header > div:first-of-type { flex: auto; }
.post > header h1 { font-size: 1.5em; margin-bottom: 0; }
.post .about { color: slategray; font-style: italic; }
.post .body { white-space: pre-line; }
.content:last-child { margin-bottom: 0; }
.content form { margin: 1em 0; display: flex; flex-direction: column; }
.content label { font-weight: bold; margin-bottom: 0.5em; }
.content input, .content textarea { margin-bottom: 1em; }
.content textarea { min-height: 12em; resize: vertical; }
input.danger { color: #cc2f2e; }
input[type=submit] { align-self: start; min-width: 10em; }
```

You can find a less compact version of `style.css` in the [example code](https://github.com/pallets/flask/tree/1.0.2/examples/tutorial/flaskr/static/style.css).

Go to <http://127.0.0.1:5000/auth/login> and the page should look like the screenshot below.

You can read more about CSS from [Mozilla’s documentation](https://developer.mozilla.org/docs/Web/CSS). 

如果更改静态文件，请刷新浏览器页。如果未显示更改，请尝试清除浏览器的缓存



# Blog Blueprint

您将使用编写身份验证蓝图时学到的相同技术来编写博客蓝图。博客应该列出所有的帖子，允许登录的用户创建帖子，并允许文章的作者编辑或删除它。在实现每个视图时，请保持开发服务器运行。在保存更改时，尝试访问浏览器中的url并对其进行测试。

## The Blueprint

定义蓝图并在应用程序工厂注册。

`flaskr/blog.py`

```python
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('blog', __name__)
```

从工厂导入并注册蓝图，在返回应用程序之前，将新代码放在工厂函数的末尾。.

`flaskr/__init__.py`

```python
def create_app():
    app = ...
    # existing code omitted

	from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')
    
    return app
```

与AUTH蓝图不同，博客蓝图没有url_前缀。因此，索引视图将位于/，Create视图在/create，依此类推。blog是flaskr的主要特性，因此博客索引将成为主要索引是有意义的。

但是，下面定义的索引视图的端点将是blog.index。一些身份验证视图引用了普通索引端点。app.add_url_Rule()将端点名称‘index’与 `/` url 关联起来，以便url_for(‘index’)或url_for(‘blog.index’)都能工作，从而生成相同的 `/` url 。

在另一个应用程序中，您可能会给博客蓝图一个url_前缀，并在应用程序工厂中定义一个单独的索引视图，类似于hello视图。那么索引和blog.index端点和URL就会不同了。

## Index

将显示所有的帖子，最近的第一次。使用一个联接，以便用户表中的作者信息在结果中可用

`flaskr/blog.py`

```
@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('blog/index.html', posts=posts)
```

`flaskr/templates/blog/index.html`

```
{% extends 'base.html' %}

{% block header %}
  <h1>{% block title %}Posts{% endblock %}</h1>
  {% if g.user %}
    <a class="action" href="{{ url_for('blog.create') }}">New</a>
  {% endif %}
{% endblock %}

{% block content %}
  {% for post in posts %}
    <article class="post">
      <header>
        <div>
          <h1>{{ post['title'] }}</h1>
          <div class="about">by {{ post['username'] }} on {{ post['created'].strftime('%Y-%m-%d') }}</div>
        </div>
        {% if g.user['id'] == post['author_id'] %}
          <a class="action" href="{{ url_for('blog.update', id=post['id']) }}">Edit</a>
        {% endif %}
      </header>
      <p class="body">{{ post['body'] }}</p>
    </article>
    {% if not loop.last %}
      <hr>
    {% endif %}
  {% endfor %}
{% endblock %}
```

当用户登录时，标题块会添加指向创建视图的链接。当用户是帖子的作者时，他们会看到指向该帖子的更新视图的“编辑”链接。 loop.last是Jinja for循环中可用的特殊变量。它用于在每个帖子之后显示除最后一个之外的一行，以便在视觉上将它们分开。

## Create

Create视图的工作方式与 auth `register` 视图相同。要么显示表单，要么验证发布的数据，然后将POST添加到数据库中，要么显示错误。

在博客视图中使用了您前面编写的LOGIN_Equired装饰器。用户必须登录才能访问这些视图，否则它们将被重定向到登录页面。

`flaskr/blog.py`

```
@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')
```

`flaskr/templates/blog/create.html`

```
{% extends 'base.html' %}

{% block header %}
  <h1>{% block title %}New Post{% endblock %}</h1>
{% endblock %}

{% block content %}
  <form method="post">
    <label for="title">Title</label>
    <input name="title" id="title" value="{{ request.form['title'] }}" required>
    <label for="body">Body</label>
    <textarea name="body" id="body">{{ request.form['body'] }}</textarea>
    <input type="submit" value="Save">
  </form>
{% endblock %}
```

## Update

更新和删除视图都需要按ID获取帖子，并检查作者是否与登录的用户匹配。为了避免代码重复，您可以编写一个函数来获取发布并从每个视图调用它。

`flaskr/blog.py`

```
def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post
```

[`abort()`](http://flask.pocoo.org/docs/1.0/api/#flask.abort)将引发一个返回HTTP状态代码的特殊异常。它需要一个可选的消息来显示错误，否则使用默认消息。 404表示“未找到”，403表示“禁止”。 （401表示“未授权”，但您重定向到登录页面而不是返回该状态。）

 定义了check_author参数，以便该函数可用于获取帖子而无需检查作者。如果您编写了一个视图来显示页面上的单个帖子，用户无关紧要，因为他们没有修改帖子，这将非常有用。

`flaskr/blog.py`

```
@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)
```

与您到目前为止所编写的视图不同，update函数采用参数id。这对应于路径中的<int:id>。真正的URL看起来像/ 1 / update。 Flask将捕获1，确保它是一个int，并将其作为id参数传递。如果你没有指定int：而是做 <id>，它将是一个字符串。要生成更新页面的URL，需要传递url_for（），以便知道要填写的内容：url_for（'blog.update'，id = post ['id']）。这也在上面的index.html文件中。

Create和UPDATE视图看起来非常相似。主要区别在于UPDATE视图使用POST对象和UPDATE查询而不是INSERT。通过一些巧妙的重构，您可以为这两个操作使用一个视图和模板，但是对于本教程来说，更清楚地将它们分开。

`flaskr/templates/blog/update.html`

```html
{% extends 'base.html' %}

{% block header %}
  <h1>{% block title %}Edit "{{ post['title'] }}"{% endblock %}</h1>
{% endblock %}

{% block content %}
  <form method="post">
    <label for="title">Title</label>
    <input name="title" id="title"
      value="{{ request.form['title'] or post['title'] }}" required>
    <label for="body">Body</label>
    <textarea name="body" id="body">{{ request.form['body'] or post['body'] }}</textarea>
    <input type="submit" value="Save">
  </form>
  <hr>
  <form action="{{ url_for('blog.delete', id=post['id']) }}" method="post">
    <input class="danger" type="submit" value="Delete" onclick="return confirm('Are you sure?');">
  </form>
{% endblock %}
```

此模板有两种形式。第一个页面将编辑后的数据发布到当前页面(`/<id>/update`)。另一个表单只包含一个按钮，并指定一个操作属性，该属性将发送到DELETE视图。该按钮在提交之前使用一些javascript来显示确认对话框。

模式{request.form[‘title’]或post[‘title’]}用于选择表单中显示的数据。当表单尚未提交时，将出现原始的POST数据，但是如果发布了无效的表单数据，则需要显示该数据，以便用户能够修复错误，因此使用request.form代替。request是模板中自动可用的另一个变量。

## Delete

DELETE视图没有自己的模板，DELETE按钮是update.html的一部分，并发布到`/<id>/delete` 。因为没有模板，所以它只处理POST方法，然后重定向到索引视图。

`flaskr/blog.py`

```
@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))
```

恭喜你，你已经完成了你的应用！花点时间尝试一下浏览器中的所有内容。然而，在项目完成之前还有更多的工作要做。





# Make the Project Installable

使您的项目可安装意味着您可以构建一个分发文件并将其安装在另一个环境中，就像您在项目环境中安装了flask一样。这使得部署项目就像安装任何其他库一样，所以您使用所有标准python工具来管理所有东西。

安装还带来了其他一些好处，这在本教程中或作为一个新的python用户可能并不明显，包括:

- 目前，python和flask只知道如何使用flaskr包，因为您是从项目的目录中运行的。安装意味着您可以导入它，无论您从哪里运行。
-  您可以像管理其他软件包一样管理项目的依赖项, so pip install yourproject.whl installs them.
- 测试工具可以将您的测试环境与开发环境隔离开来。

注意：这是在本教程后面介绍的，但是在您未来的项目中，您应该始终从这个开始。

## Describe the Project

The `setup.py`文件描述了您的项目及其所属的文件。

`setup.py`

```
from setuptools import find_packages, setup

setup(
    name='flaskr',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
    ],
)
```

`packages`告诉python要包含哪些包目录(以及它们包含的python文件)。find_Packages()自动查找这些目录，因此不必键入它们。若要包含其他文件(如静态和模板目录)，请设置include_Package_data。Python需要另一个名为MANIFEST.in的文件来判断其他数据是什么。

`MANIFEST.in`

```
include flaskr/schema.sql
graft flaskr/static
graft flaskr/templates
global-exclude *.pyc
```

这告诉python复制静态目录和模板目录以及schema.sql文件中的所有内容，但是要排除所有字节码文件。

See the [official packaging guide](https://packaging.python.org/tutorials/distributing-packages/) for another explanation of the files and options used.

## Install the Project

Use `pip` to install your project in the virtual environment.

```
pip install -e .
```

这告诉pip在当前目录中查找setup.py，并以可编辑或开发模式安装它。可编辑模式意味着，在对本地代码进行更改时，只有在更改有关项目的元数据(如其依赖项)时才需要重新安装。

您可以观察到，该项目现在已安装了pip列表。

```
pip list

Package        Version   Location
-------------- --------- ----------------------------------
click          6.7
Flask          1.0
flaskr         1.0.0     /home/user/Projects/flask-tutorial
itsdangerous   0.24
Jinja2         2.10
MarkupSafe     1.0
pip            9.0.3
setuptools     39.0.1
Werkzeug       0.14.1
wheel          0.30.0
```

到目前为止，您运行项目的方式没有什么变化。FLASK_APP仍然被设置为flaskr，flask run仍然运行应用程序。





# Test Coverage

为应用程序编写单元测试可以让您检查所编写的代码是否按照预期的方式工作。flask提供了一个测试客户端，它模拟对应用程序的请求并返回响应数据。

您应该尽可能多地测试您的代码。函数中的代码仅在调用函数时运行，而分支(如if块)中的代码仅在满足条件时才运行。您希望确保每个函数都使用覆盖每个分支的数据进行测试。

你越接近100%的覆盖范围，你就会越舒服，做一个改变不会意外地改变其他行为。但是，100%的覆盖率并不能保证您的应用程序没有bug。特别是，它不测试用户如何在浏览器中与应用程序交互。尽管如此，测试覆盖率仍然是开发过程中使用的重要工具。

注意：这是在本教程后面介绍的，但是在您未来的项目中，您应该在开发过程中进行测试。

You’ll use [pytest](https://pytest.readthedocs.io/) and [coverage](https://coverage.readthedocs.io/) to test and measure your code. Install them both:

```
pip install pytest coverage
```

## Setup and Fixtures

测试代码位于测试目录中。此目录位于flaskr包的旁边，而不是在其内部。py文件包含每个测试将使用的称为Fixtures的安装函数。测试在python模块中以`test_`开始，而这些模块中的每个测试函数也以`test_`开始。

每个测试都将创建一个新的临时数据库文件，并填充将在测试中使用的一些数据。编写一个SQL文件以插入该数据。

`tests/data.sql`

```
INSERT INTO user (username, password)
VALUES
  ('test', 'pbkdf2:sha256:50000$TCI4GzcX$0de171a4f4dac32e3364c7ddc7c14f3e2fa61f2d17574483f7ffbb431b4acb2f'),
  ('other', 'pbkdf2:sha256:50000$kJPKsz6N$d2d4784f1b030a9761f5ccaeeaca413f27f2ecb76d6168407af962ddce849f79');

INSERT INTO post (title, body, author_id, created)
VALUES
  ('test title', 'test' || x'0a' || 'body', 1, '2018-01-01 00:00:00');
```

`app` fixture将调用工厂并通过test_config来配置应用程序和数据库以进行测试，而不是使用本地开发配置。

`tests/conftest.py`

```python
import os
import tempfile

import pytest
from flaskr import create_app
from flaskr.db import get_db, init_db

with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')


@pytest.fixture  # 测试固件
def app():
    db_fd, db_path = tempfile.mkstemp()

    app = create_app({
        'TESTING': True,
        'DATABASE': db_path,
    })

    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)

    yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture  
def runner(app):
    return app.test_cli_runner()
```

[`tempfile.mkstemp()`](https://docs.python.org/3/library/tempfile.html#tempfile.mkstemp) 创建并打开一个临时文件，返回文件对象及其路径。数据库路径被重写，因此它指向此临时路径，而不是实例文件夹。设置路径后，将创建数据库表并插入测试数据。测试结束后，临时文件将关闭并删除。

[`TESTING`](http://flask.pocoo.org/docs/1.0/config/#TESTING) 告诉flask，应用程序是在测试模式。flask会改变一些内部行为，这样测试就更容易了，其他扩展也可以使用标志来使测试更容易。

 `client` fixture使用应用程序所创建的应用程序对象调用app.test_client()。测试将使用客户机在不运行服务器的情况下向应用程序发出请求。

The `runner` fixture is similar to `client`. [`app.test_cli_runner()`](http://flask.pocoo.org/docs/1.0/api/#flask.Flask.test_cli_runner) 创建一个运行程序，该运行程序可以调用在应用程序中注册的Click命令行命令。

pytest通过将其函数名与测试函数中的参数名称相匹配来使用 fixtures。例如，接下来要编写的test_hello函数使用一个客户端参数。pytest将这个值与`client` fixture函数匹配，调用它，并将返回的值传递给测试函数。



## Factory

关于工厂本身的测试并不多。大多数代码都将针对每个测试执行，因此如果某些内容失败，其他测试将会注意到。

唯一可以更改的行为是通过测试配置。如果没有传递配置，则应该有一些默认配置，否则配置应该被重写。

`tests/test_factory.py`

```python
from flaskr import create_app


def test_config():
    assert not create_app().testing
    assert create_app({'TESTING': True}).testing


def test_hello(client):
    response = client.get('/hello')
    assert response.data == b'Hello, World!'
```

在本教程开始时，您在编写工厂时添加了Hello路由作为示例。它返回“Hello，world！”，因此测试检查响应数据是否匹配。

## Database

在应用程序上下文中，get_db应在每次调用时返回相同的连接。在上下文之后，应该关闭连接。

`tests/test_db.py`

```
import sqlite3

import pytest
from flaskr.db import get_db


def test_get_close_db(app):
    with app.app_context():
        db = get_db()
        assert db is get_db()

    with pytest.raises(sqlite3.ProgrammingError) as e:
        db.execute('SELECT 1')

    assert 'closed' in str(e)
```

The `init-db` command should call the `init_db` function and output a message.

`tests/test_db.py`

```
def test_init_db_command(runner, monkeypatch):
    class Recorder(object):
        called = False

    def fake_init_db():
        Recorder.called = True

    monkeypatch.setattr('flaskr.db.init_db', fake_init_db)
    result = runner.invoke(args=['init-db'])
    assert 'Initialized' in result.output
    assert Recorder.called
```

此测试使用pytest的 `monkeypatch`  fixture 将init_db函数替换为记录调用它的函数。上面所写的`runner` fixture用于按名称调用init-db命令。

## Authentication

对于大多数视图，需要登录用户。在测试中执行此操作的最简单方法是向客户端的登录视图发出POST请求。而不是每次都写出来，你可以用方法编写一个类，并使用一个fixture将它传递给每个测试的客户端。

`tests/conftest.py`

```python
class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, username='test', password='test'):
        return self._client.post(
            '/auth/login',
            data={'username': username, 'password': password}
        )

    def logout(self):
        return self._client.get('/auth/logout')


@pytest.fixture
def auth(client):
    return AuthActions(client)
```

使用auth fixture，您可以在测试中调用auth.login（）以作为测试用户登录，该测试用户作为测试数据的一部分插入到app fixture中。

注册视图应在GET上成功呈现。在具有有效表单数据的POST上，它应该重定向到登录URL，并且用户的数据应该在数据库中。无效数据应显示错误消息。

`tests/test_auth.py`

```python
import pytest
from flask import g, session
from flaskr.db import get_db


def test_register(client, app):
    assert client.get('/auth/register').status_code == 200
    response = client.post(
        '/auth/register', data={'username': 'a', 'password': 'a'}
    )
    assert 'http://localhost/auth/login' == response.headers['Location']

    with app.app_context():
        assert get_db().execute(
            "select * from user where username = 'a'",
        ).fetchone() is not None


@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('', '', b'Username is required.'),
    ('a', '', b'Password is required.'),
    ('test', 'test', b'already registered'),
))
def test_register_validate_input(client, username, password, message):
    response = client.post(
        '/auth/register',
        data={'username': username, 'password': password}
    )
    assert message in response.data
```

client.get（）发出GET请求并返回Flask返回的Response对象。类似地，client.post（）发出POST请求，将数据字典转换为表单数据。

要测试页面呈现成功，会发出一个简单的请求并检查200 OK status_code。如果渲染失败，Flask将返回500内部服务器错误代码。

当注册视图重定向到登录视图时，[`headers`](http://flask.pocoo.org/docs/1.0/api/#flask.Response.headers) 将具有带有登录URL的`Location` header。

[`data`](http://flask.pocoo.org/docs/1.0/api/#flask.Response.data)包含响应的主体作为字节。如果您希望在页面上呈现某个值，请检查它是否在数据中。必须将字节与字节进行比较。如果要比较Unicode文本，请改用get_data（as_text = True）。

 pytest.mark.parametrize告诉Pytest使用不同的参数运行相同的测试函数。您可以在此处使用它来测试不同的无效输入和错误消息，而无需编写相同的代码三次。

登录视图的测试与注册的测试非常相似。会话应该在登录后设置user_id，而不是测试数据库中的数据。

`tests/test_auth.py`

```python
def test_login(client, auth):
    assert client.get('/auth/login').status_code == 200
    response = auth.login()
    assert response.headers['Location'] == 'http://localhost/'

    with client:
        client.get('/')
        assert session['user_id'] == 1
        assert g.user['username'] == 'test'


@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('a', 'test', b'Incorrect username.'),
    ('test', 'a', b'Incorrect password.'),
))
def test_login_validate_input(auth, username, password, message):
    response = auth.login(username, password)
    assert message in response.data
```

在with块中使用client允许在返回响应后访问上下文变量，例如session。通常，访问请求之外的会话会引发错误。

测试注销与登录相反。会话不应包含注销后的user_id。

`tests/test_auth.py`

```python
def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert 'user_id' not in session
```

## Blog

所有博客视图都使用您之前编写的auth fixture。调用auth.login（）以及来自客户端的后续请求将作为测试用户登录。

 索引视图应显示有关随测试数据添加的帖子的信息。以作者身份登录时，应该有一个链接来编辑帖子。

您还可以在测试索引视图时测试更多的身份验证行为。当未登录时，每个页面都显示登录或注册的链接。登录时，有一个链接可以注销。

`tests/test_blog.py`

```python
import pytest
from flaskr.db import get_db


def test_index(client, auth):
    response = client.get('/')
    assert b"Log In" in response.data
    assert b"Register" in response.data

    auth.login()
    response = client.get('/')
    assert b'Log Out' in response.data
    assert b'test title' in response.data
    assert b'by test on 2018-01-01' in response.data
    assert b'test\nbody' in response.data
    assert b'href="/1/update"' in response.data
```

​     用户必须登录才能访问创建，更新和删除视图。登录用户必须是要访问更新和删除的帖子的作者，否则返回403 Forbidden状态。如果不存在具有给定ID的帖子，则更新和删除应返回404 Not Found。

`tests/test_blog.py`

```python
@pytest.mark.parametrize('path', (
    '/create',
    '/1/update',
    '/1/delete',
))
def test_login_required(client, path):
    response = client.post(path)
    assert response.headers['Location'] == 'http://localhost/auth/login'


def test_author_required(app, client, auth):
    # change the post author to another user
    with app.app_context():
        db = get_db()
        db.execute('UPDATE post SET author_id = 2 WHERE id = 1')
        db.commit()

    auth.login()
    # current user can't modify other user's post
    assert client.post('/1/update').status_code == 403
    assert client.post('/1/delete').status_code == 403
    # current user doesn't see edit link
    assert b'href="/1/update"' not in client.get('/').data


@pytest.mark.parametrize('path', (
    '/2/update',
    '/2/delete',
))
def test_exists_required(client, auth, path):
    auth.login()
    assert client.post(path).status_code == 404
```

创建和更新视图应呈现并返回GET请求的200 OK状态。在POST请求中发送有效数据时，create应将新的post数据插入数据库，update应修改现有数据。两个页面都应显示无效数据的错误消息。

`tests/test_blog.py`

```
def test_create(client, auth, app):
    auth.login()
    assert client.get('/create').status_code == 200
    client.post('/create', data={'title': 'created', 'body': ''})

    with app.app_context():
        db = get_db()
        count = db.execute('SELECT COUNT(id) FROM post').fetchone()[0]
        assert count == 2


def test_update(client, auth, app):
    auth.login()
    assert client.get('/1/update').status_code == 200
    client.post('/1/update', data={'title': 'updated', 'body': ''})

    with app.app_context():
        db = get_db()
        post = db.execute('SELECT * FROM post WHERE id = 1').fetchone()
        assert post['title'] == 'updated'


@pytest.mark.parametrize('path', (
    '/create',
    '/1/update',
))
def test_create_update_validate(client, auth, path):
    auth.login()
    response = client.post(path, data={'title': '', 'body': ''})
    assert b'Title is required.' in response.data
```

DELETE视图应该重定向到索引url，而post应该不再存在于数据库中。

`tests/test_blog.py`

```
def test_delete(client, auth, app):
    auth.login()
    response = client.post('/1/delete')
    assert response.headers['Location'] == 'http://localhost/'

    with app.app_context():
        db = get_db()
        post = db.execute('SELECT * FROM post WHERE id = 1').fetchone()
        assert post is None
```

## Running the Tests

​     可以将一些额外的配置添加到项目的setup.cfg文件中，这些配置不是必需的，但可以使运行测试的覆盖范围更加冗长。

`setup.cfg`

```
[tool:pytest]
testpaths = tests

[coverage:run]
branch = True
source =
    flaskr
```

To run the tests, use the `pytest` command. It will find and run all the test functions you’ve written.

```
pytest

========================= test session starts ==========================
platform linux -- Python 3.6.4, pytest-3.5.0, py-1.5.3, pluggy-0.6.0
rootdir: /home/user/Projects/flask-tutorial, inifile: setup.cfg
collected 23 items

tests/test_auth.py ........                                      [ 34%]
tests/test_blog.py ............                                  [ 86%]
tests/test_db.py ..                                              [ 95%]
tests/test_factory.py ..                                         [100%]

====================== 24 passed in 0.64 seconds =======================
```

如果任何测试失败，pytest将显示引发的错误。您可以运行pytest -v来获取每个测试函数的列表而不是点。

要度量测试的代码覆盖率，请使用Coverage命令来运行pytest，而不是直接运行它。

```
coverage run -m pytest
```

You can either view a simple coverage report in the terminal:

```
coverage report

Name                 Stmts   Miss Branch BrPart  Cover
------------------------------------------------------
flaskr/__init__.py      21      0      2      0   100%
flaskr/auth.py          54      0     22      0   100%
flaskr/blog.py          54      0     16      0   100%
flaskr/db.py            24      0      4      0   100%
------------------------------------------------------
TOTAL                  153      0     44      0   100%
```

html报告允许您查看每个文件中包含了哪些行：

```
coverage html
```

这将在htmlcov目录中生成文件。在浏览器中打开htmlcov/index.html以查看报告。



# Deploy to Production

本教程的这一部分假定您有一个要部署应用程序的服务器。它概述了如何创建分发文件并进行安装，但不会详细介绍要使用的服务器或软件。您可以在开发计算机上设置新环境以尝试以下说明，但可能不应将其用于托管真实的公共应用程序。有关托管应用程序的许多不同方法的列表，请参阅部署选项。 

 See [Deployment Options](http://flask.pocoo.org/docs/1.0/deploying/) for a list of many different ways to host your application.

## Build and Install

 如果要在其他位置部署应用程序，可以构建分发文件。 Python发行版的当前标准是*wheel* 格式，扩展名为.whl。确保首先安装了轮库：

```
pip install wheel
```

使用Python运行setup.py为您提供了一个命令行工具来发出与构建相关的命令。 bdist_wheel命令将构建一个a wheel 分配文件。

```
python setup.py bdist_wheel
```

You can find the file in `dist/flaskr-1.0.0-py3-none-any.whl`. 文件名是项目的名称、版本和一些关于文件可以安装的标签。

Copy this file to another machine, [set up a new virtualenv](http://flask.pocoo.org/docs/1.0/installation/#install-create-env), then install the file with `pip`.

```
pip install flaskr-1.0.0-py3-none-any.whl
```

Pip will install your project along with its dependencies.

Since this is a different machine, you need to run `init-db` again to create the database in the instance folder.

```
export FLASK_APP=flaskr
flask init-db
```

当flask检测到它已安装(不是在可编辑模式下)时，它会为实例文件夹使用不同的目录。You can find it at`venv/var/flaskr-instance` instead.

## Configure the Secret Key

In the beginning of the tutorial that you gave a default value for [`SECRET_KEY`](http://flask.pocoo.org/docs/1.0/config/#SECRET_KEY). This should be changed to some random bytes in production. Otherwise, attackers could use the public `'dev'` key to modify the session cookie, or anything else that uses the secret key.

You can use the following command to output a random secret key:

```
python -c 'import os; print(os.urandom(16))'

b'_5#y2L"F4Q8z\n\xec]/'
```

Create the `config.py` file in the instance folder, which the factory will read from if it exists. Copy the generated value into it.

`venv/var/flaskr-instance/config.py`

```
SECRET_KEY = b'_5#y2L"F4Q8z\n\xec]/'
```

You can also set any other necessary configuration here, although `SECRET_KEY` is the only one needed for Flaskr.

## Run with a Production Server

在公开运行而不是在开发中运行时，不应该使用内置的开发服务器(flask run)。开发服务器是由werkzeug为方便而提供的，但并不是为了特别高效、稳定或安全而设计的。

Instead, use a production WSGI server. For example, to use [Waitress](https://docs.pylonsproject.org/projects/waitress/), first install it in the virtual environment:

```
pip install waitress
```

您需要告诉服务员您的应用程序，但它不像`flask run`那样使用FLASK_APP。您需要告诉它导入并调用应用程序

```
waitress-serve --call 'flaskr:create_app'

Serving on http://0.0.0.0:8080
```

有关托管应用程序的许多不同方法的列表，请参见部署选项。waitress只是一个例子，因为它同时支持windows和Linux。您可以为项目选择更多的WSGI服务器和部署选项。

Continue to [Keep Developing!](http://flask.pocoo.org/docs/1.0/tutorial/next/).



# Keep Developing!

You’ve learned about quite a few Flask and Python concepts throughout the tutorial. Go back and review the tutorial and compare your code with the steps you took to get there. Compare your project to the [example project](https://github.com/pallets/flask/tree/1.0.2/examples/tutorial), which might look a bit different due to the step-by-step nature of the tutorial.

There’s a lot more to Flask than what you’ve seen so far. Even so, you’re now equipped to start developing your own web applications. Check out the [Quickstart](http://flask.pocoo.org/docs/1.0/quickstart/#quickstart) for an overview of what Flask can do, then dive into the docs to keep learning. Flask uses [Jinja](https://palletsprojects.com/p/jinja/), [Click](https://palletsprojects.com/p/click/), [Werkzeug](https://palletsprojects.com/p/werkzeug/), and [ItsDangerous](https://palletsprojects.com/p/itsdangerous/) behind the scenes, and they all have their own documentation too. You’ll also be interested in [Extensions](http://flask.pocoo.org/docs/1.0/extensions/#extensions) which make tasks like working with the database or validating form data easier and more powerful.

If you want to keep developing your Flaskr project, here are some ideas for what to try next:

- A detail view to show a single post. Click a post’s title to go to its page.
- Like / unlike a post.
- Comments.
- Tags. Clicking a tag shows all the posts with that tag.
- A search box that filters the index page by name.
- Paged display. Only show 5 posts per page.
- Upload an image to go along with a post.
- Format posts using Markdown.
- An RSS feed of new posts.

Have fun and make awesome applications!