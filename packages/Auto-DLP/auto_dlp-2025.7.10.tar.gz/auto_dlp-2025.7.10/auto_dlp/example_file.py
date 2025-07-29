import json
import os
from pathlib import Path


def generate_file(folder: Path, name):
    file = folder / name
    if file.exists():
        print(
            f"A {name} file already exists in the directory {folder}, won't overwrite it. Please delete the file manually if you want to regenerate the sample file.")
        return

    file.touch(exist_ok=False)

    match os.name:
        case "nt":
            config_dir = "C:\\ProgramData"  # This does not work sPath("C:") / "ProgramData"
        case "posix":
            config_dir = Path.home() / ".config"
        case _:
            print(f"Unknown OS name: {os.name} so no custom configuration of config path possible, using POSIX default")
            config_dir = Path.home() / ".config"

    config_dir = config_dir / "auto-dlp"

    json_obj = {
        "config dir": str(config_dir),
        "artists": {
            "Disney": {
                "songs": {
                    "Let it go": "L0MK7qz13bU"
                }
            },
            "Billie Eilish": {
                "playlists": {
                    "Dont smile at me": "OLAK5uy_mYmH6NFnJ6IaH3Ln3wGeVimrFk8FXKzcA",
                    "Happier Than Ever": "OLAK5uy_lkHngwJMHlqHsz7ckye6lwrhYmyFTMvM4"
                }
            },
            "Rick Astley": {
                "songs": {
                    "Never gonna give you up": "dQw4w9WgXcQ"
                }
            }
        }
    }

    with open(file, "w") as fhandle:
        json.dump(json_obj, fhandle, indent="\t")

    print(f"Successfully created file at {file.resolve()}")
