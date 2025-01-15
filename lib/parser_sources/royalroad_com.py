#!/usr/bin/python3
#
# @author bunhash
# @email bunhash@bhmail.me
#
# Parses royalroad.com novels
#

from bs4 import BeautifulSoup, NavigableString
from selenium.webdriver.common.by import By

class Parser:

    @staticmethod
    def load_book_page(driver, url):
        driver.get(url)

    @staticmethod
    def get_title(driver):
        story_div = driver.wait_for_class_name('fic-title')
        title_h1 = story_div.find_element(By.XPATH, './/div/h1')
        return title_h1.text.strip()

    @staticmethod
    def get_author(driver):
        story_div = driver.wait_for_class_name('fic-title')
        author_span = story_div.find_element(By.XPATH, './/div/h4/span[2]')
        return author_span.text.strip()

    @staticmethod
    def get_chapterlist(driver):
        chapterlist = list()
        while True:

            # Get all chapters on the page
            chapter_tab = driver.wait_for_id('chapters')
            tbody = chapter_tab.find_element(By.TAG_NAME, 'tbody')
            for row in tbody.find_elements(By.TAG_NAME, 'tr'):
                link = row.find_element(By.TAG_NAME, 'a')
                chapterlist.append(link.get_attribute('href'))

            # Go to next page
            navigation_bar = driver.wait_for_class_name('pagination-small')
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

    @staticmethod
    def get_chapter(driver, url):
        driver.get(url)
        content = driver.wait_for_class_name('chapter-page')
        return content.get_attribute('innerHTML').encode('utf-8')

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
            chapter.body.append(p)
        
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
