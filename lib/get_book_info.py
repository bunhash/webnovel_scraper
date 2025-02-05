#!/usr/bin/env python3
#
# @author bunhash
# @email bunhash@bhmail.me
#
# Grabs the Book's title, author, and chapter URLs
#

from client import Client
from driver import Driver
from filemanager import BookInfo, UrlCache

import argparse
import os
import parsers
import sys

def main(args):
    title = str()
    author = str()
    url = str()
    urls = list()
    write_bookinfo = False

    if args.url:
        url = args.url
        write_bookinfo = True
    else:
        title, author, url = BookInfo.read()

    # Ensure there's a URL
    if len(url) == 0:
        print('Usage:', sys.argv[0], '<URL>')
        sys.exit(1)

    # Load the parser
    Parser = None
    client = None
    if args.solver:
        Parser = parsers.get_parser_by_url(url, parsers.ParserType.SOLVERR)
        client = Parser(Client())
    else:
        Parser = parsers.get_parser_by_url(url, parsers.ParserType.SELENIUM)
        client = Parser(Driver())

    # Load the book info page
    page = client.get_book_info_page(url)

    # Save title and author, if not saved.
    if write_bookinfo:
        title, author = Parser.parse_book_info(page)

    # Parse all the chapter URLs
    urls = client.get_chapterlist(url, page)

    # Print details
    print('Title:', title)
    print('Author:', author)
    print('Chapters:', len(urls))

    # Save everything
    if write_bookinfo:
        BookInfo.write(title, author, url)
    UrlCache.write(urls)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='info', description='fetches webnovel information')
    parser.add_argument('-s', '--solver', action='store_true', default=False, help='use flaresolver instead of selenium driver')
    parser.add_argument('-f', '--flaresolverr', type=str, metavar='SOLVER', default='http://localhost:8191/v1', help='use flaresolverr server')
    parser.add_argument('url', nargs='?', metavar='URL', help='URL of the webnovel')
    main(parser.parse_args())
