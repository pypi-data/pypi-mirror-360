import msvcrt
import os
from os import system


def box(string: str) -> str:
    raw_lines = string.split("\n")
    stripped_lines = [line.strip() for line in raw_lines]
    if not stripped_lines:
        return "+--+\n|  |\n+--+"
    width = max((len(line) for line in stripped_lines), default=0)
    border = "+" + "-" * (width + 2) + "+"
    boxed_lines = [
        f"| {line.ljust(width)} |" if line else "|" + " " * (width + 2) + "|"
        for line in stripped_lines
    ]
    return f"{border}\n" + "\n".join(boxed_lines) + f"\n{border}"


def getch():
    return msvcrt.getch().decode("utf-8")


def getchar(d, arg):
    return d.get(arg, d["DEFAULTS"][arg])


def clsscr(*args):
    system("cls" if os.name == "nt" else "clear")
