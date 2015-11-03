import sqlite3 as lite

con = None  # db connection

class StoreInDBPipeline(object):

	def __init__(self):
		self.setupDBCon()
		self.dropTopFilmsTable()
		self.createTopFilmsTable()



	def process_item(self, item, spider):
		self.storeInDb(item)
		return item


	def storeInDb(self, item):
		self.cur.execute("INSERT INTO topfilms(\
			title, \
			channel, \
			start_ts, \
			rating \
			) \
		VALUES( ?, ?, ?, ? )",
		(
			item['title'],
            item['channel'],
            item['start_ts'],
			float(item['rating'])
		))
		self.con.commit()


	def setupDBCon(self):
		self.con = lite.connect('topfilms.db')
		self.cur = self.con.cursor()


	def __del__(self):
		self.closeDB()


	def createTopFilmsTable(self):
		self.cur.execute("CREATE TABLE IF NOT EXISTS topfilms(id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, \
			title TEXT, \
            channel TEXT, \
            start_ts TEXT, \
			rating TEXT \
			)")


	def dropTopFilmsTable(self):
		self.cur.execute("DROP TABLE IF EXISTS topfilms")

	def closeDB(self):
		self.con.close()