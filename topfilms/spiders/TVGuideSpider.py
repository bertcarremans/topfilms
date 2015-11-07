import scrapy
import unidecode
import urllib

from fuzzywuzzy import fuzz

from topfilms.items import TVGuideItem

class TVGuideSpider(scrapy.Spider):
    name = "tvguide"
    allowed_domains = ["nieuwsblad.be", "themoviedb.org"]
    start_urls = [
        "http://www.nieuwsblad.be/tv-gids/vandaag/film/",
        #"http://www.nieuwsblad.be/tv-gids/morgen/film",
        #"http://www.nieuwsblad.be/tv-gids/overmorgen/film"

    ]


    def parse(self, response):
        for col_inner in response.xpath('//div[@class="grid__col__inner"]'):
            chnl = col_inner.xpath('.//div[@class="tv-guide__channel"]/h6/a/text()').extract_first()

            if chnl in ['EEN', 'CANVAS', 'VTM', '2BE', 'VITAYA', 'VIER', 'VIJF', 'NPO1', 'NPO2', 'NPO3']:
                for program in col_inner.xpath('.//div[@class="program"]'):
                    item = TVGuideItem()
                    item['channel'] = chnl
                    title = program.xpath('.//div[@class="title"]/a/text()').extract_first()
                    title = unidecode.unidecode(title)  # Replace special characters with characters without accents, ...

                    title = title.replace('.', '')
                    title = urllib.quote_plus(title)  # Create valid url parameter
                    item['title'] = program.xpath('.//div[@class="title"]/a/text()').extract_first()
                    item['start_ts'] = program.xpath('.//div[@class="time"]/text()').extract_first()

                    #print item
                    print "******* https://www.themoviedb.org/search?query="+title

                    # Extract information from the Movie Database www.themoviedb.org
                    request = scrapy.Request("https://www.themoviedb.org/search?query="+title,callback=self.parse_tmdb)
                    request.meta['item'] = item  # Pass the item with the request to the detail page

                    yield request


    def parse_tmdb(self, response):
        item = response.meta['item']  # Use the passed item

        tmdb_title = response.xpath('//a[@class="title result"][1]/text()').extract_first()
        match_ratio = fuzz.ratio(item['title'], tmdb_title)

        if match_ratio > 90:
            item['genre'] = response.xpath('.//span[@class="genres"][1]/text()').extract_first()
            item['plot'] = response.xpath('.//p[@class="overview"][1]/text()').extract_first()
            item['rating'] = response.xpath('//span[@class="vote_average"][1]/text()').extract_first()
            item['release_date'] = response.xpath('.//span[@class="release_date"][1]/text()').extract_first()
            yield item
        else:
            return





