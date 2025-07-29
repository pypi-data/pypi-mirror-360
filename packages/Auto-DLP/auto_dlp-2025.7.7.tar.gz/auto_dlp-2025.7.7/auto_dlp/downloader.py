import os
import shutil
import sys
from pathlib import Path

import yt_dlp as yt
from yt_dlp import DownloadError

import auto_dlp.codecs as codecs
import auto_dlp.file_locations as fs
from auto_dlp import unavailable_items, ffmpeg


def _video_url(x):
    return f"https://www.youtube.com/watch?v={x}"


# def _song_file_path(song_id):
#     return fs.download_cache() / f"{song_id}.mp3"

def _try_get_song_file(song_id):
    downld_cache = fs.download_cache()
    for fmt in ["mp3", "m4a"]:
        file = downld_cache / f"{song_id}.{fmt}"
        if file.exists():
            return file
    return None


def _download_song(song_id, config, use_cookies=False):
    if unavailable_items.is_unavailable(song_id):
        return None

    if config.codec not in codecs.available_codecs():
        raise RuntimeError(
            f"In the config the codec to use was specified as {config.codec}, "
            f"but currently only the codecs {codecs.available_codecs()} have been tested and are supported")
    codec = config.codec

    # Saving directory so that current dir can be restored later (has to be changed for yt-dlp to work)
    download_dir = fs.download_cache()
    music_dir = Path(os.curdir).resolve()

    fs.touch_folder(download_dir)
    fs.touch_folder(fs.ytdlp_download_cache())

    os.chdir(download_dir)

    ydl_options = {
        'format': 'm4a/bestaudio/best',
        "cache-dir": fs.ytdlp_download_cache(),
        "outtmpl": "%(id)s",
        "print": f"Song %(id)s has been downloaded",
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': codec,
        }]
    }

    if ffmpeg.EXECUTABLE() != "":
        ydl_options["ffmpeg_location"] = str(ffmpeg.EXECUTABLE())

    if use_cookies:
        ydl_options["cookiesfrombrowser"] = ("firefox",)

    try:
        with yt.YoutubeDL(ydl_options) as ydl:
            error_code = ydl.download([_video_url(song_id)])
            print(f"Error Code {error_code}")
    except DownloadError as e:
        print("An error occurred during download", file=sys.stderr)

        if unavailable_items.is_error_message_indicative_of_unavailability(e.msg):
            unavailable_items.know_is_unavailable(song_id)
            return None

        if not use_cookies and config.use_cookies:
            print("Retrying with cookies", file=sys.stderr)
            return _download_song(song_id, config, True)
        else:
            return None

    os.chdir(music_dir)

    song_file = _try_get_song_file(song_id)
    if song_file is None:
        raise RuntimeError(
            f"There was an internal error during the download, somehow the file {download_dir / f"{song_id}.{codec}"} was not created")

    return song_file


def _interruptable_download_song(song_id, config):
    try:
        return _download_song(song_id, config)
    except KeyboardInterrupt as e:
        path: Path = _try_get_song_file(song_id)
        if path is not None:
            path.unlink(missing_ok=True)
        raise e


def get_song_file(song_id, config):
    song_file = _try_get_song_file(song_id)
    if song_file is not None:
        return song_file

    music_dir = Path(os.curdir).resolve()
    path = _interruptable_download_song(song_id, config)
    os.chdir(music_dir)
    return path


def delete_cached_version(artist: str, song_id: str):
    song_file: Path = _try_get_song_file(song_id)
    if song_file is not None:
        folder = fs.download_cache_trash() / artist
        fs.touch_folder(folder)
        shutil.move(song_file, folder / song_file.name)
