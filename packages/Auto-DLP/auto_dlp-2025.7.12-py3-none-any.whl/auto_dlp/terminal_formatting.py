def add_color(color, string):
    return f"\x1b[38;5;{color}m{string}\x1b[m"
