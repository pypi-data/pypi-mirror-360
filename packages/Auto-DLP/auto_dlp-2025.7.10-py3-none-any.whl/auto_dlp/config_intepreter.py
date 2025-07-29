import os
import sys
from pathlib import Path, PurePosixPath
from time import sleep

import requests

import auto_dlp.adb_fs_cleaning as adb_clean
import auto_dlp.download_manager as download
import auto_dlp.file_cleaning as clean
import auto_dlp.file_locations as fs
import auto_dlp.fs_sync as fs_sync
import auto_dlp.variables as variables
from auto_dlp import adb, playlist_items, age_hints, terminal_formatting
from auto_dlp.file_locations import touch_folder
from auto_dlp.metadata import process_artist
from auto_dlp.name_cleaning import clean_name, name_contains_illegal_chars, get_illegal_fs_chars
from auto_dlp.redownloading import redownload
from auto_dlp.terminal_formatting import add_color


class Config:
    properties = ["config dir", "adb push", "adb push dir", "restart adb", "extra sync folders", "clean push dir",
                  "name rules", "artists", "rule macros", "use cookies", "rename", "name samples", "retry interval",
                  "fragile playlists", "sync dirs", "codec"]

    def __init__(self):
        self.config_dir = None
        self.adb_push = False
        self.adb_push_dir = PurePosixPath("/sdcard/Music/")
        self.restart_adb = False
        self.extra_sync_folders = []
        self.clean_push_dir = True
        self.name_rules = []
        self.compiled_name_rules = []
        self.rule_macros = {}
        self.name_samples = 4
        self.artists = []
        self.use_cookies = False
        self.rename = {}
        self.retry_interval = 10
        self.fragile_playlists = []
        self.sync_dirs = []
        self.invalid_item_names = 0
        self.invalid_item_name_artist_count = 0
        self.codec = "aac"

    def assign_property(self, key, value):
        match key:
            case "config dir":
                self.config_dir = Path(value)
                variables.CONFIG_DIR = self.config_dir
            case "adb push":
                self.adb_push = bool(value)
            case "adb push dir":
                self.adb_push_dir = PurePosixPath(value)
            case "clean push dir":
                self.clean_push_dir = bool(value)
            case "restart adb":
                self.restart_adb = bool(value)
            case "name rules":
                self.name_rules = list(value)
            case "rule macros":
                self.rule_macros = dict(value)
            case "name_samples":
                self.name_samples = int(value)
            case "artists":
                self.artists = [
                    Artist.from_json(self, name, json) for name, json in value.items()
                ]
            case "use cookies":
                self.use_cookies = bool(value)
            case "rename":
                self.rename = dict(value)
            case "retry interval":
                self.retry_interval = float(value)
            case "fragile playlists":
                self.fragile_playlists = list(value)
            case "extra sync folders":
                self.extra_sync_folders = list(value)
            case "sync dirs":
                self.sync_dirs = [Path(path_string).expanduser() for path_string in value]
            case "codec":
                self.codec = str(value)

    def get_locations_to_sync(self):
        for artist in self.artists:
            yield fs.artist_dir(artist.name).resolve()
        for folder in self.extra_sync_folders:
            yield (fs.music_dir() / folder).resolve()

    @classmethod
    def from_json(cls, json):
        config = Config()

        for key, value in json.items():
            if key not in cls.properties:
                raise ValueError(f"Unknown property key: {key}")

            config.assign_property(key, value)

        if config.invalid_item_names > 0:
            print(
                f"{config.invalid_item_names} name(s) over {config.invalid_item_name_artist_count} artist(s) contain an illegal character",
                file=sys.stderr)
            sys.exit(-1)

        return config

    def __str__(self):
        return (f"""config file: {self.config_dir}
adb push: {self.adb_push}
name rules: {" ".join(self.name_rules)}
artists:
""" + "\n".join(map(str, self.artists)))


class Artist:
    properties = ["songs", "playlists"]

    def __init__(self, config, name):
        self.config = config
        self.name = name
        self.songs = {}
        self.playlists = {}

    def all_songs(self):
        yield from self.songs.values()

        for name, playlist_id in self.playlists.items():
            for entry in playlist_items.get(self.config, playlist_id):
                yield entry["id"]

    def assign_property(self, key, value):
        match key:
            case "songs":
                # self.songs = dict(value)
                self.songs = _process_years_in_names(dict(value), age_hints.add_hint_song)
            case "playlists":
                # self.playlists = dict(value)
                self.playlists = _process_years_in_names(dict(value), age_hints.add_hint_playlist)

    def validate_item_names(self):
        invalid_name_count = [0]

        def validate_item_name(item_type: str, name: str):
            if name_contains_illegal_chars(name):
                print(
                    f"{item_type} name contains illegal character(s): {add_color(1, name)} contains one of {add_color(1, get_illegal_fs_chars())}",
                    file=sys.stderr)
                invalid_name_count[0] += 1

        validate_item_name("artist", self.name)
        for song in self.songs.keys():
            validate_item_name("song", song)
        for playlist in self.playlists.keys():
            validate_item_name("playlist", playlist)

        if invalid_name_count[0] > 0:
            self.config.invalid_item_names += invalid_name_count[0]
            self.config.invalid_item_name_artist_count += 1

    @classmethod
    def from_json(cls, config, name, json):
        artist = Artist(config, name)

        for key, value in json.items():
            if key not in cls.properties:
                raise ValueError(f"Unknown property key: {key}")

            artist.assign_property(key, value)

        artist.validate_item_names()

        return artist

    def __str__(self):
        return "\n".join((
            f"""    {self.name}:""",
            *(f"        {name}: {song_id}" for name, song_id in self.songs.items()),
            *(f"        {name}: {playlist_id}" for name, playlist_id in self.playlists.items())
        ))


def _process_years_in_names(mp, hint_function):
    new_map = {}

    for name, obj_id in mp.items():
        new_name = age_hints.parse_name(name, obj_id, hint_function)
        new_map[new_name] = obj_id

    return new_map


def _execute_artist(config, artist):
    print(f"Looking at {terminal_formatting.add_color(2, artist.name)}")
    touch_folder(fs.artist_dir(artist.name))
    clean.know_file(fs.artist_dir(artist.name))

    for song_name, song_id in artist.songs.items():
        print(f"Downloading {song_name} ({song_id})")
        download.download_song(config, artist.name, song_name, song_id)

    process_artist(config, artist, artist.all_songs(), fs.artist_dir(artist.name), fs.artist_songs_dir(artist.name))

    for playlist_name, playlist_id in artist.playlists.items():
        print(
            f"Downloading {playlist_name} ({playlist_id})\n\tinto {fs.playlist_dir(artist.name, playlist_name).resolve()}")
        download.download_playlist(config, artist.name, playlist_name, playlist_id)


def _resiliently_execute_artist(config, artist):
    try:
        while True:
            try:
                _execute_artist(config, artist)
                return
            except requests.exceptions.ConnectionError as e:
                print(f"Connection to Internet services failed: {e}", file=sys.stderr, flush=True)
                print(
                    f"Retrying in {config.retry_interval} seconds; Press {add_color(2, "Ctrl-C")} to skip this artist")
                sleep(config.retry_interval)
                continue
    except KeyboardInterrupt:
        print(f"Artist {artist.name} will be left untouched")
        clean.know_folder_recursively(fs.artist_dir(artist.name))


def execute_adb(config):
    if not config.adb_push: return

    if adb.is_device_connected(config):
        if config.adb_push:
            adb.push_files(config)

        if config.clean_push_dir:
            adb_clean.clean_all(config)
    else:
        print("No Android device connected to this computer using usb", file=sys.stderr)


def execute_sync_sd(config, src: Path, dest: Path):
    print(f"Syncing from {src} to {dest}")
    if not dest.exists():
        print(f"Interrupting sync because destination does not exist: {terminal_formatting.add_color(1, dest)}")
        return
    for to_sync in config.get_locations_to_sync():
        sub_path = to_sync.relative_to(src)
        print(f"Syncing {sub_path}")
        fs_sync.sync(src / sub_path, dest / sub_path)


def execute_sync(config):
    src = Path(os.curdir).resolve()
    for dest in config.sync_dirs:
        execute_sync_sd(config, src, dest)


def execute(json_file, redownload_objects=(), test_names=(), playlist_test_names=None, verbose=False):
    config = Config.from_json(json_file)

    if playlist_test_names is not None:
        for artist in config.artists:
            if playlist_test_names in artist.playlists:
                playlist_test_names = artist.playlists[playlist_test_names]
        test_names = list(test_names)
        test_names += map(lambda x: x["name"], playlist_items.get(config, playlist_test_names))

    if len(test_names) > 0:
        for name in test_names:
            print(f"{name} becomes {clean_name(config, name, verbose=verbose)}")
        return

    if len(redownload_objects) > 0:
        for obj in redownload_objects:
            redownload(config, obj.strip())
        return

    print(config)

    for artist in config.artists:
        _resiliently_execute_artist(config, artist)

    clean.clean_all(config)

    execute_sync(config)
    execute_adb(config)
