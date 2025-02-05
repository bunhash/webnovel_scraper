#!/usr/bin/env python3
#
# @author bunhash
# @email bunhash@bhmail.me
#
# Renames the staged files
#

from filemanager import UrlCache
import os
import shutil
import sys

def main(args):
    urls = UrlCache.read()
    for index in range(len(urls)):
        old_filename = UrlCache.get_filename(urls[index])
        new_filename = UrlCache.get_filename(urls[index], index=index)
        if os.path.exists(old_filename):
            print(f'Info: {old_filename} -> {new_filename}')
            shutil.move(old_filename, new_filename)
        else:
            print(f'Warning: could not find {old_filename}')

if __name__ == '__main__':
    main(sys.argv[1:])
