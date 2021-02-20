
import cx_Oracle

from timing.log_setting import logging


class OrcUtils():
    def __init__(self, ORL):
        self.orl = ORL

    def execute_chone(self, sql):
        self.conn = cx_Oracle.connect(self.orl)
        try:
            self.cursor = self.conn.cursor()
            self.cursor.execute(sql)
            return self.cursor.fetchone()
        except:
            self.cursor.rollback()
        finally:
            self.cursor.close()

    def execute(self, sql):
        self.conn = cx_Oracle.connect(self.orl)
        logging.info(sql.replace("\n", ""))
        try:
            self.cursor = self.conn.cursor()
            self.cursor.execute(sql)
            result = self.cursor.fetchall()

            for _ in result:
                logging.info("返回数据 : " + str(_))
            return result
        except BaseException as base:
            self.conn.rollback()
            logging.error("SQL Execution failed!")
            logging.error(base)
            return ()
        finally:
            try:
                self.cursor.close()
                self.conn.close()
            except:
                pass

    def update(self, sql):
        self.conn = cx_Oracle.connect(self.orl)
        sql = sql.replace("\u2022", "·")
        logging.info(sql.replace("\n", ""))
        try:
            self.cursor = self.conn.cursor()
            result = self.cursor.execute(sql)
            self.conn.commit()
            logging.info("返回数据 : " + str(result))
            # self.cursor.close()
            return result
        except BaseException as base:
            self.conn.rollback()
            logging.error("SQL Execution failed!")
            logging.error(base)
            return 0
        finally:
            try:
                self.cursor.close()
                self.conn.close()
            except:
                pass
