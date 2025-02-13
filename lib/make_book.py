#!/usr/bin/env python3
#
# @author bunhash
# @email bunhash@bhmail.me
#
# Makes the EPUB from the parsed chapters
#

from filemanager import BookInfo, ChapterList
from ebooklib import epub
import os
import subprocess
import sys
import uuid

def main(args):
    # Get the title and author
    title, author, _ = BookInfo.read()

    # Get the chapter info
    chapter_info = ChapterList.read()

    # Get the cover image
    cover_img = None
    if os.path.exists('cover.jpg'):
        with open('cover.jpg', 'rb') as ifile:
            cover_img = ifile.read()

    # Build the EPUB
    print('Title:', title)
    print('Author:', author)
    print('Chapters:', len(chapter_info))
    print('Building epub ...')
    build_epub(title, author, chapter_info, cover_img=cover_img)
    print('Complete')

# Define css style
CSS_STYLE = """
@namespace epub "http://www.idpf.org/2007/ops";
body {
    font-family: Cambria, Liberation Serif, Bitstream Vera Serif, Georgia, Times, Times New Roman, serif;
}
h2 {
    text-align: left;
    text-transform: uppercase;
    font-weight: 200;     
}
ol {
    list-style-type: none;
}
ol > li:first-child {
    margin-top: 0.3em;
}
    nav[epub|type~='toc'] > ol > li > ol  {
    list-style-type:square;
}
    nav[epub|type~='toc'] > ol > li > ol > li {
    margin-top: 0.3em;
}
"""

def build_epub(title, author, chapter_info, cover_img=None, gen_toc=True):

    # Create book object
    book = epub.EpubBook()

    # Set the metadata
    book.set_identifier(str(uuid.uuid1()))
    book.set_title(title)
    book.set_language('en')
    book.add_author(author)

    # Set the cover
    if cover_img:
        book.set_cover('image.jpg', cover_img)

    # Add css file
    nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=CSS_STYLE)
    book.add_item(nav_css)

    # Create spine, add cover page as first page
    book.spine = ['cover', 'nav']
    if gen_toc: book.toc = list()

    # Add the chapters
    for filename, ctitle in chapter_info:
        chapter = epub.EpubHtml(title=ctitle, file_name='{}.xhtml'.format(filename.rstrip('.html')))
        with open(filename, 'rb') as ifile:
            chapter.set_content(ifile.read())
        book.add_item(chapter)
        if gen_toc: book.toc.append(chapter)
        book.spine.append(chapter)

    # Add navigation
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # create epub file
    epub.write_epub('{}.epub'.format(title), book, {})
    if os.name == 'nt':
        subprocess.run(['ebook-convert.exe', '{}.epub'.format(title), '{}.azw3'.format(title), '--no-inline-toc'], shell=True, check=True)

if __name__ == '__main__':
    main(sys.argv[1:])
