import pycopy


def sync(src, dest):
    pycopy.sync(src, dest, do_delete=True)
