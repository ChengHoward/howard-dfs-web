# -*- coding:utf-8 -*-
import json, os, configparser
import uuid

from flask import Blueprint, render_template, session, request, jsonify
from empty.TaskEmpty import Task
from timing.thread_task import JobTime
from utils import cf
from web import user_page, user_data

jt = JobTime()
TaskSession = jt.TaskSession

manager = Blueprint("/manager", __name__)


@manager.route("/", methods=["GET"])
@user_page
def index():
    return render_template("manage/manage.html")


@manager.route("/hello.page", methods=["GET"])
@user_page
def hello():
    return render_template("manage/hello.html")


@manager.route("/log", methods=["GET"])
@user_page
def log_page():
    return render_template("manage/log.html")


@manager.route("/login", methods=["POST"])
def login():
    data = request.form
    user = {x[0]: x[1] for x in cf.items(section="admin")}
    print(data)
    if user.get("user") == data.get("username") and user.get("password") == data.get("password"):
        session["user_login"] = 1
        res_json = {
            "status": True,
            "msg": "登录成功"
        }
    else:
        res_json = {
            "status": False,
            "msg": "登录失败，用户名或密码错误"
        }

    return json.dumps(res_json, check_circular=False, ensure_ascii=False)


@manager.route("/task", methods=["GET"])
@user_page
def task():
    return render_template("manage/task.html")


###
#   任务控制接口
###


@manager.route("/task.json", methods=["GET", "POST"])
@user_page
def task_data():
    res_json = {
        "msg": "",
        "count": TaskSession.query(Task).count(),
        "code": 0,
        "data": [_.to_dict() for _ in TaskSession.query(Task).all()]
    }
    return str(json.dumps(res_json, check_circular=False, ensure_ascii=False))


@manager.route("/enable.json", methods=["POST"])
@user_data
def enable_json():

    data = request.form
    task_id = data.get("task_id", "")
    enable = True if data.get("enable", False) else False
    if task_id == "":
        return jsonify({"status": False, "msg": "参数错误"})
    TaskSession.query(Task).filter_by(task_id=task_id).update({'enable': enable, })
    TaskSession.commit()
    jt.initTask()
    return jsonify({"status": True, "msg": "修改成功"})


@manager.route("/addTask", methods=["GET", "POST"])
@user_data
def addTask():
    data = request.form
    content = data.get("content")
    time = data.get("time")
    label = data.get("label")
    task_id = str(uuid.uuid4())
    command = data.get("command", "")
    enable = data.get("enable") is not None
    mark = data.get("mark")
    TaskSession.add(Task(
        task_id=task_id,
        enable=enable,
        content=content,
        time=time,
        label=label,
        command=command,
        mark=mark
    ))
    TaskSession.commit()
    jt.initTask()
    return str(json.dumps({
        "status": True,
        "msg": "添加成功"
    }, check_circular=False, ensure_ascii=False))


@manager.route("/editTask", methods=["GET", "POST"])
@user_data
def editTask():
    data = request.form
    content = data.get("content")
    time = data.get("time")
    label = data.get("label")
    command = data.get("command", "")
    enable = data.get("enable") is not None
    mark = data.get("mark")
    task_id = data.get("task_id")

    TaskSession.query(Task).filter_by(task_id=task_id).update({
        "enable": enable,
        "content": content,
        "time": time,
        "label": label,
        "command": command,
        "mark": mark
    })
    TaskSession.commit()
    jt.initTask()
    return str(json.dumps({
        "status": True,
        "msg": "修改成功"
    }, check_circular=False, ensure_ascii=False))


@manager.route("/delTask", methods=["GET", "POST"])
@user_data
def delTask():
    data = request.form
    task_id = data.get("task_id")

    TaskSession.query(Task).filter_by(task_id=task_id).delete()
    TaskSession.commit()
    jt.initTask()
    return str(json.dumps({
        "status": True,
        "msg": "删除成功"
    }, check_circular=False, ensure_ascii=False))
