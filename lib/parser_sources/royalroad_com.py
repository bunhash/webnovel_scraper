#!/usr/bin/python3
#
# @author bunhash
# @email bunhash@bhmail.me
#
# Parses royalroad.com novels
#

from bs4 import BeautifulSoup, NavigableString
from selenium.webdriver.common.by import By

COPYRIGHT_TRIGGER_LENGTH = 200
COPYRIGHT_TRIGGER_THRESHOLD = 8
COPYRIGHT_TRIGGERS = [
    # Big red flags
    ('amazon', 6),
    ('royal road', 6),

    # Actions
    ('lifted', 1),
    ('misappropriated', 2),
    ('pilfered', 2),
    ('report', 3),
    ('stolen', 2),
    ('support', 1),
    ('taken', 2),

    # Access wording
    ('authorization', 3),
    ('consent', 1),
    ('genuine', 2),
    ('illegal', 2),
    ('illicit', 3),
    ('infringe', 3),
    ('official', 1),
    ('original', 1),
    ('permission', 1),
    ('prefer', 1),
    ('unauthorized', 3),
    ('unlawful', 3),
    ('violation', 2),

    # Book synonyms
    ('content', 2),
    ('fiction', 2),
    ('instance', 1),
    ('narrative', 3),
    ('novel', 3),
    ('publication', 3),
    ('publish', 3),
    ('stories', 2),
    ('story', 2),
    ('tale', 2),
    ('text', 1),
    ('usage', 1),

    # Misc flags
    ('author', 1),
    ('creativ', 2),
    ('occurrence', 1),
    ('site', 3),
    ('platform', 2),
]

def is_copyright_phrase(el):
    """
    High enough success of catching annoying infringement phrases.

    I haven't noticed a false positive yet.
    """
    text = el.get_text().lower()
    if len(text) > COPYRIGHT_TRIGGER_LENGTH:
        return False
    flagged = 0
    for trigger, weight in COPYRIGHT_TRIGGERS:
        if trigger in text:
            flagged = flagged + weight
    return flagged >= COPYRIGHT_TRIGGER_THRESHOLD

class Parser:

    @staticmethod
    def parse_book_info(html):
        soup = BeautifulSoup(html, 'lxml')
        story_div = soup.find('div', {'class' : 'fic-title'})
        title_h1 = story_div.find('h1')
        spans = story_div.find_all('span')
        author_span = spans[1]

        title = title_h1.text.strip()
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
        chapter = soup.find('div', {'class' : 'chapter-content'})
        if not chapter:
            raise Exception('could not find chapter')

        # Parse title
        title = '???'
        title_el = soup.find('h1')
        if title_el:
            title = title_el.text.strip()

        # Get the reading content
        paragraphs = list()
        for p in chapter.find_all('p'):
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
            if not is_copyright_phrase(p):
                chapter.body.append(p)
            #else:
            #    print(f'found: {p.text}')
        
        # Return chapter title and chapter html
        return title.encode('utf-8', errors='ignore'), chapter.encode('utf-8', errors='ignore')

    @staticmethod
    def next_page(html):
        soup = BeautifulSoup(html, 'lxml')
        nav_el = soup.find('div', {'class' : 'nav-buttons'})
        if nav_el:
            links = nav_el.find_all('a')
            if links and 'Next' in links[-1].text:
                url = links[-1]['href']
                if 'https://' not in url:
                    return f'https://www.royalroad.com{url}'
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
        if b'chapter-content' in res:
            return res
        raise Exception('No chapter found')

class SeleniumParser(Parser):

    def __init__(self, driver):
        self._driver = driver

    def get_book_info_page(self, url):
        self._driver.get(url)
        _ = self._driver.wait_for_class_name('fic-title')
        _ = self._driver.wait_for_id('chapters')
        return self._driver.page_source()

    def get_chapterlist(self, url, html):
        if self._driver.current_url() != url:
            self._driver.get(url)

        chapterlist = list()
        while True:

            # Get all chapters on the page
            chapter_tab = self._driver.wait_for_id('chapters')
            tbody = chapter_tab.find_element(By.TAG_NAME, 'tbody')
            for row in tbody.find_elements(By.TAG_NAME, 'tr'):
                link = row.find_element(By.TAG_NAME, 'a')
                chapterlist.append(link.get_attribute('href'))

            # Go to next page
            navigation_bar = self._driver.wait_for_class_name('pagination-small')
            arrows = navigation_bar.find_elements(By.CLASS_NAME, 'nav-arrow')
            if len(arrows) == 2:
                arrows[1].click()
            else:
                try:
                    right_arrow = arrows[0].find_element(By.CLASS_NAME, 'fa-chevron-right')
                    right_arrow.click()
                except:
                    break

        return chapterlist

    def get_chapter(self, url):
        self._driver.get(url)
        _ = self._driver.wait_for_class_name('chapter-content')
        return self._driver.page_source()
