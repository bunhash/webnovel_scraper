#!/usr/bin/python3
#
# @author bunhash
# @email bunhash@bhmail.me
#
# Parses scribblehub.com novels
#

import time
from bs4 import BeautifulSoup, NavigableString
from selenium.webdriver.common.by import By

class Parser:

    @staticmethod
    def load_book_page(driver, url):
        driver.get(url)

    @staticmethod
    def get_title(driver):
        story_div = driver.wait_for_class_name('fic_title')
        return story_div.text.strip()

    @staticmethod
    def get_author(driver):
        author_span = driver.wait_for_class_name('auth_name_fic')
        return author_span.text.strip()

    @staticmethod
    def get_chapterlist(driver):
        chapterlist = list()
        while True:
            chapters_view = driver.wait_for_id('review_new_tab')

            # Get all chapters on the page
            ol_el = chapters_view.find_element(By.CLASS_NAME, 'toc_ol')
            for row in ol_el.find_elements(By.TAG_NAME, 'li'):
                link = row.find_element(By.TAG_NAME, 'a')
                chapterlist.append(link.get_attribute('href'))

            # Go to next page
            navigation_bar = driver.wait_for_id('pagination-mesh-toc')
            arrow = navigation_bar.find_element(By.CLASS_NAME, 'next')
            if arrow.tag_name == 'a':
                arrow.click()
                time.sleep(1) # it overwrites `review_new_tab`
            else:
                break

        return chapterlist[::-1]

    @staticmethod
    def get_chapter(driver, url):
        driver.get(url)
        content = driver.wait_for_id('main read chapter')
        return content.get_attribute('innerHTML').encode('utf-8')

    @staticmethod
    def parse_chapter(html):
        soup = BeautifulSoup(html, 'lxml')
        chapter = soup.find('div', {'id' : 'chp_raw'})
        if not chapter:
            raise Exception('could not find chapter')

        # Parse title
        title = '???'
        title_el = soup.find('div', {'class' : 'chapter-title'})
        if title_el:
            title = title_el.text.strip()

        # Get the reading content
        paragraphs = list()
        for p in chapter.find_all('p'):
            del p['class']
            paragraphs.append(p)
        if not paragraphs:
            for br in chapter.find_all('br'):
                br.replace_with('\n')
            for line in chapter.get_text().split('\n'):
                line = line.strip()
                if line:
                    para_tag = soup.new_tag('p')
                    para_tag.append(NavigableString(line))
                    paragraphs.append(para_tag)

        # Build chapter HTML
        chapter = BeautifulSoup('<html><head></head><body></body></html>', 'lxml')

        # Add title tag
        title_tag = chapter.new_tag('h1')
        title_tag.append(NavigableString(title))
        chapter.body.append(title_tag)

        # Add paragraphs
        for p in paragraphs:
            chapter.body.append(p)
        
        # Return chapter title and chapter html
        return title.encode('utf-8', errors='ignore'), chapter.encode('utf-8', errors='ignore')
