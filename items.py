# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ContentItem(scrapy.Item):
    # define the fields for your item here like:
    url = scrapy.Field()
    title = scrapy.Field()
    author = scrapy.Field()
    publish_company = scrapy.Field()
    publish_date = scrapy.Field()
    content = scrapy.Field()
    img_urls = scrapy.Field()
