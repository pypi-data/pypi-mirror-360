import stat
import sys
import urllib.request as request
import zipfile
from pathlib import Path
from platform import system
from subprocess import run

import auto_dlp.file_locations as fs
from auto_dlp.utils import lazy

match system():
    case "Linux":
        EXECUTABLE_NAME = Path("platform-tools") / "adb"
        DOWNLOAD_URL = "https://dl.google.com/android/repository/platform-tools-latest-linux.zip"
    case "Windows":
        EXECUTABLE_NAME = Path("platform-tools") / "adb.exe"
        DOWNLOAD_URL = "https://dl.google.com/android/repository/platform-tools-latest-windows.zip"
    case _:
        print(f"This program has not been configured to run on {system()} yet")
        sys.exit(-1)


def _allow_execution(path: Path):
    if system() != "Linux": return

    path.chmod(stat.S_IXUSR)


@lazy
def ADB_EXECUTABLE():
    installation_path: Path = fs.adb_installation()
    path = installation_path / EXECUTABLE_NAME

    if path.exists():
        return path

    print(f"Installing adb for {system()}")

    fs.touch_folder(installation_path)

    (zip_path, _) = request.urlretrieve(DOWNLOAD_URL)

    with zipfile.ZipFile(zip_path, "r") as zip:
        zip.extractall(installation_path)

    _allow_execution(path)

    return str(path)


def validate_names(config):
    illegal_chars = "|\\?*<\":>+[]/"

    def check_name(name):
        if any(c in name for c in illegal_chars):
            print(
                f"The name {name} contains characters ({', '.join(set(illegal_chars) & set(name))}) that can potentially not be pushed to your android device")

    for artist in config.artists:
        check_name(artist.name)
        for playlist in artist.playlists:
            check_name(playlist)


def push_files(config):
    validate_names(config)

    if config.restart_adb:
        print("Restarting adb server")
        run(
            [ADB_EXECUTABLE(), "kill-server"]
        )

    run([
        ADB_EXECUTABLE(), "-d", "push", "--sync",
        # *(fs.artist_dir(a.name).resolve() for a in config.artists),
        # *((fs.music_dir() / folder).resolve() for folder in config.extra_sync_folders),
        *config.get_locations_to_sync(),
        str(config.adb_push_dir)
    ])


def is_device_connected(config):
    if config.restart_adb:
        print("Restarting adb server")
        run(
            [ADB_EXECUTABLE(), "kill-server"]
        )
    return run([ADB_EXECUTABLE(), "shell", "echo", "Connected to android device"]).returncode == 0
