from pathlib import Path

import auto_dlp.codecs as codecs
import auto_dlp.variables as var


def _config_file(name):
    def function():
        file_path = Path(var.CONFIG_DIR).expanduser() / name()
        return file_path

    return function


def touch_folder(folder: Path):
    folder.mkdir(parents=True, exist_ok=True)


def touch_file(file: Path):
    if file.exists(): return
    touch_folder(file.parent)
    file.open("x").close()


@_config_file
def config_dir():
    return ""


@_config_file
def yt_api_key_file():
    return "YT_API_KEY.txt"


@_config_file
def download_cache():
    return "download cache"


@_config_file
def download_cache_trash():
    return "download cache (trash)"


@_config_file
def ytdlp_download_cache():
    return "yt-dlp download cache"


@_config_file
def thumbnail_dir():
    return "thumbnail cache"


@_config_file
def adb_installation():
    return "adb"


@_config_file
def ffmpeg_installation():
    return "ffmpeg"


@_config_file
def playlist_item_cache():
    return "playlist item cache"


@_config_file
def channel_cache():
    return "channel cache"


def channel_cache_songs():
    return channel_cache() / "songs"


@_config_file
def unavailable_items_cache():
    return "unavailable items cache"


@_config_file
def adb_push_files():
    return "adb push files.txt"


def thumbnail_file(prefix, obj_id):
    return thumbnail_dir() / prefix / f"{obj_id}.jpg"


def music_dir():
    return Path(".").expanduser()


def artist_dir(artist):
    return music_dir() / artist


def artist_songs_dir(artist):
    return artist_dir(artist) / "songs"


def try_get_song_file(artist, song, playlist: str = None):
    if playlist is None:
        directory = artist_songs_dir(artist)
    else:
        directory = playlist_dir(artist, playlist)

    for fmt in codecs.available_formats():
        path = directory / f"{song}.{fmt}"
        if path.exists():
            return path

    return None


# Adapts to the format of the original
def best_song_file(original: Path, artist, song, playlist: str = None):
    # Repeated code:
    if playlist is None:
        directory = artist_songs_dir(artist)
    else:
        directory = playlist_dir(artist, playlist)

    fmt = original.suffix
    if fmt == ".m4a":
        fmt = ".aac"
    return directory / f"{song}{fmt}"


def playlist_dir(artist, playlist):
    return artist_dir(artist) / playlist


def iter_playlist_items(artist, playlist, playlist_items):
    index = 0

    for entry in playlist_items:
        song_name = entry["name"]
        song_id = entry["id"]

        yield index, song_name, song_id
        index += 1


def try_get_playlist_files(artist, playlist, playlist_items):
    index = 0

    for entry in playlist_items:
        song_name = entry["name"]
        song_id = entry["id"]

        yield index, song_name, song_id, try_get_song_file(artist, song_name, playlist)
        index += 1
