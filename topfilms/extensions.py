import logging
from scrapy import signals
from scrapy.exceptions import NotConfigured

import smtplib
import sqlite3 as lite

logger = logging.getLogger(__name__)

class SendEmail(object):

    def __init__(self):
        #self.item_count = item_count
        #self.items_scraped = 0

        self.fromaddr = 'bert.carremans@gmail.com'
        self.toaddrs  = self.fromaddr

    @classmethod
    def from_crawler(cls, crawler):
        # first check if the extension should be enabled and raise
        # NotConfigured otherwise
        if not crawler.settings.getbool('MYEXT_ENABLED'):
            raise NotConfigured

        # get the number of items from settings
        #item_count = crawler.settings.getint('MYEXT_ITEMCOUNT', 1000)

        # instantiate the extension object
        ext = cls()

        # connect the extension object to signals
        crawler.signals.connect(ext.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(ext.spider_closed, signal=signals.spider_closed)
        #crawler.signals.connect(ext.item_scraped, signal=signals.item_scraped)

        # return the extension object
        return ext

    def spider_opened(self, spider):
        logger.info("opened spider %s", spider.name)

    def spider_closed(self, spider):
        logger.info("closed spider %s", spider.name)

        topfilms_overview = ""
        con = lite.connect('topfilms.db')
        cur = con.execute("SELECT title, channel, start_ts, rating FROM topfilms WHERE rating >= 6")
        for row in cur:
            topfilm = ' - '.join([row[0], row [1], row [2], row [3]])
            topfilms_overview = "\r\n".join([topfilms_overview, topfilm])
        con.close()

        #fromaddr = 'bert.carremans@gmail.com'
        #toaddrs  = 'bert.carremans@gmail.com'
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
        server.sendmail(self.fromaddr, self.toaddrs, msg)
        server.quit()
    '''
    def item_scraped(self, item, spider):
        self.items_scraped += 1
        if self.items_scraped % self.item_count == 0:
            logger.info("scraped %d items", self.items_scraped)
    '''