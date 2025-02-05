#!/usr/bin/env python3
#
# @author bunhash
# @email bunhash@bhmail.me
#
# Manages the file caches
#

import os

class BookInfo:

    filename = 'bookinfo.txt'

    @staticmethod
    def check_file():
        if not os.path.exists(BookInfo.filename):
            raise Exception('No urlcache.txt found')

    @staticmethod
    def read():
        BookInfo.check_file()
        with open(BookInfo.filename, 'r') as ifile:
            title = ifile.readline().strip()
            author = ifile.readline().strip()
            url = ifile.readline().strip()
        return title, author, url

    @staticmethod
    def write(title, author, url):
        with open(BookInfo.filename, 'w') as ofile:
            ofile.write(f'{title}\n')
            ofile.write(f'{author}\n')
            ofile.write(f'{url}\n')

class UrlCache:

    filename = 'urlcache.txt'
    directory = 'staging'

    @staticmethod
    def check_file():
        if not os.path.exists(UrlCache.filename):
            raise Exception('No urlcache.txt found')

    @staticmethod
    def read():
        UrlCache.check_file()
        urls = list()
        with open(UrlCache.filename, 'r') as ifile:
            for line in ifile:
                line = line.strip()
                if not line: continue
                urls.append(line)
        return urls

    @staticmethod
    def write(urls):
        with open(UrlCache.filename, 'w') as ofile:
            for url in urls:
                ofile.write(f'{url}\n')

    @staticmethod
    def get_filename(url, index=None):
        filename = url.rstrip('/').rsplit("/", maxsplit=1)[1]
        if not filename:
            raise Exception('no filename found')
        if index != None:
            filename = f'{index:04d}-{filename}'
        return os.path.join(UrlCache.directory, filename)

class ChapterList:

    filename = 'chapterlist.txt'
    directory = 'book'

    @staticmethod
    def check_file():
        if not os.path.exists(ChapterList.filename):
            raise Exception('No chapterlist.txt found')

    @staticmethod
    def read():
        ChapterList.check_file()
        chapters = list()
        with open(ChapterList.filename, 'r') as ifile:
            for line in ifile:
                line = line.strip()
                if not line: continue
                filename, ctitle = line.split(' ', maxsplit=1)
                chapters.append((filename, ctitle))
        return chapters

    @staticmethod
    def write(chapters):
        with open(ChapterList.filename, 'w') as ofile:
            for filename, title in chapters:
                try:
                    ofile.write(f'{filename} {title}\n')
                except:
                    title = title.encode('utf-8').decode('ascii', errors='ignore')
                    ofile.write(f'{filename} {title}\n')
