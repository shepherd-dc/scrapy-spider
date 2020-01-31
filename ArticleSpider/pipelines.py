# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import codecs
import json

from scrapy.exporters import JsonItemExporter
from scrapy.pipelines.images import ImagesPipeline


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
