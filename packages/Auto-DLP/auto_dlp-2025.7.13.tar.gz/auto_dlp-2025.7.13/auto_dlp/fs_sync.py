from pathlib import Path

import pycopy


def sync(src: Path, dest: Path):
    if not dest.exists():
        print(f"Skipping sync because destination does not exist: {terminal_formatting.add_color(1, dest)}")
        return

    pycopy.sync(src, dest, do_delete=True, use_hash=True)
