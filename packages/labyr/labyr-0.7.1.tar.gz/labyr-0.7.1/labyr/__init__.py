from os import _exit
from threading import Thread
from time import sleep as tsleep
from typing import Any, Callable, Union

from .utils import box, clsscr, color, getch, getchar
from .utils.entity import EntMan, Player, handlemove
from .utils.fill import fill_rect
from .utils.transform import get_map, transform

__all__ = ["labyr", "LabyrGame"]


def genlvls(
    chars: dict,
    lvlSizes: dict[int, tuple[int, int]],
):
    out = {}

    def init(dimen: tuple[int, int]) -> list[list[str]]:
        space = getchar(chars, "space")[0]
        x, y = dimen
        grid = [[space] * x for _ in range(y)]

        for i in range(x):
            for j in range(y):
                if i == 0 or i == x - 1 or j == 0 or j == y - 1:
                    grid[j][i] = "#"

        return grid

    for lvl, dimen in lvlSizes.items():
        out[lvl] = init(dimen)

    # lvl configs
    # out[lvl][y][x]

    space_char = getchar(chars, "space")[0]
    wall_char = getchar(chars, "wall")[0]
    player_char = getchar(chars, "player")[0]
    exit_char = getchar(chars, "exit")[0]

    def set_chars(out, lvl, positions, char):
        for y, x in positions:
            out[lvl][y][x] = char

    level_defs = [
        # lvl 0 conf
        # #######
        # #@...E#
        # #######
        {"player": [(1, 1)], "exit": [(1, 5)], "walls": [], "spaces": []},
        # lvl 1 conf
        # ###########
        # #@......#E#
        # #######.#.#
        # #.......#.#
        # #.#######.#
        # #.........#
        # ###########
        {
            "player": [(1, 1)],
            "exit": [(1, -2)],
            "walls": [
                ((2, 1), (2, 6)),
                ((4, 2), (4, -3)),
                ((1, -3), (3, -3)),
            ],
            "spaces": [],
        },
        # lvl 2 conf
        # ...######...
        # ####....####
        # #@...##...E#
        # ####....####
        # ...######...
        {
            "player": [(2, 1)],
            "exit": [(2, -2)],
            "walls": [
                ((1, 1), (1, 3)),
                ((1, -4), (1, -2)),
                ((3, 1), (3, 3)),
                ((3, -4), (3, -2)),
                ((2, 5), (2, 6)),
            ],
            "spaces": [
                ((0, 0), (0, 2)),
                ((-1, 0), (-1, 2)),
                ((0, -3), (0, -1)),
                ((-1, -3), (-1, -1)),
            ],
        },
        # lvl 3 conf
        # ###########
        # #@...#..###
        # ###.#....E#
        # #.....#..##
        # ###########
        {
            "player": [(1, 1)],
            "exit": [(2, -2)],
            "walls": [
                ((2, 1), (2, 2)),
                ((2, 4), (2, 4)),
                ((1, 5), (1, 5)),
                ((3, 6), (3, 6)),
                ((3, -2), (3, -2)),
                ((1, -3), (1, -2)),
            ],
            "spaces": [],
        },
    ]

    for lvl, conf in enumerate(level_defs):
        set_chars(out, lvl, conf["player"], player_char)
        set_chars(out, lvl, conf["exit"], exit_char)
        for start, end in conf["walls"]:
            fill_rect(out[lvl], start, end, wall_char)
        for start, end in conf["spaces"]:
            fill_rect(out[lvl], start, end, space_char)

    return out


def cout_labyr(map: list[list[str]], chars: dict, clvl: int):
    chmap = get_map(chars)
    # dict(transform(["player", "exit", "wall", "space"], lambda arg: getch(chars, arg)))

    print("\n" + color.C.dark_gray(f"lvl: {clvl}"))
    for i in range(len(map)):
        for j in range(len(map[0])):
            cell = map[i][j]
            ch = cell[0]
            if ch != "$" and ch in chmap:
                print(chmap[ch](ch), end="")
            elif cell.startswith("$M"):  # e.g. str: "$M1" means monster #1
                print(chmap["M"]("M"), end="")
        print()


class LabyrGame:
    def __init__(self, *, level=0) -> None:
        c = color.C()
        self.clvl = level if level is not None else 0
        self.chars = {
            "DEFAULTS": {
                "space": (".", c.dark_gray),
                "wall": ("#", c.dark_gray),
                "player": ("@", c.blue),
                "exit": ("E", c.green),
                "monster": ("M", c.red),
            },
            "space": (".", c.dark_gray),
            "wall": ("#", c.dark_gray),
            "player": ("@", c.blue),
            "exit": ("E", c.green),
            "monster": ("M", c.red),
        }
        self.__lvlSizes = {0: (7, 3), 1: (11, 7), 2: (12, 5), 3: (11, 5)}
        self.levels = genlvls(self.chars, self.__lvlSizes)
        self.entman = EntMan(self.levels, self.chars)

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        running: bool = True
        cmap = self.levels[self.clvl]

        refresh = lambda: (  # noqa: E731
            clsscr(),
            cout_labyr(cmap, self.chars, self.clvl),
        )

        win = False

        player_char = getchar(self.chars, "player")[0]
        exit_char = getchar(self.chars, "exit")[0]
        while running:
            if win:
                clsscr()
                print(f"\n{box('YOU WONNNNN')}\n")
                _exit(0)
            else:
                refresh()
            move = getch().lower()

            if move in ["w", "a", "s", "d"]:
                out = handlemove(
                    self.chars, cmap, self.entman.get(self.clvl, "player"), move
                )
                if out == "ESCAPE":
                    refresh = lambda: (  # noqa: E731
                        clsscr(),
                        cout_labyr(cmap, self.chars, self.clvl),
                    )

                    nlvl = self.clvl + 1
                    if nlvl > max(self.__lvlSizes.keys()):
                        win = True
                        continue
                    else:
                        plyr = self.entman.get(self.clvl, "player")
                        x, y = plyr
                        refresh()
                        tsleep(0.3)
                        cmap[y][x] = exit_char
                        refresh()
                        tsleep(0.5)
                        self.clvl += 1
                        cmap = self.levels[self.clvl]
            elif move == "q":
                clsscr()
                _exit(0)


labyr = LabyrGame()
