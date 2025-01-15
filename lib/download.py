#!/usr/bin/python3
#
# @author bunhash
# @email bunhash@bhmail.me
#
# Downloads the chapters
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

def main(args):
    if not os.path.exists('urlcache.txt'):
        print('No urlcache.txt found', file=sys.stderr)
        sys.exit(1)

    # Read URLs from urlcache.txt
    urls = read_lines('urlcache.txt')
    
    # Create staging directory
    if not os.path.exists('staging'):
        os.mkdir('staging')

    # Load the parser
    if len(urls) > 0:
        Parser = parsers.get_parser_by_url(urls[0])

        # Load the driver
        driver = Driver()

        # Download everything
        total = len(urls)
        for i in range(total):
            print('({:4d}/{:4d}) Downloading'.format(i + 1, total), urls[i])
            filename = urls[i].rstrip('/').rsplit("/", 1)[1]
            if not filename:
                raise Exception('no filename found')
            staging_file = os.path.join('staging', filename)
            if not os.path.exists(staging_file):
                time.sleep(random.randrange(10, 200) / 100)
                page = Parser.get_chapter(driver, urls[i])
                with open(staging_file, 'wb') as ofile:
                    ofile.write(page)

if __name__ == '__main__':
    main(sys.argv[1:])
