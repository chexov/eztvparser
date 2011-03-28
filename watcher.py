#!/usr/bin/env python
# encoding: utf-8

import ConfigParser
import urllib2
import sys
import time

import eztvit


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "Usage: %s <config> <out torrents dir>" % sys.argv[0]
        sys.exit(1)
    config_fn, out_dir = sys.argv[1:]

    config = ConfigParser.ConfigParser()
    config.read(config_fn)

    # Validate all tvshow names in the config file
    for section in config.sections():
        show = dict(config.items(section))
        if show.get('eztvit_name'):
            eztvit_id = eztvit.showid_by_name(show.get('eztvit_name'))
        else:
            eztvit_id = eztvit.showid_by_name(show['human_name'])


    # Download next episodes
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
                           out_fn = "%s/%s %sx%s.torrent" % (out_dir, show['human_name'], season, episode)
                           print "Downloading", show_name, season, episode, "to", out_fn
                           data = urllib2.urlopen(t_url)
                           open(out_fn, 'wb').write(data.read())
                           config.set(section, "season", season)
                           config.set(section, "episode", episode)
                           break
        print "Sleeping..."
        time.sleep(2)
        config.write(open(config_fn, 'w'))

