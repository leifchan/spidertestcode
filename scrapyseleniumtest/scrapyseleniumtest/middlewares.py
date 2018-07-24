# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html


from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scrapy.http import HtmlResponse
from logging import getLogger

class SeleniumMiddleware():
    def __init__(self,timeout=None):
        self.logger = getLogger(__name__)
        self.timeout = timeout
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument('--headless')
        self.browser = webdriver.Chrome(chrome_options=self.chrome_options)
        #self.browser.set_page_load_timeout(self.timeout)
        self.wait = WebDriverWait(self.browser,self.timeout)
        
    def __del__(self):
        self.browser.close()
    
    def process_request(self,request,spider):
        """
        用Chrome 抓取页面
        param request:Request对象
        param spider:Spider对象
        return:HtmlResponse
        """
        self.logger.debug('Chrome is starting')
        page = request.meta.get('page',1)
        
        try:
            self.browser.get(request.url)
            if page >1:
                input1 = self.wait.until(
                        EC.presence_of_element_located(
                                (By.CSS_SELECTOR,'#mainsrp-pager div.form > input')))
                submit = self.wait.until(
                        EC.element_to_be_clickable(
                                (By.CSS_SELECTOR,'#mainsrp-pager div.form > span.btn.J_Submit')))
                input1.clear()
                input1.send_keys(page)
                submit.click()
                
            self.wait.until(EC.text_to_be_present_in_element(
                    (By.CSS_SELECTOR,'#mainsrp-pager li.item.active > span'),str(page)))
            self.wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR,'.m-itemlist .items .item')))
            return HtmlResponse(url=request.url,body=self.browser.page_source,
                                request=request,encoding='utf-8',status=200)
            
        except TimeoutException:
            return HtmlResponse(url=request.url,status=500,request=request)
        
    @classmethod
    def from_crawler(cls,crawler):
        return cls(timeout = crawler.settings.get('SELENIUM_TIMEOUT'))
    
        

