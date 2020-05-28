import pymysql

class Database(object):
    def __init__(self):
        self.db = pymysql.connect(host='localhost',
                                  user='root',
                                  password='password',
                                  db='??????????',
                                  charset='utf8')
        self.cursor = self.db.cursor(pymysql.cursors.DictCursor)
        self.valid = True

    def execute(self, query, args={}):
        self.cursor.execute(query, args)

    def executeOne(self, query, args={}):
        self.cursor.execute(query, args)
        row = self.cursor.fetchone()
        return row

    def executeAll(self, query, args={}):
        self.cursor.execute(query, args)
        row = self.cursor.fetchall()
        return row

    def commit(self):
        self.db.commit()