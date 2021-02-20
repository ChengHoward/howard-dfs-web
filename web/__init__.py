import json
import os
from functools import wraps
from flask import session,render_template
from utils.boxManager import BoxManager
bm = BoxManager()

def user_page(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        temp = session.get("user_login")
        if not temp:
            return render_template("manage/login.html")
        return func(*args, **kwargs)

    return decorator
def user_data(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        temp = session.get("user_login")
        if not temp:
            return str(json.dumps({
                "status": False,
                "msg": "登录已失效，请刷新页面"
            }, check_circular=False, ensure_ascii=False))
        return func(*args, **kwargs)

    return decorator

def dir_is_not_null(path):
    try:
        return os.path.exists(path) and os.path.isdir(path) and not len(os.listdir(path)) ==0
    except:
        return False