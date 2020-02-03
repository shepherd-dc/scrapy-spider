import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

# chrome_options = Options()
# chrome_options.add_argument("--disable-extensions")
# chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

# browser = webdriver.Chrome(executable_path="C:/scrapy/chromedriver.exe",  chrome_options=chrome_options)

browser = webdriver.Chrome(executable_path='C:/scrapy/chromedriver.exe')

# browser.get('https://www.jianshu.com/sign_in')
#
# browser.find_element_by_css_selector(".input-prepend input#session_email_or_mobile_number").send_keys(Keys.CONTROL + "a")
# browser.find_element_by_css_selector(".input-prepend input#session_email_or_mobile_number").send_keys("18140523326")
#
# browser.find_element_by_css_selector(".input-prepend input#session_password").send_keys(Keys.CONTROL + "a")
# browser.find_element_by_css_selector(".input-prepend input#session_password").send_keys("linfeng0328")
# browser.find_element_by_css_selector("#sign-in-form-submit-btn").click()
# browser.find_element_by_css_selector("#sign-in-form-submit-btn").click()

browser.get('https://account.cnblogs.com/signin')
browser.find_element_by_css_selector("input#LoginName").send_keys("shepherd_nt")
browser.find_element_by_css_selector("input#Password").send_keys("linfeng0328")
browser.find_element_by_css_selector("#submitBtn").click()

print('yes')

time.sleep(60)
