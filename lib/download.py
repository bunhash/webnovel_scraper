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

def main(args):
    # Read URLs from stdin
    urls = list()
    for line in sys.stdin:
        urls.append(line.strip())
    
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
                with open(staging_file, 'wb') as ofile:
                    time.sleep(random.randrange(10, 200) / 100)
                    ofile.write(Parser.get_chapter(driver, urls[i]))

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
