import re
import sys

_name_pattern = re.compile("(?P<Name>.+)\\((?P<Year>[0-9]+)\\)")
_playlist_hints = {}
_song_hints = {}


def add_hint_playlist(playlist_id, year):
    if playlist_id in _playlist_hints:
        print(f"Age hint has already been set for {playlist_id}", file=sys.stderr)
    _playlist_hints[playlist_id] = year


def add_hint_song(song_id, year):
    if song_id in _song_hints:
        print(f"Age hint has already been set for {song_id}", file=sys.stderr)
    _song_hints[song_id] = year


def parse_name(ex_name, obj_id, hint_function):
    match = _name_pattern.fullmatch(ex_name)
    if match is None:
        return ex_name

    values = match.groupdict()

    hint_function(obj_id, int(values["Year"]))

    return values["Name"].strip()


def get_hint(playlist_id, song_id):
    if playlist_id is not None and playlist_id in _playlist_hints:
        return _playlist_hints[playlist_id]

    try:
        return _song_hints[song_id]
    except KeyError:
        return 0
