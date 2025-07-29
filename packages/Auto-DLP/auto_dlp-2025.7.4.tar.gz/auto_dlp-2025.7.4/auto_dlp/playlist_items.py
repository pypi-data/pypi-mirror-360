import json
from collections import Counter
from os.path import getsize
from pathlib import Path

import auto_dlp.YoutubeDataAPIv3 as api
import auto_dlp.file_locations as fs
from auto_dlp.name_cleaning import clean_name


def _get_content(file):
    with open(file) as fhandle:
        content = json.load(fhandle)
    return content


# Do not cache; returned objects are mutable
def _get_without_cleaning(config, playlist_id):
    file: Path = fs.playlist_item_cache() / f"{playlist_id}.json"
    if file.exists() and getsize(file) > 0:
        return _get_content(file)

    items = api.get_playlist_items(config, playlist_id)
    fs.touch_file(file)
    with open(file, "w") as fhandle:
        json.dump(items, fhandle)

    return items


# This method operates after name cleaning (unlike the one from YoutubeDataAPIv3)
def deduplicate_playlist_items(config, playlist_items):
    name_counter = Counter()

    # Count occurrences of each name
    for item in playlist_items:
        name_counter[clean_name(config, item["name"])] += 1

    # List of names with count greater one
    index_names = set()

    for name, count in name_counter.items():
        if count > 1:
            index_names.add(name)

    # If everything is fine
    if len(index_names) == 0:
        return playlist_items

    name_counter = Counter()

    for item in playlist_items:
        name = item["name"]
        clean = clean_name(config, name)
        if clean in index_names:
            name_counter[clean] += 1
            item["name"] = f"{name} ={name_counter[clean]}="

    return playlist_items


# Do not cache; returned objects are mutable
def get(config, playlist_id):
    items = _get_without_cleaning(config, playlist_id)

    deduplicate_playlist_items(config, items)

    return items
