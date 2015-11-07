import logging
from scrapy import signals
from scrapy.exceptions import NotConfigured

import smtplib
import sqlite3 as lite

logger = logging.getLogger(__name__)

class SendEmail(object):

    def __init__(self):
        self.fromaddr = 'bert.carremans@gmail.com'
        self.toaddr  = 'bert.carremans@gmail.com'

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
        cur = con.execute("SELECT title, channel, start_ts, plot, genre, release_date, rating FROM topfilms WHERE rating >= 6")
        for row in cur:
            title = row[0]
            channel = row[1]
            start_ts = row[2]
            plot = row[3].encode('ascii', 'ignore')
            genre = row[4]
            release_date = row[5].rstrip()[-4:]
            rating = row[6]
            topfilm = ' - '.join([title, channel, start_ts, release_date, rating, genre])
            topfilm = topfilm + "\r\n" + plot
            topfilms_overview = "\r\n\r\n".join([topfilms_overview, topfilm])
        con.close()

        msg = "\r\n".join([
          "From: " + self.fromaddr,
          "To: " + self.toaddr,
          "Subject: Top Films Overview",
          topfilms_overview
          ])
        username = 'bert.carremans'
        password = 'avbgptnzwikwjkws'
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.ehlo()
        server.starttls()
        server.login(username,password)
        server.sendmail(self.fromaddr, self.toaddr, msg)
        server.quit()
