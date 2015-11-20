import logging
from scrapy import signals
from scrapy.exceptions import NotConfigured

import smtplib
import sqlite3 as lite

from config import *

logger = logging.getLogger(__name__)

class SendEmail(object):

    def __init__(self):
        self.fromaddr = FROMADDR
        self.toaddr  = TOADDR

    @classmethod
    def from_crawler(cls, crawler):
        # first check if the extension should be enabled and raise
        # NotConfigured otherwise
        if not crawler.settings.getbool('MYEXT_ENABLED'):
            raise NotConfigured

        # instantiate the extension object
        ext = cls()

        # connect the extension object to signals
        crawler.signals.connect(ext.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(ext.spider_closed, signal=signals.spider_closed)

        # return the extension object
        return ext


    def spider_opened(self, spider):
        logger.info("opened spider %s", spider.name)

    def spider_closed(self, spider):
        logger.info("closed spider %s", spider.name)

        # Getting films with a rating above a threshold
        topfilms_overview = ""
        con = lite.connect('topfilms.db')
        cur = con.execute("SELECT title, channel, start_ts, film_date_long, plot, genre, release_date, rating, tmdb_link, nb_votes "
                          "FROM topfilms "
                          "WHERE rating >= 6.5 "
                          "ORDER BY film_date_short, start_ts")

        data=cur.fetchall()

        if len(data) > 0:  # Check if we have records in the query result
            for row in data:
                title = row[0].encode('ascii', 'ignore')
                channel = row[1]
                start_ts = row[2]
                film_date_long = row[3]
                plot = row[4].encode('ascii', 'ignore')
                genre = row[5]
                release_date = row[6].rstrip()
                rating = row[7]
                tmdb_link = row[8]
                nb_votes = row[9]
                topfilm = ' - '.join([title, channel, film_date_long, start_ts])
                topfilm = topfilm + "\r\n" + "Release date: " + release_date
                topfilm = topfilm + "\r\n" + "Genre: " + str(genre)
                topfilm = topfilm + "\r\n" + "TMDB rating: " + rating + " from " + nb_votes + " votes"
                topfilm = topfilm + "\r\n" + plot
                topfilm = topfilm + "\r\n" + "More info on: " + tmdb_link
                topfilms_overview = "\r\n\r\n".join([topfilms_overview, topfilm])

        con.close()

        if len(topfilms_overview) > 0:
            message = topfilms_overview
        else:
            message = "There are no top rated films for the coming week."

        msg = "\r\n".join([
          "From: " + self.fromaddr,
          "To: " + self.toaddr,
          "Subject: Top Films Overview",
          message
          ])
        username = UNAME
        password = PW
        server = smtplib.SMTP(GMAIL)
        server.ehlo()
        server.starttls()
        server.login(username,password)
        server.sendmail(self.fromaddr, self.toaddr, msg)
        server.quit()
