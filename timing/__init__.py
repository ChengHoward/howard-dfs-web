
import logging as logger
from logging import handlers
logging = logger.getLogger()
logging.setLevel(logger.INFO)

logfile = __name__ + '.log'
fh = handlers.TimedRotatingFileHandler(filename="./logs/" + "all.log", when="D", backupCount=3, encoding='utf-8')
fh.setLevel(logger.INFO)

ch = logger.StreamHandler()
ch.setLevel(logger.INFO)

formatter = logger.Formatter('%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

logging.addHandler(fh)
logging.addHandler(ch)