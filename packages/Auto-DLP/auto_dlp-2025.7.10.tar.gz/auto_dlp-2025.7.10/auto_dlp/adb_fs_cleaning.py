from pathlib import PurePosixPath, Path
from subprocess import run

import auto_dlp.adb as adb
import auto_dlp.file_locations as fs


def _android_path_to_os(config, path: PurePosixPath):
    path = path.relative_to(config.adb_push_dir)
    return fs.music_dir() / Path(path)


def _push_allowed_files_list(config, artist: str, path: PurePosixPath, files: list):
    temp_file: Path = fs.adb_push_files()
    fs.touch_file(temp_file)

    with open(temp_file, "w") as file:
        for f in files:
            print(config.adb_push_dir / artist / PurePosixPath(f), file=file)

    run([adb.ADB_EXECUTABLE(), "-d", "push", str(temp_file.resolve()), str(path)])


def _allowed_files(config, artist: str):
    root = fs.artist_dir(artist)
    files_list = []

    def recurse(path: Path):
        files_list.append(path.relative_to(root))
        if path.is_dir():
            for sub in path.iterdir():
                recurse(sub)

    recurse(root)

    return files_list


def clean(config, artist: str, file: PurePosixPath):
    allowed_files = config.adb_push_dir / "allowed files.txt"
    sorted_allowed_files = config.adb_push_dir / "sorted allowed files.txt"
    _push_allowed_files_list(config, artist, allowed_files, _allowed_files(config, artist))
    run([adb.ADB_EXECUTABLE(), "shell",
         f'''
sort "{allowed_files}" > "{sorted_allowed_files}"

allowed_files=()

while read -r file; do
    allowed_files+=("$file");
done < "{sorted_allowed_files}"

length=${"{#allowed_files[@]}"}

find "{config.adb_push_dir}/{artist}" | while read -r file; do
is_allowed=false;
i=0;
while [[ $i -le $length ]] ; do
    compare_to="${"{allowed_files[$i]}"}"
    if [[ "$file" == "$compare_to" ]]; then
        # echo Yes $file $compare_to;
        is_allowed=true;
    fi
    ((i++))
done
if ! $is_allowed; then
    echo Deleting $file;
    rm "$file";
fi
done
rm "{allowed_files}"
rm "{sorted_allowed_files}"
'''])
    # sys.exit()


def clean_all(config):
    for artist in config.artists:
        file = config.adb_push_dir / fs.artist_dir(artist.name).relative_to(fs.music_dir())
        print(f"Cleaning {file}")
        clean(config, artist.name, file)

    for extra_folder in config.extra_sync_folders:
        file = config.adb_push_dir / extra_folder
        print(f"Cleaning {file}")
        clean(config, extra_folder, file)
