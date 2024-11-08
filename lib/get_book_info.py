#!/usr/bin/python3
#
# @author bunhash
# @email bunhash@bhmail.me
#
# Grabs the Book's title, author, and chapter URLs
#

from driver import Driver
import os
import parsers
import sys

def main(args):
    # Variables
    title = str()
    author = str()
    url = str()
    chapters = list()
    write_bookinfo = False

    # Check arguments
    if len(args) == 0 and os.path.exists('bookinfo.txt'):
        with open('bookinfo.txt', 'r') as ifile:
            title = ifile.readline().strip()
            author = ifile.readline().strip()
            url = ifile.readline().strip()
    elif len(args) == 1:
        url = args[0]
        write_bookinfo = True

    # Ensure there's a URL
    if len(url) == 0:
        print('Usage:', sys.argv[0], '<URL>')
        return 1

    # Load the parser
    Parser = parsers.get_parser_by_url(url)

    # Create the driver and load the book page
    driver = Driver()
    Parser.load_book_page(driver, url)

    # Save title and author, if not saved.
    if write_bookinfo:
        title = Parser.get_title(driver)
        author = Parser.get_author(driver)

    # Parse all the chapter URLs
    chapters = Parser.get_chapterlist(driver)

    # Print details
    print('Title:', title)
    print('Author:', author)
    print('Chapters:', len(chapters))

    # Save everything
    if write_bookinfo:
        with open('bookinfo.txt', 'w') as ofile:
            ofile.write(f'{title}\n')
            ofile.write(f'{author}\n')
            ofile.write(f'{url}\n')
    with open('urlcache.txt', 'w') as ofile:
        for chapter_url in chapters:
            ofile.write(f'{chapter_url}\n')

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
