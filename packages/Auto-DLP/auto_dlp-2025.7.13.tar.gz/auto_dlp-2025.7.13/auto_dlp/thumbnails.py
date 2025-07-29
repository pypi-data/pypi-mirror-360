import urllib.request as request
from collections import Counter
from os.path import getsize
from pathlib import Path

from PIL import Image

import auto_dlp.YoutubeDataAPIv3 as api
import auto_dlp.file_locations as fs
from auto_dlp import utils, channels


def _get_url(api_function, obj_id):
    thumbnails: dict = api_function(obj_id)
    for key in ["high", "medium"]:
        try:
            return thumbnails[key]["url"]
        except KeyError:
            continue
    for key, value in thumbnails.items():
        return value["url"]
    return None


def _get_path(api_function, prefix, obj_id) -> Path:
    path: Path = fs.thumbnail_file(prefix, obj_id)

    if path.exists() and getsize(path) > 0:
        return path

    fs.touch_file(path)

    url = _get_url(api_function, obj_id)

    request.urlretrieve(url, path)

    return path


def _get_path_with_mime_check(api_function, prefix, obj_id) -> Path:
    path = _get_path(api_function, prefix, obj_id)
    img = Image.open(path)

    if img.format == 'JPEG':
        return path

    print(f"Reencoding thumbnail image from {img.format} to JPEG")

    img.save(path, format='JPEG')

    return path


def _get(api_function, prefix, obj_id):
    return _get_path_with_mime_check(api_function, prefix, obj_id)


def get_for_song(song_id):
    return _get(api.get_song_thumbnails, "songs", song_id)


def get_for_playlist(playlist_id):
    return _get(api.get_playlist_thumbnails, "playlists", playlist_id)


def get_for_artist(config, songs: list):
    samples = utils.take(config.name_samples, songs)
    if len(samples) == 0: return None
    channel_counts = Counter()

    for sample in samples:
        channel_counts[channels.get_for_song(sample)] += 1

    (channel, count) = channel_counts.most_common(1)[0]

    return _get(api.get_channel_thumbnails, "channels", channel)
