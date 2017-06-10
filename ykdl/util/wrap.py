#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import shlex
from logging import getLogger

logger = getLogger("wrap")

from ykdl.compact import compact_tempfile
from .html import fake_headers


def launch_player(player, urls):
    if 'mpv' in player:
        ua_flg = ''
        referer_flg = ''
#bilibili hacks
        is_bili_cdn = False
        for url in urls:
            if 'acgvideo.com' in url:
                is_bili_cdn = True
                break

        if is_bili_cdn:
            ua_flg = '--user-agent={0}'.format(fake_headers['User-Agent'])
            referer_flg = '--referrer=http://bilibili.com'

        cmd = shlex.split(player)
        if ua_flg:
            cmd += [ua_flg]
        if referer_flg:
            cmd += [referer_flg]
        cmd = cmd + ['--demuxer-lavf-o=protocol_whitelist=[file,tcp,http]'] + list(urls)
    else:
        cmd = shlex.split(player) + list(urls)
    subprocess.call(cmd)

def launch_ffmpeg(basename, ext, lenth):
    #build input
    inputfile = compact_tempfile(mode='w+t', suffix='.txt', dir='.', encoding='utf-8')
    for i in range(lenth):
        inputfile.write('file \'%s_%d_.%s\'\n' % (basename, i, ext))
    inputfile.flush()

    outputfile = basename+ '.' + ext

    cmd = ['ffmpeg','-f', 'concat', '-safe', '-1', '-y', '-i', inputfile.name, '-c', 'copy', '-hide_banner']
    if ext == 'mp4':
        cmd += ['-absf', 'aac_adtstoasc']

    cmd.append(outputfile)
    print('Merging video %s using ffmpeg:' % basename)
    subprocess.call(cmd)

def launch_ffmpeg_download(url, name, live):
    print('Now downloading: %s' % name)
    if live:
        print('stop downloading by press \'q\'')

    cmd = ['ffmpeg', '-y']

    if not url.startswith('http'):
       cmd += ['-protocol_whitelist', 'file,tcp,http' ]

    cmd += ['-i', url, '-c', 'copy', '-absf', 'aac_adtstoasc',  '-hide_banner', name]

    subprocess.call(cmd)
