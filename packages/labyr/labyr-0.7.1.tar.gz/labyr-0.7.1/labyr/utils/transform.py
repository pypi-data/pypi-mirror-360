from typing import Callable, Iterable


def get_map(d: dict):
    return {v[0]: v[1] for k, v in d.items() if not k.isupper()}


def transform(args: Iterable, f: Callable) -> list:
    return list(map(f, args))
