#!/usr/bin/env python3
#
# @author bunhash
# @email bunhash@bhmail.me
#
# Parsers
#

import enum
import importlib
import urllib.parse

PARSERS = {
    'www.ranobes.top' : 'ranobes_top',
    'ranobes.top' : 'ranobes_top',
    'www.royalroad.com' : 'royalroad_com',
    'royalroad.com' : 'royalroad_com',
    'www.scribblehub.com' : 'scribblehub_com',
    'scribblehub.com' : 'scribblehub_com',
}

class UnknownDomain(Exception):
    def __init__(self, domain):
        super().__init__(f'Unknown domain {domain}')

class ParserType(enum.Enum):
    PARSER = 1
    SELENIUM = 2
    SOLVERR = 3

def get_parser_by_name(name, parser_type=ParserType.PARSER):
    parser_mod = importlib.import_module('parser_sources.{}'.format(name), 'parser_sources')
    if parser_type == ParserType.PARSER:
        return parser_mod.Parser
    elif parser_type == ParserType.SELENIUM:
        return parser_mod.SeleniumParser
    elif parser_type == ParserType.SOLVERR:
        return parser_mod.SolverParser
    return None

def get_parser_by_domain(domain, parser_type=ParserType.PARSER):
    if domain not in PARSERS:
        raise UnknownDomain(domain)
    return get_parser_by_name(PARSERS[domain], parser_type=parser_type)

def get_parser_by_url(url, parser_type=ParserType.PARSER):
    url_info = urllib.parse.urlparse(url)
    domain = url_info.netloc
    if ':' in domain:
        domain = domain.split(':')[0]
    return get_parser_by_domain(domain, parser_type=parser_type)
