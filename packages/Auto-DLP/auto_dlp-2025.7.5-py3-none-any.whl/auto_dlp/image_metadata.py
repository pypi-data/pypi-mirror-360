from pathlib import Path

from mutagen.id3 import ID3, APIC, error
from mutagen.mp3 import MP3


def write_for_song(config, artist, path: Path):
    data = MP3(path, ID3=ID3)

    # add ID3 tag if it doesn't exist
    try:
        data.add_tags()
    except error:
        pass

    data.tags.add(
        APIC(
            encoding=3,  # 3 is for utf-8
            mime='image/jpeg',  # image/jpeg or image/png
            type=3,  # 3 is for the cover image
            desc='Cover',
            data=(path.parent / "folder.jpg").read_bytes()
        )
    )
    data.save()


def write_for_playlist_item(config, artist, playlist, path: Path):
    data = MP3(path, ID3=ID3)

    # add ID3 tag if it doesn't exist
    try:
        data.add_tags()
    except error:
        pass

    data.tags.add(
        APIC(
            encoding=3,  # 3 is for utf-8
            mime='image/jpeg',  # image/jpeg or image/png
            type=3,  # 3 is for the cover image
            desc='Cover',
            data=(path.parent / "folder.jpg").read_bytes()
        )
    )
    data.save()
