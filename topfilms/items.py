import scrapy

class TVGuideItem(scrapy.Item):
    title = scrapy.Field()
    channel = scrapy.Field()
    start_ts = scrapy.Field()

    genre = scrapy.Field()
    plot = scrapy.Field()
    rating = scrapy.Field()
    release_date = scrapy.Field()