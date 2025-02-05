#!/usr/bin/python3
#
# @author bunhash
# @email bunhash@bhmail.me
#
# Parses scribblehub.com novels
#

from bs4 import BeautifulSoup, NavigableString
from selenium.webdriver.common.by import By
import time

class Parser:

    @staticmethod
    def parse_book_info(html):
        soup = BeautifulSoup(html, 'lxml')
        title_div = soup.find('div', {'class' : 'fic_title'})
        author_span = soup.find('span', {'class' : 'auth_name_fic'})

        title = title_div.text.strip()
        author = author_span.text.strip()

        # Encode both
        title = title.encode('ascii', errors='ignore')
        if len(title) == 0:
            title = b'???'
        author = author.encode('ascii', errors='ignore')
        if len(author) == 0:
            author = b'???'

        return title.decode('ascii'), author.decode('ascii')

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
        for child in chapter:
            try:
                del child['class']
            except:
                pass
            paragraphs.append(child)
        #for p in chapter.find_all('p'):
        #    del p['class']
        #    paragraphs.append(p)
        #if not paragraphs:
        #    for br in chapter.find_all('br'):
        #        br.replace_with('\n')
        #    for line in chapter.get_text().split('\n'):
        #        line = line.strip()
        #        if line:
        #            para_tag = soup.new_tag('p')
        #            para_tag.append(NavigableString(line))
        #            paragraphs.append(para_tag)

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

    @staticmethod
    def next_page(html):
        soup = BeautifulSoup(html, 'lxml')
        link = soup.find('a', {'class' : 'btn-next'})
        if link:
            if 'disabled' in link['class']:
                return None
            url = link['href']
            if 'https://' not in url:
                return f'https://www.scribblehub.com{url}'
            return url
        return None

class SolverParser(Parser):

    def __init__(self, client):
        self._client = client

    def get_book_info_page(self, url):
        raise Exception('not implemented for now')

    def get_chapterlist(self, url, html):
        raise Exception('not implemented for now')

    def get_chapter(self, url):
        res = self._client.get(url)
        if b'id="main read chapter"' in res:
            return res
        raise Exception('No chapter found')

class SeleniumParser(Parser):

    def __init__(self, driver):
        self._driver = driver

    def get_book_info_page(self, url):
        self._driver.get(url)
        _ = self._driver.wait_for_class_name('fic_title')
        _ = self._driver.wait_for_class_name('auth_name_fic')
        return self._driver.page_source()

    def get_chapterlist(self, url, html):
        self._driver.add_cookie({
            'name' : 'toc_show',
            'value' : '50'
        })
        self._driver.get(url)

        chpcounter_input = self._driver.wait_for_id('chpcounter')
        total_chapters = int(chpcounter_input.get_attribute('value'))
        total_toc_pages = (total_chapters + 49) // 50

        toc_page = 1
        chapterlist = list()
        while True:
            chapters_view = self._driver.wait_for_id('review_new_tab')

            # Get all chapters on the page
            ol_el = chapters_view.find_element(By.CLASS_NAME, 'toc_ol')
            for row in ol_el.find_elements(By.TAG_NAME, 'li'):
                link = row.find_element(By.TAG_NAME, 'a')
                chapterlist.append(link.get_attribute('href'))

            # Go to next page
            navigation_bar = self._driver.wait_for_id('pagination-mesh-toc')
            arrow = navigation_bar.find_element(By.CLASS_NAME, 'next')
            toc_page = toc_page + 1
            if toc_page > total_toc_pages:
                break
            self._driver.get(url + f'?toc={toc_page}')

        return chapterlist[::-1]

    def get_chapter(self, url):
        self._driver.get(url)
        _ = self._driver.wait_for_id('main read chapter')
        return self._driver.page_source()
