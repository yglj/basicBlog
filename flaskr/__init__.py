
from flask import Flask
import os


def create_app(test_config=None):
    # 创建实例
    # print('__name__:', __name__)
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(SECRET_KEY='abc',
                            DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'))
    # 从instance目录下找配置
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    # 确保实例目录存在
    try:
        # print('instance.app:', app.instance_path)
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/hello/')  # 在这里，路径后必须要写反斜杠，404 error
    def hello():
        return "hello world!"

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    print(app.url_map)

    return app

#
# if __name__ == '__main__':
#     app = create_app()
#     app.run()
