# FurriesBotSQLdb
#
# Wrapper for MySQLdb python library.
# Originally written for Furries bots.
#
# @version 1.0.1 (2013-03-29)
# @author Daniel Salciccioli <sactage@sactage.com>, 2012
# @license Distributed under the terms of the MIT license.
import MySQLdb


class FurriesBotSQLdb(object):
    def __init__(self, db, pw, user, host, port=None):
        if port is None:
            port = 3306
        self.db = db
        self.host = host
        self.pw = pw
        self.user = user
        self.port = port
        self.conn = MySQLdb.connect(db=db, host=host, passwd=pw, user=user, port=port)
        self.cursor = self.conn.cursor()

    def exe(self, query):
        try:
            self.cursor.execute(query)
            self.conn.commit()
        except MySQLdb.OperationalError:
            # Server connection lost
            self.reconnect()
            self.exe(query)

    def reconnect(self):
        self.conn = MySQLdb.connect(db=self.db, host=self.host, passwd=self.pw, user=self.user, port=self.port)
        self.cursor = self.conn.cursor()

    def fetch(self, query, multi=True):
        self.exe(query)
        result = None
        try:
            if multi is True:
                result = []
                while 1:
                    row = self.cursor.fetchone()
                    if row is None:
                        break
                    result.append(row)
                return result
            else:
                result = self.cursor.fetchone()[0]
                return result
        except MySQLdb.MySQLError:
            raise
