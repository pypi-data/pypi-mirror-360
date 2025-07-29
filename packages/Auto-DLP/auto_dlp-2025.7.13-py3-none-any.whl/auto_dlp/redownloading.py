import re

import auto_dlp.downloader as downloader
import auto_dlp.file_locations as fs
from auto_dlp import playlist_items
from auto_dlp.name_cleaning import clean_name
from auto_dlp.terminal_formatting import add_color


class PlaylistWrapper:
    def __init__(self, config, artist, name, oid):
        self.config = config
        self.artist = artist
        self.name = name
        self.oid = oid

    def __str__(self):
        return f"playlist {add_color(1, self.name)} ({self.oid}) by {add_color(2, self.artist.name)}"

    def items(self):
        for entry in playlist_items.get(self.config, self.oid):
            song_name = clean_name(self.config, entry["name"])
            song_id = entry["id"]

            yield SongWrapper(self.config, self.artist, song_name, song_id, self)

    def delete(self):
        print(f"Deleting {self}:")

        for song in self.items():
            song.delete()


class SongWrapper:
    def __init__(self, config, artist, name, oid, playlist: PlaylistWrapper = None):
        self.config = config
        self.artist = artist
        self.name = name
        self.oid = oid
        self.playlist = playlist

    def __str__(self):
        return f"song {add_color(1, self.name)} ({self.oid}) by {add_color(2, self.artist.name)}"

    def get_file(self):
        if self.playlist is None:
            return fs.try_get_song_file(self.artist.name, self.name)
        else:
            return fs.try_get_song_file(self.artist.name, self.name, self.playlist.name)

    def delete(self):
        file = self.get_file()
        if file is None: return
        print(f"Deleting {self}: {file}")
        file.unlink(missing_ok=True)
        downloader.delete_cached_version(self.artist.name, self.oid)


# Yields: song name, song id and artist
def _iter_songs(config, artist=None):
    if artist is None:
        for artist in config.artists:
            yield from _iter_songs(config, artist)

    for name, song_id in artist.songs.items():
        yield SongWrapper(config, artist, name, song_id)

    for playlist in _iter_playlists(config, artist):
        for entry in playlist_items.get(config, playlist.oid):
            name = clean_name(config, entry["name"])
            song_id = entry["id"]

            yield SongWrapper(config, artist, name, song_id, playlist)


def _iter_playlists(config, artist=None):
    if artist is None:
        for artist in config.artists:
            yield from _iter_playlists(config, artist)

    for playlist_name, playlist_id in artist.playlists.items():
        yield PlaylistWrapper(config, artist, playlist_name, playlist_id)


def _get_obj_locations(config, obj_id):
    obj_re = re.compile(obj_id, flags=re.IGNORECASE)

    for playlist in _iter_playlists(config):
        if playlist.oid == obj_id or obj_re.fullmatch(playlist.name) is not None:
            yield playlist

    for song in _iter_songs(config):
        if song.oid == obj_id or obj_re.fullmatch(song.name) is not None:
            yield song


def redownload(config, obj_id):
    matches = list(_get_obj_locations(config, obj_id))
    print(f"Found the following matches for {obj_id}:")
    for obj in matches:
        print(f"Found {obj}")

    confirmation = input(f"Really redownload all matches for {obj_id}? (y/n) ")
    if confirmation.strip() != "y":
        print("Aborted")
        return

    for obj in matches:
        obj.delete()
