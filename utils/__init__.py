import configparser
import os

conf_ = os.getcwd() + "/config.conf"
cf = configparser.ConfigParser()
cf.read(conf_, encoding="utf-8-sig")