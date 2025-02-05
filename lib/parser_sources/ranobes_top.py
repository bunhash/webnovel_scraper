#!/usr/bin/python3
#
# @author bunhash
# @email bunhash@bhmail.me
#
# Parses ranobes.top novels
#

from bs4 import BeautifulSoup, NavigableString
from selenium.webdriver.common.by import By
import json
import time

class Parser:

    @staticmethod
    def parse_book_info(html):
        soup = BeautifulSoup(html, 'lxml')
        story_div = soup.find('div', {'class' : 'r-fullstory-s1'})
        title_h1 = story_div.find('h1', {'class' : 'title'})
        spans = title_h1.find_all('span')

        # Get title and author
        title = None
        author = spans[1].text.lstrip('by').strip()
        if spans[0].has_attr('hidden'):
            for span in spans:
                span.decompose()
            title = title_h1.text.strip()
        else:
            title = spans[0].text.strip()

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

    @staticmethod
    def next_page(html):
        soup = BeautifulSoup(html, 'lxml')
        link = soup.find('a', {'id' : 'next'})
        if link:
            url = link['href']
            if 'https://' not in url:
                return f'https://www.ranobes.top{url}'
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
        if b'id="arrticle"' in res:
            return res
        raise Exception('No chapter found')

class SeleniumParser(Parser):

    def __init__(self, driver):
        self._driver = driver

    def get_book_info_page(self, url):
        self._driver.get(url)
        _ = self._driver.wait_for_class_name('r-fullstory-s1')
        _ = self._driver.wait_for_class_name('r-fullstory-chapters-foot')
        return self._driver.page_source()

    def get_chapterlist(self, url, html):
        soup = BeautifulSoup(html, 'lxml')

        # Get total number of translated chapters
        novel_spec_div = soup.find('div', {'class' : 'r-fullstory-spec'})
        novel_spec_uls = novel_spec_div.find_all('ul')
        novel_spec_items = novel_spec_uls[0].find_all('li')
        num_chapters_span = None
        for li in novel_spec_items:
            if 'Available' in li.text or 'Translated' in li.text:
                num_chapters_span = li.find('span')
        num_chapters = int(num_chapters_span.get_text().strip('chapters').strip())
        total_toc_pages = (num_chapters + 24) // 25
        print(f'found {num_chapters} chapters')
        print(f'{total_toc_pages} toc pages')

        # Get TOC base URL
        footer_div = soup.find('div', {'class' : 'r-fullstory-chapters-foot'})
        links_a = footer_div.find_all('a')
        more_chapters = links_a[1]['href']
        if 'https://' not in more_chapters:
            more_chapters = f'https://ranobes.top{more_chapters}'

        # Load TOC
        self._driver.get(more_chapters)

        # Get all chapter URLs
        toc_page = 1
        chapterlist = list()
        while True:
            print(f'loading /page/{toc_page}')
            footer = self._driver.wait_for_class_name('page_next')
            toc_soup = BeautifulSoup(self._driver.page_source(), 'lxml')
            data = None
            for script in toc_soup.find_all('script'):
                if 'window.__DATA__' in script.text:
                    data = json.loads(script.text.strip().strip('window.__DATA__ = '))
                    break
            for chapter in data['chapters']:
                chapterlist.append(chapter['link'])
            toc_page = toc_page + 1
            if toc_page > total_toc_pages:
                break
            self._driver.get(more_chapters + f'page/{toc_page}/')
            time.sleep(1)

        return chapterlist[::-1]

    def get_chapter(self, url):
        self._driver.get(url)
        self._driver.wait_for_id('arrticle')
        return self._driver.page_source()
