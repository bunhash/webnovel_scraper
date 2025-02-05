#!/usr/bin/env python3
#
# @author bunhash
# @email bunhash@bhmail.me
#
# Parses the downloaded chapter
#

from filemanager import UrlCache, ChapterList
import sys
import os
import multiprocessing
import parsers

def main(args):
    urls = UrlCache.read()

    if not os.path.exists(ChapterList.directory):
        os.mkdir(ChapterList.directory)

    pool = multiprocessing.Pool(processes=20)
    jobs = list()
    try:
        # Create the parsing jobs
        count = 0
        for url in urls:
            count = count + 1
            raw_filename = UrlCache.get_filename(url, index=(count - 1))
            if not os.path.exists(raw_filename):
                print('File does not exist:', raw_filename, file=sys.stderr)
                continue
            parsed_filename = os.path.join(ChapterList.directory, f'{count:04d}.html')
            Parser = parsers.get_parser_by_url(url)
            jobs.append((raw_filename, pool.apply_async(parse, (Parser, url, raw_filename, parsed_filename))))
        pool.close()

        # Complete the parsing jobs
        chapters = list()
        total = len(jobs)
        for i in range(total):
            raw, res = jobs[i]
            print('({:4d}/{:4d}) Parsing'.format(i + 1, total), raw)
            try:
                filename, title = res.get(timeout=None)
                chapters.append((filename, title))
            except KeyboardInterrupt as e:
                raise e
            except Exception as e:
                print(e)

        # Write chapterlist
        ChapterList.write(chapters)

    except KeyboardInterrupt:
        pool.terminate()
        pool.join()

def parse(Parser, url, ifname, ofname):
    try:
        with open(ifname, 'rb') as ifile:
            ctitle, chapter = Parser.parse_chapter(ifile.read())
            ctitle = ctitle.decode('utf-8', errors='ignore')
            with open(ofname, 'wb') as ofile:
                ofile.write(chapter)
            return ofname, ctitle
    except KeyboardInterrupt as e:
        raise e
    except Exception as e:
        raise Exception(f'Error parsing {ifname}->{ofname}: {e}')

if __name__ == '__main__':
    main(sys.argv[1:])
