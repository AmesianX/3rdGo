# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ProjectItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    src_url = scrapy.Field()
    url = scrapy.Field()
    label = scrapy.Field()
    body = scrapy.Field()
    encoding = scrapy.Field()
