import sqlite3


class SqliteDB():
    def __init__(self,db_path):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    def query(self,_sql):
        try:
            self.cursor.execute(_sql)
            return self.cursor.fetchall()
        except BaseException as base:
            print(base)
            return ()
        finally:
            pass

    def execute(self,_sql)   :
        try:
            c = self.cursor.execute(_sql)
            return self.conn.total_changes
        except BaseException as base:
            print(base)
            self.conn.rollback()
        finally:
            self.conn.commit()


    def executeObj(self,_sql,_obj):
        try:
            c = self.cursor.executemany(_sql,_obj)
            return self.conn.total_changes
        except BaseException as base:
            print(base)
            self.conn.rollback()
        finally:
            self.conn.commit()

