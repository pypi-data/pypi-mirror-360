import shutil

import auto_dlp.downloader as downloader
import auto_dlp.file_cleaning as clean
import auto_dlp.file_locations as fs
import auto_dlp.metadata as metadata
from auto_dlp import playlist_items, terminal_formatting
from auto_dlp.name_cleaning import clean_name


def _copy_if_necessary(src, dest):
    if dest.exists(): return False
    if not src.exists():
        raise RuntimeError(f"There was an unexpected error during download. The file {src} could not be found.")

    fs.touch_file(dest)
    shutil.copyfile(src, dest)
    return True


def download_song(config, artist, name, song_id):
    raw_file = downloader.get_song_file(song_id, config)
    file = fs.best_song_file(raw_file, artist, name)

    fs.touch_folder(file.parent)
    clean.know_file(file.parent)
    necessary = _copy_if_necessary(raw_file, file)
    clean.know_file(file)

    if necessary:
        metadata.write_for_song(config, artist, name, song_id, file)


def download_playlist(config, artist, playlist_name, playlist_id):
    raw_items = playlist_items.get(config, playlist_id)
    items = [
        {"name": clean_name(config, i["name"]), "id": i["id"]} for i in raw_items
    ]

    fs.touch_folder(fs.playlist_dir(artist, playlist_name))
    clean.know_file(fs.playlist_dir(artist, playlist_name))

    for index, name, song_id in fs.iter_playlist_items(artist, playlist_name, items):
        raw_file = downloader.get_song_file(song_id, config)
        if raw_file is None:
            print(
                f"{terminal_formatting.add_color(3, 'Skipping')} "
                f"unavailable song {terminal_formatting.add_color(3, name)} from {playlist_name}")
            continue

        target_path = fs.best_song_file(raw_file, artist, name, playlist_name)

        necessary = _copy_if_necessary(raw_file, target_path)
        clean.know_file(target_path)

        if necessary:
            print(f"Downloaded {name} by {artist} from {playlist_name}")
            metadata.write_for_playlist_item(config, artist, playlist_name, name, playlist_id, song_id, index,
                                             len(items), target_path)

    metadata.process_playlist(config, artist, playlist_name, playlist_id, fs.playlist_dir(artist, playlist_name))
