# -*- coding:utf-8 -*-
import os

from flask import Flask, render_template

from timing import logging
from web.gateway import gateway
from web.manager import manager
from web.file_box import file_box

app = Flask(__name__)
# Logger("flask.log",logger=logging.default_handler,level='debug')
# format_str = logging.Formatter('%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s')
# default_handler = handlers.TimedRotatingFileHandler(filename="./logs/" + "flask.log", when="D", backupCount=3,
#                                                     encoding='utf-8')
app.register_blueprint(file_box, url_prefix="/file_box")
app.register_blueprint(manager, url_prefix="/manager")
app.register_blueprint(gateway, url_prefix="/gateway")
app.config['SECRET_KEY'] = "123456"
os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'


@app.route('/')
def index():
    return render_template("index.html")


# 自定义错误页面
@app.errorhandler(404)
def page_not_found(e):
    return render_template("error-404.html")


# 自定义错误页面
@app.errorhandler(500)
def server_error(e):
    return render_template("error-500.html")


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001)
