#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.util.html import get_content, add_header
from ykdl.util.match import match1, matchall
from ykdl.util import log
from ykdl.extractor import VideoExtractor
from ykdl.videoinfo import VideoInfo
from ykdl.compact import HTTPSHandler, build_opener, HTTPCookieProcessor, install_opener, urlopen, quote
from .youkujs import supported_stream_code, ids, stream_code_to_id, stream_code_to_profiles, id_to_container


import time
import json
import ssl

def fetch_cna():
    url = 'http://gm.mmstat.com/yt/ykcomment.play.commentInit?cna='
    req = urlopen(url)
    cookies = req.info()['Set-Cookie']
    cna = match1(cookies, "cna=([^;]+)")
    return cna if cna else "oqikEO1b7CECAbfBdNNf1PM1"

class Youku(VideoExtractor):
    name = u"优酷 (Youku)"

    def __init__(self):
        VideoExtractor.__init__(self)
        self.ccode = '0401'


    def prepare(self):
        add_header("referer", "http://v.youku.com")
        ssl_context = HTTPSHandler(
            context=ssl.SSLContext(ssl.PROTOCOL_TLSv1))
        cookie_handler = HTTPCookieProcessor()
        opener = build_opener(ssl_context, cookie_handler)
        opener.addheaders = [('Cookie','__ysuid=%d' % time.time())]
        install_opener(opener)
        
        info = VideoInfo(self.name)        

        if self.url and not self.vid:
             self.vid = match1(self.url, 'youku\.com/v_show/id_([a-zA-Z0-9=]+)' ,\
                                         'player\.youku\.com/player\.php/sid/([a-zA-Z0-9=]+)/v\.swf',\
                                         'loader\.swf\?VideoIDS=([a-zA-Z0-9=]+)',\
                                         'loader\.swf\?VideoIDS=([a-zA-Z0-9=]+)',\
                                         'player\.youku\.com/embed/([a-zA-Z0-9=]+)',\
                                         'video.tudou.com/v/([a-zA-Z0-9=]+)')

        self.logger.debug("VID: " + self.vid)
        api_url = 'https://ups.youku.com/ups/get.json?vid={}&ccode={}&client_ip=192.168.1.1&utid={}&client_ts={}'.format(self.vid, self.ccode, quote(fetch_cna()), int(time.time()))

        data = json.loads(get_content(api_url))
        assert data['e']['code'] == 0, data['e']['desc']
        data = data['data']
        assert 'stream' in data, data['error']['note']
        info.title = data['video']['title']
        streams = data['stream']
        for s in streams:
            self.logger.debug("stream> " + str(s))
            t = stream_code_to_id[s['stream_type']]
            urls = []
            for u in s['segs']:
                self.logger.debug("seg> " + str(u))
                if u['key'] != -1:
                    if 'cdn_url' in u:
                        urls.append(u['cdn_url'])
                else:
                    self.logger.warning("VIP video, ignore unavailable seg: {}".format(s['segs'].index(u)))
            if len(urls) == 0:
                urls = [s['m3u8_url']]
                c = 'm3u8'
            else:
                c = id_to_container[t]
            size = s['size']
            info.stream_types.append(t)
            info.streams[t] =  {
                    'container': c,
                    'video_profile': stream_code_to_profiles[t],
                    'size': size,
                    'src' : urls
                }
        info.stream_types = sorted(info.stream_types, key = ids.index)
        return info


site = Youku()
