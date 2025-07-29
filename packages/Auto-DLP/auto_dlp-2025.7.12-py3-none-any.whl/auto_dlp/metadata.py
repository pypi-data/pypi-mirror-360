import shutil
from pathlib import Path

from mutagen.easyid3 import EasyID3

import auto_dlp.file_cleaning as clean
import auto_dlp.thumbnails as thumbnails
from auto_dlp import age_hints
from auto_dlp.terminal_formatting import add_color


def write_for_song(config, artist, name: str, song_id, path: Path):
    mut = EasyID3()
    mut["title"] = name
    mut["artist"] = artist
    mut["albumartist"] = artist
    mut["album"] = f"{artist} songs"
    mut["copyright"] = "none"
    # mut["date"] = "0"
    mut["date"] = str(age_hints.get_hint(None, song_id))
    mut.save(path, v1=2)
    mut.save(path, v1=1)

    # meta = eye.load(path)
    # meta.tag.title = name
    # meta.tag.artist = artist
    # meta.tag.album = f"{artist} songs"
    # meta.tag.album_artist = artist
    # meta.tag.original_release_date = 2000

    # meta.tag.save()
    # meta.tag.track_num = 3


def process_artist(config, artist, songs, artist_path, song_path: Path):
    thumbnail = thumbnails.get_for_artist(config, songs)
    if thumbnail is None: return

    for path in [artist_path, song_path]:
        if not path.exists():
            continue

        img_path = path / "folder.jpg"

        if img_path.exists():
            clean.know_file(img_path)
            continue

        shutil.copyfile(thumbnail, img_path)
        clean.know_file(img_path)


def process_playlist(config, artist, playlist, playlist_id, path: Path):
    img_path = path / "folder.jpg"
    if img_path.exists():
        clean.know_file(img_path)
        return
    try:
        shutil.copyfile(thumbnails.get_for_playlist(playlist_id), img_path)
        clean.know_file(img_path)
    except RuntimeError:
        print(add_color(1, "Could not write playlist thumbnail to playlist directory"))


def write_for_playlist_item(config, artist, playlist, name, playlist_id, song_id, index, item_count, path: Path):
    mut = EasyID3()
    mut["title"] = name
    mut["artist"] = artist
    mut["albumartist"] = artist
    mut["album"] = playlist
    mut["copyright"] = "none"
    mut["tracknumber"] = f"{index + 1}/{item_count}"
    # mut["date"] = "0"
    mut["date"] = str(age_hints.get_hint(playlist_id, song_id))
    mut.save(path, v1=2)
    mut.save(path, v1=1)

    # meta = eye.load(path)
    # meta.tag.title = name
    # meta.tag.artist = artist
    # meta.tag.album = f"{artist} songs"
    # meta.tag.album_artist = artist
    # meta.tag.original_release_date = 2000
    # meta.tag.track_num = index + 1

    # meta.tag.save()
