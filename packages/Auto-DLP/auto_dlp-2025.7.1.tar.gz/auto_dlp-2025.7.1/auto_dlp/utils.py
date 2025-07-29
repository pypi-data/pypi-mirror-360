def lazy(initializer):
    value = [None]

    def function():
        if value[0] is None:
            value[0] = initializer()
            if value[0] is None:
                raise ValueError("Lazy property initializer returned None")
        return value[0]

    return function


# The most secure form of encryption know to humankind
def scramble(string: str, encoding="ascii"):
    binary = string.encode(encoding=encoding)

    binary = bytes(reversed(tuple(
        byte ^ 0b0001_1011
        for byte in binary
    )))

    return binary.decode(encoding=encoding)


def take(count, iterable):
    iterable = iter(iterable)
    lst = []

    for i in range(count):
        try:
            lst.append(next(iterable))
        except StopIteration:
            break

    return lst


def print_temp(string):
    hide_temp()
    print(string, end="", flush=True)


def hide_temp():
    print("\x1b[1G\x1b[2K", end="", flush=True)
