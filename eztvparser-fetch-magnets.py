#!/usr/bin/env python

import eztvit

if __name__ == "__main__":
    import pprint
    import sys
    import os
    import re
    import urllib2

    if len(sys.argv) != 4:
        print "Usage: %s <outdir> http://eztv.it/shows/36/breaking-bad/ <filename filter: S02>" % sys.argv[0]
        sys.exit(1)

    out_dir = sys.argv[1]
    url = sys.argv[2]  # http://eztv.it/shows/36/breaking-bad/
    filter_pat = sys.argv[3]

    url_pat = re.compile(ur"shows\/(\d+)\/(.+)\/")
    m = url_pat.search(url)
    if m:
        show_id, show_name = m.groups()
    else:
        print "Could not extract show from", url
        sys.exit(1)

    for v in eztvit.torrents(show_id):
        for __t in v['torrents']:
            if v['filename'].find(filter_pat) > -1:
                if __t.find("magnet:") > -1:
                    f = open(os.path.join(out_dir, v['filename']+ ".magnet"), 'wb')
                    f.write(__t)
                    print "%s;%s;%s" % (__t, v['filename'], eztvit.episodeinfo_from_filename(v['filename']) )

