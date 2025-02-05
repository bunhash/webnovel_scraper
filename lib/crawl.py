#!/usr/bin/env python3
#
# @author bunhash
# @email bunhash@bhmail.me
#
# Downloads the chapters by crawling
#

from client import Client, ProxyClient
from driver import Driver
from filemanager import UrlCache

import argparse
import os
import parsers
import proxies
import queue
import random
import sys
import threading
import time

def main(args):
    # Read URLs
    urls = UrlCache.read()
    
    # Create staging directory
    if not os.path.exists(UrlCache.directory):
        os.mkdir(UrlCache.directory)

    if len(urls) > 0:
        # Load the parser
        if args.selenium:
            Parser = parsers.get_parser_by_url(urls[0], parsers.ParserType.SELENIUM)
            Crawler(Parser, Parser(Driver()), urls).start()
        else:
            Parser = parsers.get_parser_by_url(urls[0], parsers.ParserType.SOLVERR)
            Crawler(Parser, Parser(Client(solver=args.flaresolverr)), urls).start()

class Crawler:

    def __init__(self, Parser, client, urls):
        self._Parser = Parser
        self._client = client
        self._urls = urls

    def _download(self, count, url, staging_file, attempts=3):
        for _ in range(attempts):
            try:
                print('({:4d}) Downloading {}'.format(count, url))
                page = self._client.get_chapter(url)
                with open(staging_file, 'wb') as ofile:
                    ofile.write(page)
                return page
            except KeyboardInterrupt as e:
                raise e
            except Exception as e:
                print('({:4d}) Error downloading {}'.format(count, url))

    def start(self, maxattempts=3):
        count = 0
        for url in self._urls:
            count = count + 1
            staging_file = UrlCache.get_filename(url, index=(count - 1))
            if os.path.exists(staging_file):
                print('({:4d}) Using cached {}'.format(count, url))
            else:
                time.sleep((random.random() * 1.5) + 0.5)
                _ = self._download(count, url, staging_file, attempts=maxattempts)
        try:
            url = self._urls[-1]
            while url:
                time.sleep((random.random() * 1.5) + 0.5)
                page = self._download(count, url, UrlCache.get_filename(url, index=(count - 1)), attempts=maxattempts)

                # Get next page
                next_url = self._Parser.next_page(page)
                if next_url:
                    self._urls.append(next_url)

                # Set next link (could be None)
                url = next_url
                count = count + 1
        finally:
            UrlCache.write(self._urls)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='crawl', description='downloads chapters by crawling')
    parser.add_argument('-s', '--selenium', action='store_true', default=False, help='use local selenium driver')
    parser.add_argument('-f', '--flaresolverr', type=str, metavar='SOLVER', default='http://localhost:8191/v1', help='use flaresolverr server (default)')
    main(parser.parse_args())
