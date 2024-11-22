# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class DatasetItem(scrapy.Item):
    name = scrapy.Field()
    updated = scrapy.Field()
    views = scrapy.Field()
    api_url = scrapy.Field()
    url = scrapy.Field()
    category = scrapy.Field()
    id = scrapy.Field()
    description = scrapy.Field()
    data_type = scrapy.Field()
    file_download = scrapy.Field()
    rows = scrapy.Field()

