from pathlib import PurePosixPath
from subprocess import run

from auto_dlp import terminal_formatting
from auto_dlp.adb import ADB_EXECUTABLE


def _run_command(*command, capture_output=False):
    process = run([ADB_EXECUTABLE(), "-d", "shell", *command], capture_output=capture_output)

    if capture_output:
        return process.stdout

    return None


def is_dir(path: PurePosixPath):
    files = list_files(path)
    return len(files) != 1 or files[0] != path


def list_files(path: PurePosixPath):
    output = _run_command("ls", "-1", '"' + str(path.absolute()) + '"', capture_output=True)
    b_file_names = output.split(b"\n")
    file_names = []
    for name in b_file_names:
        try:
            name = name.decode().strip()
        except UnicodeDecodeError as e:
            print(
                f"{terminal_formatting.add_color(3, "Skipping")} file {name} because it could not be decoded using unicode")
            continue

        if name != "":
            file_names.append(name)

    return [path / name for name in file_names]


def delete_file(path: PurePosixPath):
    _run_command("rm", "-r", '"' + str(path.absolute()) + '"')
