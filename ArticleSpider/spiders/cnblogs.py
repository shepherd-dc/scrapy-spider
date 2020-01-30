from urllib import parse

import scrapy
from scrapy import Request


class CnblogsSpider(scrapy.Spider):
    name = 'cnblogs'
    allowed_domains = ['news.cnblogs.com']
    start_urls = ['http://news.cnblogs.com/']

    def parse(self, response):
        '''
        1. 获取新闻列表中的新闻url交给scrapy下载，下载完成后后调用相应的解析方法（callback）
        2. 获取下一页的url并交给scrapy下载，下载完成后交给parse继续跟进
        '''
        # url = response.xpath('// div[@id="news_list"] // h2[@class="news_entry"] / a / @href').extract()
        # url = response.css('#news_list .news_entry a::attr(href)').extract()
        post_nodes = response.css('#news_list .news_block')
        for post_node in post_nodes:
            image_url = post_node.css('.entry_summary a img::attr(src)').extract_first('')
            post_url = post_node.css('.news_entry a::attr(href)').extract_first('')
            yield Request(
                url=parse.urljoin(response.url, post_url),
                meta={'front_image_url': image_url},
                callback=self.parse_detail
            )

        ''' 提取下一页并交给scrapy下载 '''
        # next_url = response.css('.pager a:last-child::text').extract_first('')
        # if next_url == 'Next >':
        #     next_url = response.css('.pager a:last-child::attr(href)').extract_first('')
        #     yield Request(url=parse.urljoin(response.url, next_url))
        next_url = response.xpath('// div[@class="pager"] // a[contains(text(), "Next >")] / @href').extract_first('')
        # 递归调用parse（默认callback为parse）继续处理下一页列表url
        yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)

    def parse_detail(self, response):
        pass