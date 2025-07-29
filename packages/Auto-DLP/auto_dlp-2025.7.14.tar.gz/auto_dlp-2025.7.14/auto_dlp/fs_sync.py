from pathlib import Path

import pycopy


def sync(src: Path, dest: Path):
    if not src.exists():
        print(f"Skipping sync because source does not exist: {terminal_formatting.add_color(1, src)}")
        return

    pycopy.sync(src, dest, do_delete=True, use_hash=True)
