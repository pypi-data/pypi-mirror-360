from pathlib import Path

from mutagen.id3 import ID3, APIC, error
from mutagen.mp3 import MP3


def _add_img(data: MP3, type_id: int, desc: str, img_path: Path):
    data.tags.add(
        APIC(
            encoding=3,  # 3 is for utf-8
            mime='image/jpeg',  # image/jpeg or image/png
            type=type_id,  # 3 is for the cover image
            desc=desc,
            data=img_path.read_bytes()
        )
    )


def _add_imgs(song_path: Path):
    data = MP3(song_path, ID3=ID3)

    # add ID3 tag if it doesn't exist
    try:
        data.add_tags()
    except error:
        pass

    playlist_img = song_path.parent / "folder.jpg"
    artist_img = song_path.parent.parent / "folder.jpg"

    _add_img(data, 3, "Cover", playlist_img)
    _add_img(data, 8, "Artist or Performer", artist_img)

    data.save()


def write_for_song(config, artist, path: Path):
    _add_imgs(path)


def write_for_playlist_item(config, artist, playlist, path: Path):
    _add_imgs(path)
