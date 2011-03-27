#!/usr/bin/env python
# encoding: utf-8

import ConfigParser
import urllib2

import eztvit

config = ConfigParser.ConfigParser()
config.read('config')

for section in config.sections():
    show = dict(config.items(section))

    if show.get('show_type') == 'seasonepisode':
        print show

        eztvit_id = None
        if show.get('eztvit_name'):
            eztvit_id = eztvit.showid_by_name(show.get('eztvit_name'))
        else:
            eztvit_id = eztvit.showid_by_name(show['human_name'])

        for eztv_espisode in eztvit.torrents(eztvit_id):
            show_name, season, episode = eztvit.episodeinfo_from_filename(eztv_espisode['filename'])
            if int(season)  >= int(show.get('season')) and \
               int(episode) >  int(show.get('episode')):
                   for t_url in eztv_espisode['torrents']:
                       out_fn = "%s S%sE%s.torrent" % (show['human_name'], season, episode)
                       print "Downloading", show_name, season, episode, "to", out_fn
                       data = urllib2.urlopen(t_url)
                       open(out_fn, 'wb').write(data.read())
                       config.set(section, "season", season)
                       config.set(section, "episode", episode)
                       break

config.write(open('config', 'w'))

