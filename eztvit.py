#!/usr/bin/env python
# encdoing: utf-8
import sys
import urllib2

import lxml.html

def showid_by_name():
    """
    Returns mapping of showID nad showName
    """
    tree = lxml.html.parse('http://eztv.it/')
    for _el in tree.xpath('//select[@name="SearchString"]/option'):
        yield(_el.get('value'), _el.text)

def torrents(showid):
    """
    Gets eztv.it showid
    Returns list with filename and torrent info
    """
    tree = lxml.html.parse('http://eztv.it/shows/%s/' % showid)
    for _tr in tree.xpath('//table[@class="forum_header_noborder"]/tr[@class="forum_header_border"]'):
        yield {'filename': _tr.xpath('td[2]/a/text()')[0],
               'torrents': _tr.xpath('td[3]/a/@href')}

