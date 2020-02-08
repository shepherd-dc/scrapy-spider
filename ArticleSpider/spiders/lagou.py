# -*- coding: utf-8 -*-
import datetime
import os
import pickle

import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from ArticleSpider.items import ArticleItemLoader, LagouJobItem
from ArticleSpider.utils.common import get_md5


class LagouSpider(CrawlSpider):
    name = 'lagou'
    allowed_domains = ['www.lagou.com']
    start_urls = ['http://www.lagou.com/']

    rules = (
        Rule(LinkExtractor(allow=(r'zhaopin/.*',)), follow=True),
        Rule(LinkExtractor(allow=(r'gongsi/j\d+.html',)), follow=True),
        Rule(LinkExtractor(allow=r'jobs/\d+.html'), callback='parse_job', follow=True)
    )

    def parse_job(self, response):
        # 解析拉勾网的职位
        item_loader = ArticleItemLoader(item=LagouJobItem(), response=response)
        item_loader.add_css("title", ".job-name::attr(title)")
        item_loader.add_value("url", response.url)
        item_loader.add_value("url_object_id", get_md5(response.url))
        item_loader.add_css("salary", ".job_request .salary::text")
        item_loader.add_xpath("job_city", "//*[@class='job_request']/p/span[2]/text()")
        item_loader.add_xpath("work_years", "//*[@class='job_request']/p/span[3]/text()")
        item_loader.add_xpath("degree_need", "//*[@class='job_request']/p/span[4]/text()")
        item_loader.add_xpath("job_type", "//*[@class='job_request']/p/span[5]/text()")

        item_loader.add_css("tags", '.position-label li::text')
        item_loader.add_css("publish_time", ".publish_time::text")
        item_loader.add_css("job_advantage", ".job-advantage p::text")
        item_loader.add_css("job_desc", ".job_bt div")
        item_loader.add_css("job_addr", ".work_addr")
        item_loader.add_css("company_name", "#job_company dt a img::attr(alt)")
        item_loader.add_css("company_url", "#job_company dt a::attr(href)")
        item_loader.add_value("crawl_time", datetime.now())

        job_item = item_loader.load_item()

        return job_item

    def start_requests(self):
        # 使用selenium模拟登录后拿到cookie交给scrapy的request使用
        # 1、通过selenium模拟登录
        # 从文件中读取cookies
        cookies = []
        if os.path.exists("lagou.cookie"):
            cookies = pickle.load(open("lagou.cookie", "rb"))

        if not cookies:
            import time
            from selenium import webdriver
            browser = webdriver.Chrome(executable_path="C:/scrapy/chromedriver.exe")
            browser.get("https://passport.lagou.com/login/login.html")
            browser.find_element_by_css_selector(".form_body .input.input_white").send_keys("18140523326")
            browser.find_element_by_css_selector('.form_body input[type="password"]').send_keys("linfeng0328")
            browser.find_element_by_css_selector('div[data-view="passwordLogin"] input.btn_lg').click()
            input("检查网页是否有验证码要输入，有就在网页输入验证码，输入完后，控制台回车；如果无验证码，则直接回车")
            time.sleep(3)
            cookies = browser.get_cookies()
            # 写入cookie到文件中
            pickle.dump(cookies, open("lagou.cookie", "wb"))

        cookie_dict = {}
        for cookie in cookies:
            cookie_dict[cookie["name"]] = cookie["value"]

        for url in self.start_urls:
            yield scrapy.Request(url, dont_filter=True, cookies=cookie_dict)
