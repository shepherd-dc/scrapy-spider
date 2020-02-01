# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import codecs
import json

import MySQLdb
from scrapy.exporters import JsonItemExporter
from scrapy.pipelines.images import ImagesPipeline
from twisted.enterprise import adbapi


class ArticleSpiderPipeline(object):
    def process_item(self, item, spider):
        return item


class ArticleImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        if 'front_image_url' in item:
            if results:
                for ok, value in results:
                    image_file_path = value['path']
                item['front_image_path'] = image_file_path

        return item


class MysqlPipeline(object):
    '''用mysqlclient同步写入数据库'''
    def __init__(self):
        self.connect = MySQLdb.connect('127.0.0.1', 'root', '123456', 'article_spider', charset='utf8', use_unicode=True)
        self.cursor = self.connect.cursor()

    def process_item(self, item, spider):
        insert_sql = '''
            insert into cnblogs_article(url_object_id, title, url, create_date, fav_nums)
            values (%s, %s, %s, %s, %s)
        '''
        self.cursor.execute(insert_sql, (item["url_object_id"], item["title"], item["url"], item["create_date"], item["fav_nums"]))
        self.connect.commit()


class MysqlTwistedPipeline(object):
    '''用twisted异步写入数据库'''
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        from MySQLdb.cursors import DictCursor
        dbparms = dict(
            host = settings["MYSQL_HOST"],
            db = settings["MYSQL_DBNAME"],
            user = settings["MYSQL_USER"],
            passwd = settings["MYSQL_PASSWORD"],
            charset = 'utf8',
            cursorclass = DictCursor,
            use_unicode = True
        )
        dbpool = adbapi.ConnectionPool("MySQLdb", **dbparms)

        return cls(dbpool)

    def process_item(self, item, spider):
        # 使用twisted将mysql插入变成异步执行
        query = self.dbpool.runInteraction(self.do_insert, item)
        # 处理异常
        query.addErrback(self.handle_error, item, spider)

    def do_insert(self, cursor, item):
        # 执行具体的插入
        insert_sql = '''
                    insert into cnblogs_article(url_object_id, title, url, create_date, front_image_url, front_image_path, praise_nums, comment_nums, fav_nums, tags, content)
                    values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE fav_nums=VALUES(fav_nums)
                '''
        params = list()
        params.append(item.get('url_object_id', ''))
        params.append(item.get('title', ''))
        params.append(item.get('url', ''))
        params.append(item.get('create_date', ''))
        front_image = ','.join(item.get('front_image_url', []))
        params.append(front_image)
        params.append(item.get('front_image_path', ''))
        params.append(item.get('praise_nums', 0))
        params.append(item.get('comment_nums', 0))
        params.append(item.get('fav_nums', 0))
        params.append(item.get('tags', ''))
        params.append(item.get('content', ''))

        cursor.execute(insert_sql, tuple(params))

    def handle_error(self, failure, item, spider):
        # 处理异步插入的异常
        print (failure)


class JsonWithEncodingPipeline(object):
    '''自定义导出json文件'''
    def __init__(self):
        self.file = codecs.open('article.json', 'a', encoding='utf-8')

    def process_item(self, item, spider):
        lines = json.dumps(dict(item), ensure_ascii=False) + '\n'
        self.file.write(lines)
        return item

    def spider_closed(self, spider):
        self.file.close()


class JsonExporterPipeline(object):
    '''用scrapy内置的exporter导出json文件'''
    def __init__(self):
        self.file = open('article_export.json', 'wb')
        self.exporter = JsonItemExporter(self.file, encoding='utf-8', ensure_ascii=False)
        self.exporter.start_exporting()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item

    def spider_closed(self, spider):
        self.exporter.finish_exporting()
        self.file.close()
