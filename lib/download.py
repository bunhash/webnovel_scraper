#!/usr/bin/env python3
#
# @author bunhash
# @email bunhash@bhmail.me
#
# Downloads the chapters
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
    # Check command line arguments
    if args.threads > 1 and args.selenium:
        print('Selenium mode does not support multiple threads', file=sys.stderr)
        sys.exit(1)

    # Read URLs
    urls = UrlCache.read()
    
    # Create staging directory
    if not os.path.exists(UrlCache.directory):
        os.mkdir(UrlCache.directory)

    if len(urls) > 0:
        # Load the parser
        if args.selenium:
            Parser = parsers.get_parser_by_url(urls[0], parsers.ParserType.SELENIUM)
            Downloader(Parser(Driver()), urls).start()
        else:
            if args.threads or args.proxies:
                MultiDownloader(
                    urls,
                    args.flaresolverr,
                    threads=2, # Flaresolver has a queue of 4 -- 2 seems to work for ranobes
                    useproxies=args.proxies
                ).start()
            else:
                Parser = parsers.get_parser_by_url(urls[0], parsers.ParserType.SOLVERR)
                Downloader(Parser(Client(solver=args.flaresolverr)), urls).start()

class Downloader:

    def __init__(self, client, urls):
        self._client = client
        self._urls = urls
        self._total = len(urls)

    def _download(self, index, staging_file, attempts=3):
        for _ in range(attempts):
            try:
                print('({:4d}/{:4d}) Downloading {}'.format(index + 1, self._total, self._urls[index]))
                page = self._client.get_chapter(self._urls[index])
                with open(staging_file, 'wb') as ofile:
                    ofile.write(page)
                return
            except KeyboardInterrupt as e:
                raise e
            except Exception as e:
                print('({:4d}/{:4d}) Error downloading {}'.format(index + 1, self._total, self._urls[index]))

    def start(self, maxattempts=3):
        for i in range(self._total):
            staging_file = UrlCache.get_filename(self._urls[i], index=i)
            if os.path.exists(staging_file):
                print('({:4d}/{:4d}) Using cached'.format(i + 1, self._total), self._urls[i])
            else:
                time.sleep((random.random() * 1.5) + 0.5)
                self._download(i, staging_file, attempts=maxattempts)

class MultiDownloader:

    @staticmethod
    def _download(clients, client, url, index, total, staging_file, Parser, solver, useproxies, proxylist, attempts):
        for _ in range(attempts):
            try:
                page = client.get_chapter(url)
                with open(staging_file, 'wb') as ofile:
                    ofile.write(page)
                clients.put(client)
                return
            except KeyboardInterrupt as e:
                raise e
            except Exception as e:
                if useproxies:
                    client = Parser(ProxyClient(proxylist.random_proxy(), solver=solver))
        print('({:4d}/{:4d}) Failed to download'.format(index + 1, total), url)
        clients.put(client)

    def __init__(self, urls, solver, threads=5, useproxies=False):
        assert(len(urls) > 0)
        self._urls = urls
        self._total = len(urls)
        self._maxthreads = threads
        self._useproxies = useproxies
        self._proxylist = None
        self._Parser = parsers.get_parser_by_url(urls[0], parsers.ParserType.SOLVERR)
        self._solver = solver
        self._clients = queue.Queue()
        for _ in range(threads):
            if useproxies:
                self._proxylist = proxies.ProxyList()
                self._clients.put(self._Parser(ProxyClient(
                    self._proxylist.random_proxy(), solver=self._solver
                )))
            else:
                self._clients.put(self._Parser(Client(solver=self._solver)))
        self._threads = list()

    def _clean_threads(self, wait=False):
        for t in self._threads:
            if wait or not t.is_alive():
                try:
                    t.join()
                    self._threads.remove(t)
                except Exception as e:
                    pass

    def start(self, maxattempts=5):
        for i in range(self._total):
            staging_file = UrlCache.get_filename(self._urls[i], index=i)
            if os.path.exists(staging_file):
                print('({:4d}/{:4d}) Using cached'.format(i + 1, self._total), self._urls[i])
            else:
                print('({:4d}/{:4d}) Downloading'.format(i + 1, self._total), self._urls[i])
                self._clean_threads()
                while True:
                    try:
                        client = self._clients.get(True, 0.1)
                        t = threading.Thread(
                            target=MultiDownloader._download, args=(
                                self._clients,
                                client,
                                self._urls[i],
                                i,
                                self._total,
                                staging_file,
                                self._Parser,
                                self._solver,
                                self._useproxies,
                                self._proxylist,
                                maxattempts,
                            )
                        )
                        self._threads.append(t)
                        t.start()
                        break
                    except queue.Empty:
                        continue
        self._clean_threads(wait=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='download', description='downloads chapters')
    parser.add_argument('-s', '--selenium', action='store_true', default=False, help='use local selenium driver')
    parser.add_argument('-f', '--flaresolverr', type=str, metavar='SOLVER', default='http://localhost:8191/v1', help='use flaresolverr server (default)')
    parser.add_argument('-t', '--threads', action='store_true', default=False, help='run multiple threads')
    parser.add_argument('-p', '--proxies', action='store_true', default=False, help='use proxies with multiple threads')
    main(parser.parse_args())
