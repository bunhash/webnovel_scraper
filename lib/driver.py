#!/usr/bin/env python3
#
# @author bunhash
# @email bunhash@bhmail.me
#
# Wrapper to the Selenium driver
#

from selenium.webdriver import ChromeOptions as Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import random
import time
import undetected_chromedriver as uc

class Driver:

    def __init__(self):
        options = Options()
        options.add_argument('--start-maximized')
        options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36')
        self._driver = uc.Chrome(options=options, use_subprocess=False)

    def __del__(self):
        try:
            self._driver.close()
            self._driver.quit()
        except:
            pass

    def get(self, url):
        self._driver.get(url)

    def click(self, element):
        time.sleep(random.randrange(10, 200) / 100)
        element.click()

    def current_url(self):
        return self._driver.current_url

    def add_cookie(self, cookie):
        self._driver.add_cookie(cookie)
    
    def page_source(self):
        return self._driver.page_source.encode('utf-8', errors='ignore')

    def wait_for(self, tup, timeout=60):
        return WebDriverWait(self._driver, timeout).until(EC.presence_of_element_located(tup))

    def wait_for_tag(self, tag, timeout=60):
        return self.wait_for((By.TAG_NAME, tag), timeout=timeout)

    def wait_for_class_name(self, name, timeout=60):
        return self.wait_for((By.CLASS_NAME, name), timeout=timeout)

    def wait_for_id(self, el_id, timeout=60):
        return self.wait_for((By.ID, el_id), timeout=timeout)

    def wait_for_xpath(self, xpath, timeout=60):
        return self.wait_for((By.XPATH, xpath), timeout=timeout)
