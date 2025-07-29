import re
import sys
from functools import cache

_illegal_chars = "\\/!*&\":?#|.,"
_n_whitespace_re = re.compile("\\s{2,}")
_indent = " " * 10


@cache
def regex_for_rule(config, rule):
    for value, repl in config.rule_macros.items():
        rule = rule.replace(value, repl)
    return re.compile(rule, flags=re.IGNORECASE)


def get_illegal_fs_chars():
    return _illegal_chars


def name_contains_illegal_chars(name: str):
    return any(((c in name) for c in _illegal_chars))


def clean_name(config, name: str, verbose=False):
    if verbose:
        print(f"Name at start:\n{_indent}{name}\n", file=sys.stderr)

    if name in config.rename:
        if verbose:
            print(f"Name has been force renamed: {name} -> {config.rename[name]}", file=sys.stderr)
        return config.rename[name]

    og_name = name
    name = "".join(filter(lambda c: c not in _illegal_chars, name))
    name = name.replace(" ", " ")

    if verbose:
        print(f"Name after removing illegal chars:\n{_indent}{name}\n", file=sys.stderr)

    for rule in config.name_rules:
        rule: re.Pattern = regex_for_rule(config, rule)
        name = rule.sub("", name)
        if verbose:
            print(f"Name after regex rule {rule.pattern}:\n{_indent}{name}\n", file=sys.stderr)

    name = _n_whitespace_re.sub(" ", name)
    name = name.strip()

    if name == "":
        if not verbose:
            clean_name(config, og_name, verbose=True)
        raise ValueError(f"Name is empty after cleaning: {og_name}")

    return name
