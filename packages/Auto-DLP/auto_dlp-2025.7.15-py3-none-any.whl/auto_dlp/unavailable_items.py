import auto_dlp.file_locations as fs

_unavailability_err_msgs = ["This video has been removed", "This video is not available", "This video is private",
                            "This video is no longer available", "Video unavailable", "Private video"]


def is_error_message_indicative_of_unavailability(msg):
    return any(i in msg for i in _unavailability_err_msgs)


def _indicator_file(song_id):
    return fs.unavailable_items_cache() / song_id


def know_is_unavailable(song_id):
    if is_unavailable(song_id): return
    fs.touch_file(_indicator_file(song_id))


def is_unavailable(song_id):
    file = _indicator_file(song_id)
    return file.exists()
