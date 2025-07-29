import os
import sys
import zipfile
from pathlib import Path
from platform import system
from urllib import request

import auto_dlp.file_locations as fs
from auto_dlp import utils

match system():
    case "Linux":
        EXECUTABLE_NAME = None
        DOWNLOAD_URL = None
    case "Windows":
        EXECUTABLE_NAME = Path("ffmpeg-master-latest-win64-gpl-shared") / "bin" / "ffmpeg.exe"
        DOWNLOAD_URL = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl-shared.zip"
    case _:
        print(f"This program has not been configured to run on {system()} yet")
        sys.exit(-1)


def check_ffmpeg_availability_linux():
    if os.system("ffmpeg -version") != 0:
        print(
            "Something is wrong with your ffmpeg installation and you are on Linux\nYou are on your own (try sudo apt install ffmpeg)",
            file=sys.stderr)
        sys.exit(-1)


@utils.lazy
def EXECUTABLE():
    if system() == "Linux":
        check_ffmpeg_availability_linux()
        return ""

    installation_path: Path = fs.ffmpeg_installation()
    path = installation_path / EXECUTABLE_NAME

    if path.exists():
        print(f"ffmpeg found at {path}")
        return path

    print(f"Installing ffmpeg for {system()}")

    fs.touch_folder(installation_path)

    (zip_path, _) = request.urlretrieve(DOWNLOAD_URL)

    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(installation_path)

    return path
