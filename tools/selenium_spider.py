import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

# chrome_options = Options()
# chrome_options.add_argument("--disable-extensions")
# chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

# # 加载webdriver驱动，避免反爬识别，用cmd手动启动Chrome：
# # C:\Program Files (x86)\Google\Chrome\Application>chrome.exe --remote-debugging-port=9222
# browser = webdriver.Chrome(executable_path="C:/scrapy/chromedriver.exe",  chrome_options=chrome_options)

# browser = webdriver.Chrome(executable_path='C:/scrapy/chromedriver.exe')

# browser.get('https://www.jianshu.com/sign_in')
#
# browser.find_element_by_css_selector(".input-prepend input#session_email_or_mobile_number").send_keys(Keys.CONTROL + "a")
# browser.find_element_by_css_selector(".input-prepend input#session_email_or_mobile_number").send_keys("18140523326")
#
# browser.find_element_by_css_selector(".input-prepend input#session_password").send_keys(Keys.CONTROL + "a")
# browser.find_element_by_css_selector(".input-prepend input#session_password").send_keys("linfeng0328")
# browser.find_element_by_css_selector("#sign-in-form-submit-btn").click()
# browser.find_element_by_css_selector("#sign-in-form-submit-btn").click()

# browser.get('https://account.cnblogs.com/signin')
# time.sleep(3) # 等待页面加载完成，防止下面的操作找不到原素
# browser.find_element_by_css_selector("input#LoginName").clear()
# browser.find_element_by_css_selector("input#LoginName").send_keys("shepherd_nt")
# browser.find_element_by_css_selector("input#Password").clear()
# browser.find_element_by_css_selector("input#Password").send_keys("linfeng0328")
# browser.find_element_by_css_selector("#submitBtn").click()
#
# print('yes')
#
# time.sleep(60)

# # 自动下拉滚动条翻译
# browser.get('https://www.oschina.net/blog')
# time.sleep(3)
#
# js_script = 'window.scrollTo(0, document.body.scrollHeight); var lenOfPage = document.body.scrollHeight; return lenOfPage;'
# lenOfPage = browser.execute_script(js_script)
#
# match=False
# while(match == False):
#     lastCount = lenOfPage
#     time.sleep(3)
#     lenOfPage = browser.execute_script(js_script)
#     if lastCount == lenOfPage:
#         match = True

# 设置Chromedriver不加载图片
chrome_opt = webdriver.ChromeOptions()
prefs = {
    "profile.managed_default_content_settings.images": 2
}
chrome_opt.add_experimental_option('prefs', prefs)
driver = webdriver.Chrome(executable_path="C:/scrapy/chromedriver.exe", chrome_options=chrome_opt)
driver.get('https://www.oschina.net/blog')

# phantomjs：无界面的浏览器。多进程情况下性能会下降很严重。
# UserWarning: Selenium support for PhantomJS has been deprecated, please use headless versions of Chrome or Firefox instead.
exe_path = 'C:/scrapy/phantomjs-2.1.1-windows/bin/phantomjs.exe'
browser = webdriver.PhantomJS(executable_path=exe_path)
browser.get('https://my.oschina.net/jijunjian/blog/3162766')
print(browser.page_source)
browser.quit()
