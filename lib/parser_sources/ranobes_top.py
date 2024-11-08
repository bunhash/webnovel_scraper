#!/usr/bin/python3
#
# @author bunhash
# @email bunhash@bhmail.me
#
# Parses ranobes.top novels
#

import json
from bs4 import BeautifulSoup, NavigableString
from selenium.webdriver.common.by import By

class Parser:

    @staticmethod
    def load_book_page(driver, url):
        driver.get(url)

    @staticmethod
    def get_title(driver):
        story_div = driver.wait_for_class_name('r-fullstory-s1')
        title_h1 = story_div.find_element(By.CLASS_NAME, 'title')
        title_span = title_h1.find_element(By.XPATH, './/span[1]')
        return title_span.text.strip()

    @staticmethod
    def get_author(driver):
        story_div = driver.wait_for_class_name('r-fullstory-s1')
        title_h1 = story_div.find_element(By.CLASS_NAME, 'title')
        author_span = title_h1.find_element(By.XPATH, './/span[2]')
        return author_span.text.lstrip('by').strip()

    @staticmethod
    def get_chapterlist(driver):

        # Click "MORE CHAPTERS"
        footer = driver.wait_for_class_name('r-fullstory-chapters-foot')
        more_chapters = footer.find_element(By.XPATH, './/a[2]')
        driver.click(more_chapters)

        # Read chapters
        chapterlist = list()
        while True:
            footer = driver.wait_for_class_name('page_next')
            toc_soup = BeautifulSoup(driver.page_source(), 'lxml')
            data = None
            for script in toc_soup.find_all('script'):
                if 'window.__DATA__' in script.text:
                    data = json.loads(script.text.strip().strip('window.__DATA__ = '))
                    break
            for chapter in data['chapters']:
                chapterlist.append(chapter['link'])
            try:
                # Click next page arrow
                next_page = footer.find_element(By.XPATH, './/a[1]')
                driver.click(next_page)
            except:
                break
        return chapterlist[::-1]

    @staticmethod
    def get_chapter(driver, url):
        driver.get(url)
        driver.wait_for_id('arrticle')
        return driver.page_source()

    @staticmethod
    def parse_chapter(html):
        soup = BeautifulSoup(html, 'lxml')

        # Parse title
        title = '???'
        title_el = soup.find('h1', {'class' : 'h4 title'})
        if title_el:
            for child in title_el.children:
                if isinstance(child, NavigableString):
                    t = child.text.strip()
                    if len(t) > 0:
                        title = t

        # Get the reading content
        paragraphs = list()
        story = soup.find('div', {'id' : 'arrticle'})
        if story:
            for p in story.find_all('p'):
                paragraphs.append(p)
            if len(paragraphs) == 0:
                for child in story.children:
                    if isinstance(child, NavigableString):
                        p = soup.new_tag('p')
                        p.append(child)
                        paragraphs.append(p)

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
