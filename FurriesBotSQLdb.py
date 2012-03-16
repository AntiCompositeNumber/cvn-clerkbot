# Wrapper for MySQLdb python library (originally written for Furries bots)
# 
# (C) Daniel Salciccioli <sactage@sactage.com>, 2012
#
# Distributed under the terms of the MIT license.
import MySQLdb #REQUIRES
class FurriesBotSQLdb(object):
	def __init__(self, db, pw, user, host, port=None):
		if port == None: port = 3306
		self.conn = MySQLdb.connect(db=db, host=host, passwd=pw, user=user, port=port)
		self.cursor = self.conn.cursor()
	def exe(self, query):
		self.cursor.execute(query)
	def fetch(self, query, multi=True):
		self.exe(query)
		result = None
		try:
			if multi == True:
				result = []
				while 1:
					row = self.cursor.fetchone()
					if row == None:
						break
					result.append(row)
				return result
			else:
				result = self.cursor.fetchone()[0]
				return result
		except MySQLError:
			raise MySQLError
