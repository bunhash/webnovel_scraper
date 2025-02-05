#!/usr/bin/env python3
#
# @author bunhash
# @email bunhash@bhmail.me
#
# Manages a client session
#

import httpx
import json
import urllib.parse

class Client:

    def __init__(self, solver='http://localhost:8191/v1', timeout=60000):
        self._solver = solver
        self._timeout = timeout
        self._session = None
        try:
            self._session = self._send_cmd({
                'cmd' : 'sessions.create',
                'maxTimeout' : self._timeout,
            })['session']
        except:
            raise Exception('failed to create session')

    def __del__(self):
        if self._session:
            _ = self._send_cmd({
                'cmd' : 'sessions.destroy',
                'session' : self._session
            })

    def _send_cmd(self, config, timeout=None):
        if not timeout:
            timeout = self._timeout
        headers = {'Content-Type': 'application/json'}
        res = httpx.post(url=self._solver, headers=headers, json=config, timeout=timeout)
        res_data = json.loads(res.text)
        if res_data['status'] != 'ok':
            message = res_data['message']
            raise Exception(f'{message}')
        return res_data

    def find_solution(self, url, timeout=None, config={}):
        if not timeout:
            timeout = self._timeout
        config['cmd'] = 'request.get'
        config['session'] = self._session
        config['url'] = url
        config['maxTimeout'] = timeout
        solution = self._send_cmd(config, timeout=timeout)['solution']
        status_code = solution['status']
        if status_code != 200:
            raise Exception(f'status code: {status_code}')
        return solution

    def get(self, url, timeout=None, config={}):
        if not timeout:
            timeout = self._timeout
        config['cmd'] = 'request.get'
        config['session'] = self._session
        config['url'] = url
        config['maxTimeout'] = timeout
        solution = self._send_cmd(config, timeout=timeout)['solution']
        status_code = solution['status']
        if status_code != 200:
            raise Exception(f'status code: {status_code}')
        return solution['response'].encode('utf-8', 'ignore')

    def post(self, url, postData={}, timeout=None, config={}):
        if not timeout:
            timeout = self._timeout
        config['cmd'] = 'request.get'
        config['session'] = self._session
        config['url'] = url
        config['maxTimeout'] = self._timeout
        config['postData'] = '&'.join([
            '{}={}'.format(
                urllib.parse.quote_plus(k),
                urllib.parse.quote_plus(data[k]),
            ) for k in data.keys()
        ])
        solution = self._send_cmd(config, timeout=timeout)['solution']
        status_code = solution['status']
        if status_code != 200:
            raise Exception(f'status code: {status_code}')
        return solution['response'].encode('utf-8', 'ignore')

class ProxyClient(Client):

    def __init__(self, proxy, solver='http://localhost:8191/v1', timeout=60000):
        super().__init__(solver=solver, timeout=timeout)
        self._proxy = proxy

    def get(self, url, timeout=None, config={}):
        config['proxy'] = self._proxy
        return super().get(url, timeout=timeout, config=config)

    def post(self, url, postData={}, timeout=None, config={}):
        config['proxy'] = self._proxy
        return super().post(url, postData=postData, timeout=timeout, config=config)
