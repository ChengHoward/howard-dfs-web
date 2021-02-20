import datetime
import json, time, threading
import os
import re
import uuid

import schedule
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from empty import TaskBase
from empty.TaskEmpty import Task
from timing.log_setting import log as logging

logging = logging.logger
class JobTime():
    def __init__(self):
        self.weekday = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期天"]
        self.main_engine = create_engine('sqlite:///task.db?check_same_thread=False', echo=False)
        TaskBase.metadata.create_all(self.main_engine, checkfirst=True)
        self.SqlSession = sessionmaker(bind=self.main_engine)
        self.TaskSession = self.SqlSession()
        self.tasklock = "task.lock"
        self.clean_task_lock()
        self.read_config()
        self.t = threading.Thread(target=self.schedule_run)
        self.t.start()
        self.task_lock = False
        self.initTask()

    def task_status(self):
        try:
            last_time = open("time", encoding="utf-8", mode="r").read()
        except:
            last_time = ""
        return self.task_lock, last_time

    def schedule_run(self):
        while True:
            schedule.run_pending()
            time.sleep(1)

    def read_config(self):
        self.task_list = [_.to_dict() for _ in self.TaskSession.query(Task).all()]

    def at_task(self, jobs):
        logging.info("手动同步")
        self.run_daemon_thread(self.job(str(uuid.uuid4()), jobs, "手动任务"))

    def initTask(self):
        logging.info("销毁所有任务，重新启动")
        schedule.clear("all")
        self.read_config()
        for task in self.task_list:
            if task.get("enable"):
                self.run_daemon_thread(
                    self.to_thread(self.job(task.get("task_id"), task.get("command"), "定时任务"), task.get("time"),
                                   task.get("content"),
                                   task.get("label"), task.get("task_id")))

    def run_daemon_thread(self, target, *args, **kwargs):
        job_thread = threading.Thread(target=target, args=args, kwargs=kwargs)
        job_thread.setDaemon(True)
        job_thread.start()

    def clean_task_lock(self):
        # try:
        #     os.remove(self.tasklock)
        # except:
        #     pass
        self.task_lock = False

    def getdate(self,beforeOfDay):
        today = datetime.datetime.now()
        offset = datetime.timedelta(beforeOfDay)
        _d =  today + offset
        return {
            "year": str(_d.year),
            "month": str(_d.month).rjust(2, '0'),
            "day": str(_d.day).rjust(2, '0'),
            "hour": str(_d.hour).rjust(2, '0'),
            "minute": str(_d.minute).rjust(2, '0'),
            "second": str(_d.second).rjust(2, '0'),
            "weekday": str(self.weekday[_d.weekday()]),
        }

    def getDic(self,key):
        _d = datetime.datetime.now()
        _dic = {
            "year": str(_d.year),
            "month": str(_d.month).rjust(2, '0'),
            "day": str(_d.day).rjust(2, '0'),
            "hour": str(_d.hour).rjust(2, '0'),
            "minute": str(_d.minute).rjust(2, '0'),
            "second": str(_d.second).rjust(2, '0'),
            "weekday": str(self.weekday[_d.weekday()]),
            "cwd": str(os.getcwd()),
            "uuid": str(uuid.uuid4()),
            "uuid(32)": str(uuid.uuid4()).replace("-",""),
            # "${user_home}": str(os.environ['HOME']),
        }
        value = _dic.get(key,None)
        if value is None:
            try:
                key1 = key.split(":")[0]
                key2 = int(key.split(":")[1])
                value = self.getdate(key2).get(key1, None)
            except BaseException as base:
                print(base)
                value = ""
        return value



    def transform_command(self, _command) -> dict:
        cps = re.findall(r'\$\{(.*?)\}',_command)
        _dic = {}
        for _ in cps:
            _dic.update({
                "${%s}" %_:self.getDic(str(_).replace(" ",""))
            })
        for _, __ in _dic.items():
            _command = _command.replace(_, __)

        return _command

    def job(self, id, command, task_type):
        logging.info("任务 %s 创建" % str(id))

        def run():
            logging.info("开始任务")
            _command = self.transform_command(str(command))
            print(_command)
            try:
                # res = os.system(_command)
                # logging.info(str(res))
                pass
            except BaseException as base:
                logging.error(str(base))
            # print(str(res))

        return run

    def log(self):
        datas = []
        if os.path.exists("up_log"):
            with open("up_log", 'r', encoding="utf-8") as f:
                while True:
                    line = f.readline()
                    if line == "":
                        break
                    lines = line.split("|||")
                    datas.append({
                        "id": lines[0],
                        "task_name": lines[1],
                        "task_type": lines[2],
                        "update_num": lines[3],
                        "task_status": lines[4],
                        "msg": lines[5],
                        "task_time": lines[6],
                    })
        return datas

    def to_thread(self, target, t, content, label, id):
        def run():
            if content == "每隔秒":
                schedule.every(int(t)).seconds.do(target).tag("all", label, id)
            elif content == "每隔分":
                schedule.every(int(t)).minutes.do(target).tag("all", label, id)
            elif content == "每隔时":
                schedule.every(int(t)).hours.do(target).tag("all", label, id)
            elif content == "每隔天":
                schedule.every(int(t)).days.do(target).tag("all", label, id)
            elif content == "每秒":
                schedule.every().second.at(t).do(target).tag("all", label, id)
            elif content == "每分":
                schedule.every().minute.at(t).do(target).tag("all", label, id)
            elif content == "每时":
                schedule.every(t).hour.at(t).do(target).tag("all", label, id)
            elif content == "每天":
                schedule.every().day.at(t).do(target).tag("all", label, id)
            elif content == "每周一":
                schedule.every().monday.at(t).do(target).tag("all", label, id)
            elif content == "每周二":
                schedule.every().tuesday.at(t).do(target).tag("all", label, id)
            elif content == "每周三":
                schedule.every().wednesday.at(t).do(target).tag("all", label, id)
            elif content == "每周四":
                schedule.every().thursday.at(t).do(target).tag("all", label, id)
            elif content == "每周五":
                schedule.every().friday.at(t).do(target).tag("all", label, id)
            elif content == "每周六":
                schedule.every().saturday.at(t).do(target).tag("all", label, id)
            elif content == "每周日":
                schedule.every().sunday.at(t).do(target).tag("all", label, id)

        return run
