import json
import re
from pathlib import Path
from urllib import parse

import requests
import scrapy
from scrapy import Request

from ArticleSpider.items import ArticleSpiderItem, ArticleItemLoader
from ArticleSpider.utils import common


class CnblogsSpider(scrapy.Spider):
    name = 'cnblogs'
    allowed_domains = ['news.cnblogs.com']
    start_urls = ['http://news.cnblogs.com/']

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36"
    }

    def parse(self, response):
        '''
        1. 获取新闻列表中的新闻url交给scrapy下载，下载完成后后调用相应的解析方法（callback）
        2. 获取下一页的url并交给scrapy下载，下载完成后交给parse继续跟进
        '''
        # url = response.xpath('// div[@id="news_list"] // h2[@class="news_entry"] / a / @href').extract()
        # url = response.css('#news_list .news_entry a::attr(href)').extract()
        post_nodes = response.css('#news_list .news_block')[:1]
        for post_node in post_nodes:
            image_url = post_node.css('.entry_summary a img::attr(src)').extract_first('')
            if image_url.startswith('//'):
                image_url = 'https:' + image_url
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
        # yield Request(url=parse.urljoin(response.url, next_url))

    def parse_detail(self, response):
        match_re = re.match(".*?(\d+)", response.url)
        if match_re:
            post_id = match_re.group(1)

            # article_item = ArticleSpiderItem()
            # title = response.css("#news_title a::text").extract_first("")
            # create_date = response.css("#news_info .time::text").extract_first("")
            # match_re = re.match(".*?(\d+.*)", create_date)
            # if match_re:
            #     create_date = match_re.group(1)
            # content = response.css("#news_content").extract_first("")
            # tag_list = response.css(".news_tags a::text").extract()
            # tags = ",".join(tag_list)

            # html = requests.get(parse.urljoin(response.url, "/NewsAjax/GetAjaxNewsInfo?contentId={}".format(post_id)))
            # j_data = json.loads(html.text)
            # praise_nums = j_data["DiggCount"]
            # fav_nums = j_data["TotalView"]
            # comment_nums = j_data["CommentCount"]
            # article_item["title"] = title
            # article_item["create_date"] = create_date
            # article_item["content"] = content
            # article_item["tags"] = tags
            # article_item["url"] = response.url
            # if response.meta.get("front_image_url", ""):
            #     article_item["front_image_url"] = [response.meta.get("front_image_url", "")]
            # else:
            #     article_item["front_image_url"] = []

            item_loader = ArticleItemLoader(item=ArticleSpiderItem(), response=response)
            item_loader.add_css('title', '#news_title a::text')
            item_loader.add_css('create_date', '#news_info .time::text')
            item_loader.add_css('content', '#news_content')
            item_loader.add_css('tags', '.news_tags a::text')
            item_loader.add_value('url', response.url)
            if response.meta.get('front_image_url', []):
                item_loader.add_value('front_image_url', response.meta.get('front_image_url', []))

            yield Request(url=parse.urljoin(response.url, "/NewsAjax/GetAjaxNewsInfo?contentId={}".format(post_id)),
                          meta={"article_item": item_loader, "url": response.url}, callback=self.parse_nums)

    def parse_nums(self, response):
        j_data = json.loads(response.text)
        # article_item = response.meta.get("article_item", "")
        item_loader = response.meta.get('article_item', '')

        # praise_nums = j_data["DiggCount"]
        # fav_nums = j_data["TotalView"]
        # comment_nums = j_data["CommentCount"]
        #
        # article_item["praise_nums"] = praise_nums
        # article_item["fav_nums"] = fav_nums
        # article_item["comment_nums"] = comment_nums
        # article_item["url_object_id"] = common.get_md5(article_item["url"])

        item_loader.add_value('praise_nums', j_data['DiggCount'])
        item_loader.add_value('fav_nums', j_data['TotalView'])
        item_loader.add_value('comment_nums', j_data['CommentCount'])
        item_loader.add_value('url_object_id', common.get_md5(response.meta.get('url', '')))

        article_item = item_loader.load_item()

        yield article_item


    def start_requests(self):
        zhihu_findUrl = 'https://www.zhihu.com/notifications'
        if not Path('cnblogsCookies.json').exists():
            self.login()  # 先执行login，保存cookies之后便可以免登录操作

        # 毕竟每次执行都要登录还是挺麻烦的，我们要充分利用cookies的作用
        # 从文件中获取保存的cookies
        with open('cnblogsCookies.json', 'r', encoding='utf-8') as f:
            list_cookies = json.loads(f.read())  # 获取cookies

        # 把获取的cookies处理成dict类型
        cookies_dict = dict()
        for cookie in list_cookies:
            # 在保存成dict时，我们其实只要cookies中的name和value，而domain等其他都可以不要
            cookies_dict[cookie['name']] = cookie['value']

        for url in self.start_urls:
            yield Request(url=url, cookies=cookies_dict, headers=self.headers, dont_filter=True)

    def login(self):
        import time
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.keys import Keys

        # chrome_options = Options()
        # chrome_options.add_argument("--disable-extensions")
        # chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        #
        # browser = webdriver.Chrome(executable_path="C:/scrapy/chromedriver.exe",  chrome_options=chrome_options)

        browser = webdriver.Chrome(executable_path='C:/scrapy/chromedriver.exe')
        browser.get('https://account.cnblogs.com/signin')
        time.sleep(3)  # 执行休眠3s等待浏览器的加载

        # browser.find_element_by_css_selector("input#LoginName").send_keys(Keys.CONTROL + "a")
        browser.find_element_by_css_selector("input#LoginName").clear()
        browser.find_element_by_css_selector("input#LoginName").send_keys("shepherd_nt")
        browser.find_element_by_css_selector("input#Password").clear()
        browser.find_element_by_css_selector("input#Password").send_keys("linfeng0328")
        input("检查网页是否有验证码要输入，有就在网页输入验证码，输入完后，控制台回车；如果无验证码，则直接回车")
        try:
            browser.find_element_by_css_selector("#submitBtn").click()
        except:
            pass
        print('yes')
        # 通过上述的方式实现登录后，其实我们的cookies在浏览器中已经有了，我们要做的就是获取
        cookies = browser.get_cookies()  # Selenium为我们提供了get_cookies来获取登录cookies
        browser.close()  # 获取cookies便可以关闭浏览器
        # 然后的关键就是保存cookies，之后请求从文件中读取cookies就可以省去每次都要登录一次的
        # 当然可以把cookies返回回去，但是之后的每次请求都要先执行一次login没有发挥cookies的作用
        jsonCookies = json.dumps(cookies)  # 通过json将cookies写入文件
        with open('cnblogsCookies.json', 'w') as f:
            f.write(jsonCookies)
        print(cookies)
