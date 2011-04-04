#!/usr/bin/env python
# encoding: utf-8

import ConfigParser
import urllib2
import sys
import time
import pprint

import eztvit

def proceed_with_show(show):
    eztvit_id = None
    if show.get('eztvit_name'):
        eztvit_id = eztvit.showid_by_name(show.get('eztvit_name'))
    else:
        eztvit_id = eztvit.showid_by_name(show['human_name'])

    all_torrents = eztvit.torrents(eztvit_id)
    while True:
        try:
            eztv_espisode = all_torrents.next()
        except IOError:
            print "Error loading torrents for", show['human_name']
            print "Got error. Sleeping..."
            time.sleep(10)
            try:
                eztv_espisode = all_torrents.next()
            except StopIteration:
                break
        except StopIteration:
            break

        show_name, season, episode = eztvit.episodeinfo_from_filename(eztv_espisode['filename'])
        #print u"Got %s S%s E%s => S%s E%s" % (show_name, season, episode, int(show.get('season')), int(show.get('episode')) )
        if int(season) > int(show.get('season')):
            # in case season is changed, reset episode count
            show['episode'] = 0

        if int(season) >= int(show.get('season')) and \
           int(episode) > int(show.get('episode')):
               for t_url in eztv_espisode['torrents']:
                   out_fn = "%s/%s %sx%s.torrent" % (out_dir, show['human_name'], season, episode)
                   print "Downloading", show_name, season, episode, "to", out_fn
                   try:
                       data = urllib2.urlopen(t_url)
                   except urllib2.URLError:
                       print "Error loading '%s'" % t_url
                       print sys.exc_info()
                       continue

                   open(out_fn, 'wb').write(data.read())

                   # hack to get file mimetype.
                   # if it is not BitTorrent assuming it is Not Found
                   import subprocess
                   mimetype=subprocess.Popen(['file', '-b', out_fn],
                           stdout=subprocess.PIPE).communicate()[0].strip()
                   if mimetype == 'BitTorrent file':
                       print "OK. Torrent mime type:", mimetype
                       return (season, episode)
                   else:
                       print "Error. Torrent mime type:", mimetype


if __name__ == "__main__":
    if len(sys.argv) <= 2:
        print "Usage: %s <config> <out torrents dir>" % sys.argv[0]
        sys.exit(1)
    config_fn, out_dir = sys.argv[1:3]

    shows = []
    if len(sys.argv) == 4:
        shows = sys.argv[3:]

    config = ConfigParser.ConfigParser()
    config.read(config_fn)

    # Validate all tvshow names in the config file
    for section in config.sections():
        show = dict(config.items(section))

        if show.get('eztvit_ignore'):
            continue

        if show.get('eztvit_name'):
            eztvit_id = eztvit.showid_by_name(show.get('eztvit_name'))
        else:
            eztvit_id = eztvit.showid_by_name(show['human_name'])


    # Download next episodes
    for section in config.sections():
        show = dict(config.items(section))
        pprint.pprint(show)

        # in case we need only selected show, skip all others
        if shows and show['human_name'].lower() not in shows:
            continue

        if show.get('eztvit_ignore'):
            continue

        if show.get('show_type') == 'seasonepisode':
            got_new = proceed_with_show(show)
            if got_new:
                print "OK", got_new
                config.set(section, "season", got_new[0])
                config.set(section, "episode", got_new[1])
        else:
            print "Unknwn show type", show.get('show_type')
        print "-"*40

    config_f = open(config_fn, 'w')
    config.write(config_f)
    config_f.close()

