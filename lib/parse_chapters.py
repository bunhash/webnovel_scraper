#!/usr/bin/python3
#
# @author bunhash
# @email bunhash@bhmail.me
#
# Parses the downloaded chapter
#

import sys
import os
import multiprocessing
import parsers

def main(args):

    if not os.path.exists('book'):
        os.mkdir('book')

    pool = multiprocessing.Pool(processes=20)
    jobs = list()
    try:
        # Create the parsing jobs
        count = 0
        for line in sys.stdin:
            url = line.strip()
            if not url:
                continue
            count = count + 1
            raw_filename = os.path.join('staging', url.rstrip('/').split('/')[-1])
            if not raw_filename:
                print('Bad raw_filename:', url, file=sys.stderr)
                continue
            if not os.path.exists(raw_filename):
                print('File does not exist:', raw_filename, file=sys.stderr)
                continue
            parsed_filename = os.path.join('book', '{:04d}.html'.format(count))
            Parser = parsers.get_parser_by_url(url)
            jobs.append((raw_filename, pool.apply_async(parse, (Parser, url, raw_filename, parsed_filename))))
        pool.close()

        # Complete the parsing jobs
        with open('chapterlist.txt', 'w') as ofile:
            total = len(jobs)
            for i in range(total):
                raw, res = jobs[i]
                print('({:4d}/{:4d}) Parsing'.format(i + 1, total), raw)
                try:
                    ofname, ctitle = res.get(timeout=None)
                    ofile.write('{} {}\n'.format(ofname, ctitle))
                except KeyboardInterrupt as e:
                    raise e
                except Exception as e:
                    print(e)

    except KeyboardInterrupt:
        pool.terminate()
        pool.join()

def parse(Parser, url, ifname, ofname):
    try:
        with open(ifname, 'rb') as ifile:
            ctitle, chapter = Parser.parse_chapter(ifile.read())
            ctitle = ctitle.decode('ascii', errors='ignore')
            with open(ofname, 'wb') as ofile:
                ofile.write(chapter)
            return ofname, ctitle
    except KeyboardInterrupt as e:
        raise e
    except Exception as e:
        raise Exception('Error parsing {}->{}: {}'.format(ifname, ofname, e))

if __name__ == '__main__':
    main(sys.argv[1:])
