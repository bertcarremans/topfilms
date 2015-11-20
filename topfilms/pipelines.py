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
		film_date_long, \
		film_date_short, \
		rating, \
		genre, \
		plot, \
		tmdb_link, \
		release_date, \
		nb_votes \
		) \
		VALUES( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ? )",
		(
		item['title'],
		item['channel'],
		item['start_ts'],
		item['film_date_long'],
		item['film_date_short'],
		float(item['rating']),
		item['genre'],
		item['plot'],
		item['tmdb_link'],
		item['release_date'],
		item['nb_votes']
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
		film_date_long TEXT, \
		film_date_short TEXT, \
		rating TEXT, \
		genre TEXT, \
		plot TEXT, \
		tmdb_link TEXT, \
		release_date TEXT, \
		nb_votes \
		)")


	def dropTopFilmsTable(self):
		self.cur.execute("DROP TABLE IF EXISTS topfilms")

	def closeDB(self):
		self.con.close()