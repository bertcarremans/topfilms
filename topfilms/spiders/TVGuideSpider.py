import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from fuzzywuzzy import fuzz
from ..config import *
from topfilms.items import TVGuideItem

class TVGuideSpider(CrawlSpider):
    name = "tvguide"
    allowed_domains = [DOM_1, DOM_2]
    start_urls = [START_URL]

    # Extract the links from the navigation per day
    # We will not crawl the films for yesterday
    rules = (
        Rule(LinkExtractor(allow=(), deny=(r'\/gisteren'), restrict_xpaths=('//a[@class="button button--beta"]',)), callback="parse_by_day", follow= True),
    )

    def parse_by_day(self, response):

        film_date_long = response.xpath('//div[@class="grid__col__inner"]/p/text()').extract_first()
        film_date_long = film_date_long.rsplit(',',1)[-1].strip()  # Remove day name and white spaces

        # Create a film date with a short format like YYYYMMDD to sort the results chronologically
        film_day_parts = film_date_long.split()

        months_list = ['januari', 'februari', 'maart',
                  'april', 'mei', 'juni', 'juli',
                  'augustus', 'september', 'oktober',
                  'november', 'december' ]

        year = str(film_day_parts[2])
        month = str(months_list.index(film_day_parts[1]) + 1).zfill(2)
        day = str(film_day_parts[0]).zfill(2)

        film_date_short = year + month + day



        for col_inner in response.xpath('//div[@class="grid__col__inner"]'):
            chnl = col_inner.xpath('.//div[@class="tv-guide__channel"]/h6/a/text()').extract_first()

            if chnl in ALLOWED_CHANNELS:
                for program in col_inner.xpath('.//div[@class="program"]'):
                    item = TVGuideItem()
                    item['channel'] = chnl
                    item['title'] = program.xpath('.//div[@class="title"]/a/text()').extract_first()
                    item['start_ts'] = program.xpath('.//div[@class="time"]/text()').extract_first()
                    item['film_date_long'] = film_date_long
                    item['film_date_short'] = film_date_short

                    detail_link = program.xpath('.//div[@class="title"]/a/@href').extract_first()
                    url_part = detail_link.rsplit('/',1)[-1]

                    # Extract information from the Movie Database www.themoviedb.org
                    request = scrapy.Request("https://www.themoviedb.org/search?query="+url_part,callback=self.parse_tmdb)
                    request.meta['item'] = item  # Pass the item with the request to the detail page

                    yield request



    def parse_tmdb(self, response):
        item = response.meta['item']  # Use the passed item

        tmdb_titles = response.xpath('//a[@class="title result"]/text()').extract()

        if tmdb_titles:  # Check if there are results on TMDB
            for tmdb_title in tmdb_titles:
                match_ratio = fuzz.ratio(item['title'], tmdb_title)
                if match_ratio > 90:
                    item['genre'] = response.xpath('.//span[@class="genres"]/text()').extract_first()
                    item['rating'] = response.xpath('//span[@class="vote_average"]/text()').extract_first()
                    release_date = response.xpath('.//span[@class="release_date"]/text()').extract_first()
                    release_date_parts = release_date.split('/')
                    item['release_date'] = "/".join([release_date_parts[1].strip(), release_date_parts[0].strip(), release_date_parts[2].strip()])
                    tmdb_link = "https://www.themoviedb.org" + response.xpath('//a[@class="title result"]/@href').extract_first()
                    item['tmdb_link'] = tmdb_link

                    # Extract more info from the detail page
                    request = scrapy.Request(tmdb_link,callback=self.parse_tmdb_detail)
                    request.meta['item'] = item  # Pass the item with the request to the detail page

                    yield request
                    break  # We only consider the first match
                else:
                    return


    def parse_tmdb_detail(self, response):
        item = response.meta['item']  # Use the passed item

        item['nb_votes'] = response.xpath('//span[@itemprop="ratingCount"]/text()').extract_first()
        item['plot'] = response.xpath('.//p[@id="overview"]/text()').extract_first()

        yield item