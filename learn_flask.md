###A  Minimal  Application

1.创建一个flask应用实例

`app =Flask(__name__)`   参数：`__name__` 模块或包的名字

2.视图函数

```python
@app.rout('/')
def view():
	pass
```

3.设置环境变量并运行

linux：export  FLASK_APP=xx.py

window：set FLASK_APP=xx.py

flask run/ python -m flask run

可选参数：--host --port



###Debug Mode

设置flask运行环境变量为开发模式

set FLASK_ENV= development

他会做以下几件事：

+ 激活调试
+ 自动重载
+ 在Flask应用中启用调试模式

注意：这样做会造成安全风险，所以一定不要在生产机器上使用



### Routing

现代web应用使用有含义的URL来帮助用户记住网页地址。

使用`route()` 装饰器为一个函数绑定URL

> You can make parts of the URL dynamic and attach multiple rules to a function.

```python
from werkzeug.routing import BaseConverter
class RegexRule(BaseConverter):
    def __init__(self, url_map, *args):
        super(RegexRule, self).__init__(url_map)
        self.regex = args[0]

app.url_map.converters['match'] = RegexRule

@app.route('/user/<name>')  
def show_user_profile(name):
	return 'User %s' % name

@app.route('/match/<int:id>')
def match(id):
    return '请求中的参数id：%s' % id

@app.route('/rule/<match("[a-z]{3}"):id>')
def rule(id):
    return '根据自定义匹配规则匹配结果：%s' % id
```

####variable Rules

`<variable_name>` 接收一个关键字参数，也可以使用converter传递一个特定类型的参`<converter:variable_name>`

Converter types:

| `string` | (default) accepts any text without a slash |
| -------- | ------------------------------------------ |
| `int`    | accepts positive integers                  |
| `float`  | accepts positive floating point values     |
| `path`   | like `string` but also accepts slashes     |
| `uuid`   | accepts UUID strings                       |

####Unique URLs / Redirection Behavior

```python
@app.route('/projects/')
def projects():
    return 'The project page'

@app.route('/about')
def about():
    return 'The about page'
```

projects端点(endporint)的规范URL具有尾部斜杠。 它类似于文件系统中的文件夹。 如果您访问的URL没有尾部斜杠，Flask会将您重定向到带有斜杠的规范URL。

about 端点的规范URL没有尾部斜杠。 它类似于文件的路径名。 使用尾部斜杠访问URL会产生404“未找到”错误。 这有助于保持URL对这些资源的唯一性，这有助于搜索引擎避免两次索引同一页面。

#### URL Building

使用`url_for()`构建URL，它获取一个视图函数名作为第一个参数以及任意的关键字参数，所有参数拼成

一个URL，不可知的变量部分添加到URL查询参数

为什么使用URL反转函数？

+ 比固定地址更容易描述
+ 改变路径时不需要去改变固定地址
+ 更好的处理转义和Unicode编码字符
+ 总是生成绝对路径，避免相对路径在浏览器出错
+ 如果你的应用程序位于URL根目录之外

```python
with app.test_request_context():    # 测试请求上下文
    print(url_for('index'))
    print(url_for('see_route', next='/center'))
    print(url_for('login', user='John DD'))
    
'''
/
/see?next=%2Fcenter
/login/John%20DD
'''
```

#### HTTP Methods

在route装饰器中使用methods参数，来处理不同请求方式

```python
from flask import request

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return do_the_login()  # 返回登录处理函数的调用
    else:
        return show_the_login_form()  # 返回登录表单
```



###Static Files

在包或模块下新建一个static文件夹，它将会以`/static`的方式在应用中实现

为静态文件生成URLs，使用特别的`static`端点名

```python
url_for('static', filename='style.css')
```


###Rending Templates

Flask 自带Jinja2模板引擎

渲染模板使用`render_template()`方法，需要提供模板名和传给模板引擎的关键字参数

```python
@app.route('/login2', methods=['GET', 'POST'])
def login2():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print('user:{} | password:{}'.format(username, password))
    return render_template('login2.html', method=request.method)
```

Flask会在你的templates目录下找模板文件，如果你的应用是一个模块，这个文件夹在模块同级目录，如果是个包，它实际上在包里面的目录下

在模板里还可以使用[request，session](), **g对象**，还有**get_flashed_message()**函数

使用[模板继承]()会更好用，使用模板继承可能保持页面确定的要素（如头部，尾部）

自动转义默认开启，如果模板变量包含HTML它会自动转义。

使用Markup类，或者在模板中使用|safe过滤器，确保sefe HTML

```python
>>> from flask import Markup
>>> Markup('<strong>Hello %s!</strong>') % '<blink>hacker</blink>'
Markup(u'<strong>Hello &lt;blink&gt;hacker&lt;/blink&gt;!</strong>')
>>> Markup.escape('<blink>hacker</blink>')
Markup(u'&lt;blink&gt;hacker&lt;/blink&gt;')
>>> Markup('<em>Marked up</em> &raquo; HTML').striptags()
u'Marked up \xbb HTML'
```



###Accessing Request Data

#### Context Locals

全局request对象得到客户端发给服务器的数据，Flask使用context locals 来确保它的全局性和线程安全。

Certain objects in Flask are global objects,  These objects are actually proxies to objects that are local to a specific context. 

Imagine the context being the handling thread. A request comes in and the web server decides to spawn a new thread (or something else, the underlying object is capable of dealing with concurrency systems other than threads). When Flask starts its internal request handling it figures out that the current thread is the active context and binds the current application and the WSGI environments to that context (thread). It does that in an intelligent way so that one application can invoke another application without breaking.

So what does this mean to you? Basically you can completely ignore that this is the case unless you are doing something like unit testing. You will notice that code which depends on a request object will suddenly break because there is no request object. The solution is creating a request object yourself and binding it to the context. The easiest solution for unit testing is to use the test_request_context() context manager. In combination with the with statement it will bind a test request so that you can interact with it. 

```
from flask import request

with app.test_request_context('/hello', method='POST'):
    # now you can do something with the request until the
    # end of the with block, such as basic assertions:
    assert request.path == '/hello'
    assert request.method == 'POST'
```

The other possibility is passing a whole WSGI environment to the [`request_context()`](http://flask.pocoo.org/docs/1.0/api/#flask.Flask.request_context) method:

```
from flask import request

with app.request_context(environ):
    assert request.method == 'POST'
```

#### The Request Object

```
from flask import request
```

当前请求方法可以用 [`method`](http://flask.pocoo.org/docs/1.0/api/#flask.Request.method) 属性拿到. 拿取表单数据 (data transmitted in a `POST` or `PUT`request) 你可以使用 [`form`](http://flask.pocoo.org/docs/1.0/api/#flask.Request.form) 属性. 

```
@app.route('/login', methods=['POST', 'GET'])
def login():
    error = None
    if request.method == 'POST':
        if valid_login(request.form['username'],
                       request.form['password']):
            return log_the_user_in(request.form['username'])
        else:
            error = 'Invalid username/password'
    # the code below is executed if the request method
    # was GET or the credentials were invalid
    return render_template('login.html', error=error)
```

如果 `form` 中不存在这个关键字，会抛出  [`KeyError`](https://docs.python.org/3/library/exceptions.html#KeyError) 异常. 你可以捕获这个 [`KeyError`](https://docs.python.org/3/library/exceptions.html#KeyError) ,如果不捕获将会被 一个 HTTP 400 Bad Request error page 替代. 目前大多数情况不需要处理这个问题.

通过 URL提交参数 (`?key=value`)你能使用 [`args`](http://flask.pocoo.org/docs/1.0/api/#flask.Request.args) 属性:

```
searchword = request.args.get('key', '')
```

建议通过get或捕获keyError来获取URL参数，因为用户可能变动URL，向其展示404页面非常不友好。

#### File Uploads

在html表单确保不要忘记设置 `enctype="multipart/form-data"`属性, 否则浏览器将不会传输你的文件。

上传文件会被存储到内存或文件系统的暂存区，在你的请求对象中你可以通过`files` 属性找到这些文件。 每个文件被放在files字典中。这些文件看起来像一个 标准Python `file`object, 也有一个 [`save()`](http://werkzeug.pocoo.org/docs/datastructures/#werkzeug.datastructures.FileStorage.save) 方法允许你存储这些文件在服务器文件系统中。

```
from flask import request

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['the_file']
        f.save('/var/www/uploads/uploaded_file.txt')
    ...
```

 	如果你想知道这些文件上传到应用程序中叫什么, 通过[`filename`](http://werkzeug.pocoo.org/docs/datastructures/#werkzeug.datastructures.FileStorage.filename) 属性获取它. 然而请你想一想这些值可能被伪造，所以绝不能相信这些文件名。如果你想使用用户存储在服务器上的文件名，请通过Werkzeug为你提供的 [`secure_filename()`](http://werkzeug.pocoo.org/docs/utils/#werkzeug.utils.secure_filename) 函数。

```
from flask import request
from werkzeug.utils import secure_filename

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['the_file']
        f.save('/var/www/uploads/' + secure_filename(f.filename))
    ...
```

### Cookies

使用request对象中的cookies属性获取 [`cookies`](http://flask.pocoo.org/docs/1.0/api/#flask.Request.cookies) ，得到的是一个包含客户端传输过来的所有信息的字典，用响应对象的set_cookie方法设置cookies。如果你使用sessions，不要直接用cookies，而是使用Flask中的Sessions在cookies 头部添加安全信息。

```
from flask import request

@app.route('/')
def index():
    username = request.cookies.get('username')
    # use cookies.get(key) instead of cookies[key] to not get a
    # KeyError if the cookie is missing.
```

```python
from flask import make_response

@app.route('/')
def index():
    resp = make_response(render_template(...))
    resp.set_cookie('username', 'the username')
    return resp
```

注意在你的视图函数返回字符串时才会把cookies放入响应对象，使用make_response()创建响应对象去修改它

###Redirects and Erros

使用redirect()函数重定向到另一个端点，使用abort()提前终止请求

```python
from flask import abort, redirect, url_for

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login')
def login():
    abort(401)
    this_is_never_executed()
```

用户被重定向到一个不能访问的页面（401意味着拒绝访问），默认展示黑白错误页面，如果你想自定义错误页面，可以使用`errorhandler()`装饰器

```python
from flask import render_template

@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404   # 404在渲染函数后调用，告诉flask页面状态码，默认是200
```



### About Responses

视图函数的返回值会自动传到响应对象中，如果返回的是字符串值，就会作为响应体，另外还有一个200 ok

的状态码，text/html 的mimetype。

1. 视图函数返回合适的response对象，会直接响应
2. 如果是字符串，响应对象创建数据和参数
3. 返回元组可以提供额外参数，如 `(response,status, headers)` 或者 `(response, headers)` 在元组中至少有一项。 `status`将重写状态码， `headers` 可以是一个列表或字典会被加到请求头的尾部。
4. 如果是一个空对象，Flask将认定返回的是一个无效的 WSGI application 把他传到响应对象中.

在视图函数中拿到响应对象 使用[`make_response()`](http://flask.pocoo.org/docs/1.0/api/#flask.make_response) 函数。

```
@app.errorhandler(404)
def not_found(error):
    return render_template('error.html'), 404
```

```
@app.errorhandler(404)
def not_found(error):
    resp = make_response(render_template('error.html'), 404)
    resp.headers['X-Something'] = 'A value'
    return resp
```



### Sessions

使用Sessions需要设置秘钥

session对象允许存储特定用户信息从一个请求存储到下一个请求，基于cookie来实现，

并以加密的方式对cookie进行签名，这意味着用户可以查看cookie内容但不能修改它，除非用户

知道用于签名的秘钥

```python
from flask import Flask, session, redirect, url_for, escape, request

app = Flask(__name__)

# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

@app.route('/')
def index():
    if 'username' in session:
        return 'Logged in as %s' % escape(session['username'])
    return 'You are not logged in'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect(url_for('index'))
    return '''
        <form method="post">
            <p><input type=text name=username>
            <p><input type=submit value=Login>
        </form>
    '''

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('index'))
```

如果没有使用模板引擎，escape()帮你转义字符串

How to generate good secret keys

A secret key should be as random as possible. Your operating system has ways to generate pretty random data based on a cryptographic random generator. Use the following command to quickly generate a value for `Flask.secret_key` (or [`SECRET_KEY`](http://flask.pocoo.org/docs/1.0/config/#SECRET_KEY)):

```
$ python -c 'import os; print(os.urandom(16))'
b'_5#y2L"F4Q8z\n\xec]/'
```



### Message Flashing

To flash a message use the [`flash()`](http://flask.pocoo.org/docs/1.0/api/#flask.flash) method, to get hold of the messages you can use [`get_flashed_messages()`](http://flask.pocoo.org/docs/1.0/api/#flask.get_flashed_messages) which is also available in the templates. Check out the [Message Flashing](http://flask.pocoo.org/docs/1.0/patterns/flashing/#message-flashing-pattern) for a full example.



### Logging

Sometimes you might be in a situation where you deal with data that should be correct, but actually is not. For example you may have some client-side code that sends an HTTP request to the server but it’s obviously malformed. This might be caused by a user tampering with the data, or the client code failing. Most of the time it’s okay to reply with `400 Bad Request` in that situation, but sometimes that won’t do and the code has to continue working.

You may still want to log that something fishy happened. This is where loggers come in handy. As of Flask 0.3 a logger is preconfigured for you to use.

The attached [`logger`](http://flask.pocoo.org/docs/1.0/api/#flask.Flask.logger) is a standard logging [`Logger`](https://docs.python.org/3/library/logging.html#logging.Logger), so head over to the official [logging documentation](https://docs.python.org/library/logging.html) for more information.



### Hooking in WSGI Middlewares

If you want to add a WSGI middleware to your application you can wrap the internal WSGI application. For example if you want to use one of the middlewares from the Werkzeug package to work around bugs in lighttpd, you can do it like this:

```
from werkzeug.contrib.fixers import LighttpdCGIRootFix
app.wsgi_app = LighttpdCGIRootFix(app.wsgi_app)
```



### Using Flask Extensions[¶](http://flask.pocoo.org/docs/1.0/quickstart/#using-flask-extensions)

Extensions are packages that help you accomplish common tasks. For example, Flask-SQLAlchemy provides SQLAlchemy support that makes it simple and easy to use with Flask.

For more on Flask extensions, have a look at [Extensions](http://flask.pocoo.org/docs/1.0/extensions/#extensions).

### Deploying to a Web Server

Ready to deploy your new Flask app? Go to [Deployment Options](http://flask.pocoo.org/docs/1.0/deploying/#deployment).