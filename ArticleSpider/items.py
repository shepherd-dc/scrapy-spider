# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
import datetime

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, Identity, MapCompose, Join

from ArticleSpider.utils.common import date_convert, extract_num


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


class ZhihuQuestionItem(scrapy.Item):
    #知乎的问题 item
    zhihu_id = scrapy.Field()
    topics = scrapy.Field(
        output_processor=Join(separator=',')
    )
    url = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    answer_num = scrapy.Field()
    comments_num = scrapy.Field()
    watch_user_num = scrapy.Field()
    click_num = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        #插入知乎question表的sql语句
        insert_sql = """
            insert into zhihu_question(zhihu_id, topics, url, title, content, answer_num, comments_num,
              watch_user_num, click_num, crawl_time
              )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE content=VALUES(content), answer_num=VALUES(answer_num), comments_num=VALUES(comments_num),
              watch_user_num=VALUES(watch_user_num), click_num=VALUES(click_num)
        """
        zhihu_id = self.get("zhihu_id", "")
        topics = self.get("topics", "")
        url = self.get("url", "")
        title = self.get("title", "")
        content = self.get("content", "")
        answer_num = self.get("answer_num", 0)
        comments_num = self.get("comments_num", 0)
        watch_user_num = int(self.get("watch_user_num", 0))
        click_num = int(self.get("click_num", 0))
        crawl_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        params = (zhihu_id, topics, url, title, content, answer_num, comments_num,
                  watch_user_num, click_num, crawl_time)

        return insert_sql, params


class ZhihuAnswerItem(scrapy.Item):
    #知乎的问题回答item
    zhihu_id = scrapy.Field()
    url = scrapy.Field()
    question_id = scrapy.Field()
    author_id = scrapy.Field()
    content = scrapy.Field()
    praise_num = scrapy.Field()
    comments_num = scrapy.Field()
    create_time = scrapy.Field()
    update_time = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        #插入知乎question表的sql语句
        insert_sql = """
            insert into zhihu_answer(zhihu_id, url, question_id, author_id, content, praise_num, comments_num,
              create_time, update_time, crawl_time
              ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
              ON DUPLICATE KEY UPDATE content=VALUES(content), comments_num=VALUES(comments_num), praise_num=VALUES(praise_num),
              update_time=VALUES(update_time)
        """

        create_time = datetime.datetime.fromtimestamp(self["create_time"]).strftime('%Y-%m-%d %H:%M:%S')
        update_time = datetime.datetime.fromtimestamp(self["update_time"]).strftime('%Y-%m-%d %H:%M:%S')
        params = (
            self["zhihu_id"], self["url"], self["question_id"],
            self["author_id"], self["content"], self["praise_num"],
            self["comments_num"], create_time, update_time,
            self["crawl_time"].strftime('%Y-%m-%d %H:%M:%S'),
        )

        return insert_sql, params


class ArticleItemLoader(ItemLoader):
    default_output_processor = TakeFirst()
