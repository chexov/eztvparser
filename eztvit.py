#!/usr/bin/env python
# encdoing: utf-8
import sys
import urllib2
import re

import lxml.html


PAT_EPISODEINFO = [re.compile(ur"^(.+)[\t\s]*s(\d\d)e(\d\d)"),
                   re.compile(ur"^(.+)[\s\t](\d+)x(\d+)"),
                   ]

global SHOWS_MAP_CACHED
SHOWS_MAP_CACHED = []

def episodeinfo_from_filename(filename):
    filename = filename.lower()
    for episodeinfo in PAT_EPISODEINFO:
        match = episodeinfo.search(filename)
        if match:
            result = match.groups()
            return result[0].strip(), int(result[1]), int(result[2])
    raise ValueError(u"Could not get episode and season info from '%s'" % filename)


def showid_by_name(name=None):
    """
    Returns eztv show id if there is a 100% match by show title
    OR throw ValueError
    """
    result = filter(lambda kv: name.lower() == kv[1].lower(), shows_map())
    if result and len(result) == 1:
        return result[0][0]
    else:
        raise ValueError(u"TVShow '%s' not found" % name)


def shows_map(nocache=False):
    """
    Returns mapping of showID nad showName
    """
    global SHOWS_MAP_CACHED
    if not SHOWS_MAP_CACHED or nocache:
        result = []
        tree = lxml.html.parse('http://eztv.it/')
        for _el in tree.xpath('//select[@name="SearchString"]/option'):
            if _el.get('value'):
                result.append((_el.get('value'), _el.text))
        SHOWS_MAP_CACHED = result
    return SHOWS_MAP_CACHED



def torrents(showid):
    """
    Gets eztv.it showid
    Returns list with filename and torrent info

    Throws IOError in case you have problem loading the page
    """
    tree = lxml.html.parse('http://eztv.it/shows/%s/' % showid)

    for _tr in tree.xpath('//table[@class="forum_header_noborder"]/tr[@class="forum_header_border"]'):
        yield {'filename': _tr.xpath('td[2]/a/text()')[0],
               'torrents': _tr.xpath('td[3]/a/@href')}


if __name__ == "__main__":
    import pprint
    name = sys.argv[1]
    showid = showid_by_name(name)
    for v in torrents(showid):
        pprint.pprint(v)

