from os.path import getsize

import auto_dlp.YoutubeDataAPIv3 as api
import auto_dlp.file_locations as fs


def _cache_file(song_id):
    return fs.channel_cache_songs() / f"{song_id}.txt"


def _get_content(file):
    with open(file) as fhandle:
        content = fhandle.read()
    return content


def get_for_song(song_id):
    file = _cache_file(song_id)
    if file.exists() and getsize(file) > 0:
        return _get_content(file)

    channel = api.get_song_channel(song_id)
    fs.touch_file(file)
    with open(file, "w") as fhandle:
        fhandle.write(channel)

    return channel
