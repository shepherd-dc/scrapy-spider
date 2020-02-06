# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, Identity, MapCompose, Join

from ArticleSpider.utils.common import date_convert


class ArticleSpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    create_date = scrapy.Field(
        input_processor=MapCompose(date_convert)
    )
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    front_image_url = scrapy.Field(
        output_processor=Identity()
    )
    front_image_path = scrapy.Field()
    praise_nums = scrapy.Field()
    comment_nums = scrapy.Field()
    fav_nums = scrapy.Field()
    tags = scrapy.Field(
        output_processor=Join(separator=',')
    )
    content = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = '''
            insert into cnblogs_article(url_object_id, title, url, create_date, front_image_url, front_image_path, praise_nums, comment_nums, fav_nums, tags, content)
            values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE fav_nums=VALUES(fav_nums), title=VALUES(title), content=VALUES(content)
        '''
        params = list()
        params.append(self.get('url_object_id', ''))
        params.append(self.get('title', ''))
        params.append(self.get('url', ''))
        params.append(self.get('create_date', ''))
        front_image = ','.join(self.get('front_image_url', []))
        params.append(front_image)
        params.append(self.get('front_image_path', ''))
        params.append(self.get('praise_nums', 0))
        params.append(self.get('comment_nums', 0))
        params.append(self.get('fav_nums', 0))
        params.append(self.get('tags', ''))
        params.append(self.get('content', ''))

        return insert_sql, params


class ArticleItemLoader(ItemLoader):
    default_output_processor = TakeFirst()
