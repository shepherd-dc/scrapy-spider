# -*- coding: utf-8 -*-
import datetime
import json
import re
import time
from pathlib import Path
from urllib import parse

import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from ArticleSpider.items import ArticleItemLoader, ZhihuQuestionItem, ZhihuAnswerItem


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']

    #question的第1页answer的请求url
    start_answer_url = "https://www.zhihu.com/api/v4/questions/{0}/answers?include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cis_labeled%2Cis_recognized%2Cpaid_info%2Cpaid_info_content%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%2A%5D.topics&limit={1}&offset={2}&platform=desktop&sort_by=default"

    # 模拟请求的headers，非常重要，不设置也可能知乎不让你访问请求
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36",
        "HOST": "www.zhihu.com"
    }

    custom_settings = {
        "COOKIES_ENABLED": True
    }

    # scrapy请求的开始时start_request
    def start_requests(self):
        zhihu_findUrl = 'https://www.zhihu.com/notifications'
        if not Path('zhihuCookies.json').exists():
            __class__.loginZhihu()  # 先执行login，保存cookies之后便可以免登录操作

        # 毕竟每次执行都要登录还是挺麻烦的，我们要充分利用cookies的作用
        # 从文件中获取保存的cookies
        with open('zhihuCookies.json', 'r', encoding='utf-8') as f:
            listcookies = json.loads(f.read())  # 获取cookies

        # 把获取的cookies处理成dict类型
        cookies_dict = dict()
        for cookie in listcookies:
            # 在保存成dict时，我们其实只要cookies中的name和value，而domain等其他都可以不要
            cookies_dict[cookie['name']] = cookie['value']

        # Scrapy发起其他页面请求时，带上cookies=cookies_dict即可，同时记得带上header值，
        yield scrapy.Request(url=zhihu_findUrl, cookies=cookies_dict, callback=self.parse, headers=__class__.headers)

    # 使用selenium登录知乎并获取登录后的cookies，后续需要登录的操作都可以利用cookies
    @staticmethod
    def loginZhihu():
        # 登录网址
        loginurl = 'https://www.zhihu.com/signin'
        # driver = webdriver.Chrome(executable_path='C:/scrapy/chromedriver.exe')
        chrome_options = Options()
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

        # 加载webdriver驱动，避免反爬识别用cmd手动启动Chrome：
        # C:\Program Files (x86)\Google\Chrome\Application>chrome.exe --remote-debugging-port=9222
        driver = webdriver.Chrome(executable_path="C:/scrapy/chromedriver.exe",  chrome_options=chrome_options)
        # 加载页面
        driver.get(loginurl)

        time.sleep(3)  # 执行休眠3s等待浏览器的加载

        # 方式1 通过填充用户名和密码
        # driver.find_element_by_name('username').clear()  # 获取用户名框
        # driver.find_element_by_name('username').send_keys(u'username')  # 填充用户名
        # driver.find_element_by_name('password').clear()  # 获取密码框
        # driver.find_element_by_name('password').send_keys(u'password')  # 填充密码
        # input("检查网页是否有验证码要输入，有就在网页输入验证码，输入完后，控制台回车；如果无验证码，则直接回车")
        # # 点击登录按钮,有时候知乎会在输入密码后弹出验证码，这一步之后人工校验
        # driver.find_element_by_css_selector("button[class='Button SignFlow-submitButton Button--primary Button--blue']").click()
        #
        # input_no = input("检查网页是否有验证码要输入，有就在网页输入验证码，输入完后，控制台输入1回车；如果无验证码，则直接回车")
        # if int(input_no) == 1:
        #     # 点击登录按钮
        #     driver.find_element_by_css_selector(
        #         "button[class='Button SignFlow-submitButton Button--primary Button--blue']").click()

        # 方式2 直接通过扫描二维码，如果不是要求全自动化，建议用这个，非常直接，毕竟我们这一步只是想保存登录后的cookies，至于用何种方式登录，可以不必过于计较
        driver.find_element_by_css_selector(".SignFlow-qrcodeTab").click()
        input("请扫描页面二维码，并确认登录后，点击回车")  # 点击二维码手机扫描登录

        time.sleep(3)  # 同样休眠3s等待登录完成

        input("检查网页是否有完成登录跳转，如果完成则直接回车")

        # 通过上述的方式实现登录后，其实我们的cookies在浏览器中已经有了，我们要做的就是获取
        cookies = driver.get_cookies()  # Selenium为我们提供了get_cookies来获取登录cookies
        driver.close()  # 获取cookies便可以关闭浏览器
        # 然后的关键就是保存cookies，之后请求从文件中读取cookies就可以省去每次都要登录一次的
        # 当然可以把cookies返回回去，但是之后的每次请求都要先执行一次login没有发挥cookies的作用
        jsonCookies = json.dumps(cookies)  # 通过json将cookies写入文件
        with open('zhihuCookies.json', 'w') as f:
            f.write(jsonCookies)
        # print(cookies)

    def parse(self, response):
        # 这里打印出https://www.zhihu.com/notifications页面中通知中心带上cookies登录完成
        # print("登录成功: %s" % response.xpath('//div[@class="Card Notifications-Main"]//h1/text()').extract_first())

        """
        提取出html页面中的所有url 并跟踪这些url进一步爬取
        如果提取的url中格式为 /question/xxx 就下载之后直接进入解析函数
        """
        all_urls = response.css("a::attr(href)").extract()
        all_urls = [parse.urljoin(response.url, url) for url in all_urls]
        all_urls = filter(lambda x: True if x.startswith("https") else False, all_urls)
        for url in all_urls:
            match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$).*", url)
            if match_obj:
                # 如果提取到question相关的页面则下载后交由提取函数进行提取
                request_url = match_obj.group(1)
                question_id = match_obj.group(2)
                yield scrapy.Request(request_url, headers=self.headers, meta={"question_id": question_id}, callback=self.parse_question)
            else:
                # 如果不是question页面则直接进一步跟踪
                # pass
                yield scrapy.Request(url, headers=self.headers, callback=self.parse)

    def parse_question(self, response):
        # 处理question页面， 从页面中提取出具体的question item

        question_id = response.meta.get('question_id', '')

        item_loader = ArticleItemLoader(item=ZhihuQuestionItem(), response=response)
        item_loader.add_css("title", "h1.QuestionHeader-title::text")
        item_loader.add_css("content", ".QuestionHeader-detail")
        item_loader.add_value("url", response.url)
        item_loader.add_value("zhihu_id", question_id)
        item_loader.add_css("answer_num", ".List-headerText span::text")
        item_loader.add_css("comments_num", ".QuestionHeader-Comment span::text")
        item_loader.add_css("watch_user_num", ".NumberBoard:first-child .NumberBoard-itemValue::text")
        item_loader.add_css("click_num", ".NumberBoard:last-child .NumberBoard-itemValue::text")
        item_loader.add_css("topics", ".QuestionHeader-topics .Popover div::text")

        question_item = item_loader.load_item()

        # 请求答案api
        answer_url = self.start_answer_url.format(question_id, 5, 0)
        yield scrapy.Request(answer_url, headers=self.headers, callback=self.parse_answer)

        yield question_item

    def parse_answer(self, response):
        # 处理question的answer
        answer_json = json.loads(response.text)
        is_end = answer_json["paging"]["is_end"]
        next_url = answer_json["paging"]["next"]

        # 提取answer的具体字段
        for answer in answer_json["data"]:
            answer_item = ZhihuAnswerItem()
            answer_item["zhihu_id"] = answer["id"]
            answer_item["url"] = answer["url"]
            answer_item["question_id"] = answer["question"]["id"]
            answer_item["author_id"] = answer["author"]["id"] if "id" in answer["author"] else None
            answer_item["content"] = answer["content"] if "content" in answer else None
            answer_item["praise_num"] = answer["voteup_count"]
            answer_item["comments_num"] = answer["comment_count"]
            answer_item["create_time"] = answer["created_time"]
            answer_item["update_time"] = answer["updated_time"]
            answer_item["crawl_time"] = datetime.datetime.now()

            yield answer_item

        if not is_end:
            yield scrapy.Request(next_url, headers=self.headers, callback=self.parse_answer)
