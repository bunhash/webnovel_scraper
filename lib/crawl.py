#!/usr/bin/python3
#
# @author bunhash
# @email bunhash@bhmail.me
#
# Downloads the chapters by crawling
#

from driver import Driver
import os
import random
import parsers
import sys
import time

def read_lines(filename):
    lines = list()
    with open(filename, 'r') as ifile:
        for line in ifile:
            line = line.strip()
            if not line: continue
            lines.append(line)
    return lines

def get_staging_file(url):
    filename = url.rstrip('/').rsplit("/", 1)[1]
    if not filename:
        raise Exception('no filename found')
    return os.path.join('staging', filename)

def main(args):
    if len(args) > 0:
        urls = args
    else:
        if not os.path.exists('urlcache.txt'):
            print('No urlcache.txt found', file=sys.stderr)
            sys.exit(1)

        # Read URLs from urlcache.txt
        urls = read_lines('urlcache.txt')
    
    # Create staging directory
    if not os.path.exists('staging'):
        os.mkdir('staging')

    if len(urls) > 0:
        # Load the parser
        Parser = parsers.get_parser_by_url(urls[0])

        # Load the driver
        driver = Driver()

        # Download everything we know about
        for url in urls:
            staging_file = get_staging_file(url)
            if os.path.exists(staging_file):
                print(f'Using cached {url}')
            else:
                print(f'Downloading {url}')
                time.sleep(random.randrange(10, 200) / 100)
                page = Parser.get_chapter(driver, url)
                with open(staging_file, 'wb') as ofile:
                    ofile.write(page)

        # Crawl to get the rest (redownload last page)
        try:
            cur_link = urls[-1]
            while cur_link:
                # Download the page
                time.sleep(random.randrange(10, 200) / 100)
                print(f'Downloading {cur_link}')
                cur_page = Parser.get_chapter(driver, cur_link)

                # Write the page
                staging_file = get_staging_file(cur_link)
                with open(staging_file, 'wb') as ofile:
                    ofile.write(cur_page)

                # Get next page
                next_link = Parser.next_page(cur_page)
                if next_link:
                    urls.append(next_link)

                # Set next link (could be None)
                cur_link = next_link
        finally:
            # Write the new urlcache.txt
            with open('urlcache.txt', 'w') as ofile:
                for url in urls:
                    ofile.write(f'{url}\n')

if __name__ == '__main__':
    main(sys.argv[1:])
