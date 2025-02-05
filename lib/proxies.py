#!/usr/bin/env python3
#
# @author bunhash
# @email bunhash@bhmail.me
#
# Handles proxy servers
#

import httpx
import json
import random

class ProxyList:

    def __init__(self):
        hclient = httpx.Client(http2=True)
        res = hclient.get('https://api.proxyscrape.com/v4/free-proxy-list/get', params={
            'request' : 'display_proxies',
            'proxy_format' : 'protocolipport',
            'anonymity' : 'Elite',
            'format' : 'json',
        })
        if res.status_code != 200:
            raise Exception('failed to fetch proxies')
        self.proxies = json.loads(res.read())['proxies']

    def random_proxy(self):
        random.choice(self.proxies)['proxy']
