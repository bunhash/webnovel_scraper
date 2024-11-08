#!/usr/bin/python3
#
# @author bunhash
# @email bunhash@bhmail.me
#
# Parsers
#

import importlib
import urllib.parse

PARSERS = {
    'www.ranobes.top' : 'ranobes_top',
    'ranobes.top' : 'ranobes_top',
}

class UnknownDomain(Exception):
    def __init__(self, domain):
        super().__init__(f'Unknown domain {domain}')

def get_parser_by_name(name):
    parser_mod = importlib.import_module('parser_sources.{}'.format(name), 'parser_sources')
    return parser_mod.Parser

def get_parser_by_domain(domain):
    if domain not in PARSERS:
        raise UnknownDomain(domain)
    return get_parser_by_name(PARSERS[domain])

def get_parser_by_url(url):
    url_info = urllib.parse.urlparse(url)
    domain = url_info.netloc
    if ':' in domain:
        domain = domain.split(':')[0]
    return get_parser_by_domain(domain)
