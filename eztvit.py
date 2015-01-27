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


def showid_by_name(name):
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
        tree = lxml.html.fromstring(open_url('http://eztv.ch/'))
        for _el in tree.xpath('//select[@name="SearchString"]/option'):
            if _el.get('value'):
                result.append((_el.get('value'), _el.text))
        SHOWS_MAP_CACHED = result
    return SHOWS_MAP_CACHED


def open_url(url):
    headers = { 'User-Agent' : 'Mozilla/5.0' }
    req = urllib2.Request(url, None, headers)
    html = urllib2.urlopen(req).read()
    return html


def torrents_from_url(url):
    """
    Returns list with filename and torrent info from eztv URL

    Throws IOError in case you have problem loading the page
    """
    tree = lxml.html.fromstring(open_url(url))

    for _tr in tree.xpath('//table[@class="forum_header_noborder"]/tr[@class="forum_header_border"]'):
        yield {'filename': _tr.xpath('td[2]/a/text()')[0],
               'torrents': _tr.xpath('td[3]/a/@href')}


def torrents(showid):
    """
    Gets eztv.ch showid
    Returns list with filename and torrent info

    Throws IOError in case you have problem loading the page
    """
    tree = lxml.html.fromstring(open_url('http://eztv.ch/shows/%s/' % showid))

    for _tr in tree.xpath('//table[@class="forum_header_noborder"]/tr[@class="forum_header_border"]'):
        yield {'filename': _tr.xpath('td[2]/a/text()')[0],
               'torrents': _tr.xpath('td[3]/a/@href')}


def main_based_on_name():
    import pprint
    name = sys.argv[1]
    showid = showid_by_name(name)
    for v in torrents(showid):
        for __t in v['torrents']:
            print "wget '%s' -O '%s.torrent'" % (__t, v['filename'])


if __name__ == "__main__":
    import pprint
    url = sys.argv[1]  # http://eztv.ch/shows/36/breaking-bad/
    url_pat = re.compile(ur"shows\/(\d+)\/(.+)\/")
    m = url_pat.search(url)
    if m:
        show_id, show_name = m.groups()
    else:
        print "Usage: %s http://eztv.ch/shows/36/breaking-bad/" % sys.argv[0]
        sys.exit(1)

    #for v in torrents(show_id):
    for v in torrents_from_url(url):
        for __t in v['torrents']:
            if __t.find("magnet:") > -1:
                try:
                    print "%s;%s;%s" % (__t, v['filename'], episodeinfo_from_filename(v['filename']) )
                except ValueError:
                    print "no episode in filename=" + v.get('filename')


