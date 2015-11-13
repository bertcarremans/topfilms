import scrapy

class TVGuideItem(scrapy.Item):
    title = scrapy.Field()
    channel = scrapy.Field()
    start_ts = scrapy.Field()
    film_day_long = scrapy.Field()
    film_day_short = scrapy.Field()
    genre = scrapy.Field()
    plot = scrapy.Field()
    rating = scrapy.Field()
    trailer = scrapy.Field()
    release_date = scrapy.Field()