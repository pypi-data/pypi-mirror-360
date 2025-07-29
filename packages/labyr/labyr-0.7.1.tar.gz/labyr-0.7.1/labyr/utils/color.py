"""The Color module for labyr"""

__all__ = ["C"]

from colorama import Fore, Style, init


class C:
    def __init__(self) -> None:
        init(autoreset=True)  # Ensures colors reset automatically after each print

    # Foreground colors
    @staticmethod
    def red(text: str) -> str:
        return f"{Fore.RED}{text}{Style.RESET_ALL}"

    @staticmethod
    def green(text: str) -> str:
        return f"{Fore.GREEN}{text}{Style.RESET_ALL}"

    @staticmethod
    def brown(text: str) -> str:
        return f"{Fore.YELLOW}{text}{Style.RESET_ALL}"  # Brown is often represented as yellow

    @staticmethod
    def blue(text: str) -> str:
        return f"{Fore.BLUE}{text}{Style.RESET_ALL}"

    @staticmethod
    def purple(text: str) -> str:
        return f"{Fore.MAGENTA}{text}{Style.RESET_ALL}"

    @staticmethod
    def cyan(text: str) -> str:
        return f"{Fore.CYAN}{text}{Style.RESET_ALL}"

    @staticmethod
    def light_gray(text: str) -> str:
        return f"{Fore.LIGHTBLACK_EX}{text}{Style.RESET_ALL}"

    @staticmethod
    def dark_gray(text: str) -> str:
        return f"{Fore.LIGHTBLACK_EX}{text}{Style.RESET_ALL}"

    @staticmethod
    def light_red(text: str) -> str:
        return f"{Fore.LIGHTRED_EX}{text}{Style.RESET_ALL}"

    @staticmethod
    def light_green(text: str) -> str:
        return f"{Fore.LIGHTGREEN_EX}{text}{Style.RESET_ALL}"

    @staticmethod
    def light_blue(text: str) -> str:
        return f"{Fore.LIGHTBLUE_EX}{text}{Style.RESET_ALL}"

    @staticmethod
    def light_purple(text: str) -> str:
        return f"{Fore.LIGHTMAGENTA_EX}{text}{Style.RESET_ALL}"

    @staticmethod
    def light_cyan(text: str) -> str:
        return f"{Fore.LIGHTCYAN_EX}{text}{Style.RESET_ALL}"

    @staticmethod
    def light_white(text: str) -> str:
        return f"{Fore.LIGHTWHITE_EX}{text}{Style.RESET_ALL}"

    @staticmethod
    def yellow(text: str) -> str:
        return f"{Fore.YELLOW}{text}{Style.RESET_ALL}"

    # Text styles
    @staticmethod
    def bold(text: str) -> str:
        return f"{Style.BRIGHT}{text}{Style.RESET_ALL}"

    @staticmethod
    def faint(text: str) -> str:
        return f"{Style.DIM}{text}{Style.RESET_ALL}"

    @staticmethod
    def italic(text: str) -> str:
        return f"\033[3m{text}\033[0m"  # ANSI escape code for italic

    @staticmethod
    def underline(text: str) -> str:
        return f"\033[4m{text}\033[0m"  # ANSI escape code for underline

    @staticmethod
    def blink(text: str) -> str:
        return f"\033[5m{text}\033[0m"  # ANSI escape code for blink

    @staticmethod
    def negative(text: str) -> str:
        return f"\033[7m{text}\033[0m"  # ANSI escape code for negative

    @staticmethod
    def crossed(text: str) -> str:
        return f"\033[9m{text}\033[0m"  # ANSI escape code for crossed-out text


# Handle non-TTY environments and Windows VT mode
if not __import__("sys").stdout.isatty():
    for name in dir(C):
        if not name.startswith("_") and callable(getattr(C, name)):
            setattr(C, name, lambda text: text)  # Replace methods with no-op lambdas
else:
    if __import__("platform").system() == "Windows":
        kernel32 = __import__("ctypes").windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        del kernel32


# class Colors:
#     """ANSI color codes"""
#
#     BLACK = "\033[0;30m"
#     RED = "\033[0;31m"
#     GREEN = "\033[0;32m"
#     BROWN = "\033[0;33m"
#     BLUE = "\033[0;34m"
#     PURPLE = "\033[0;35m"
#     CYAN = "\033[0;36m"
#     LIGHT_GRAY = "\033[0;37m"
#     DARK_GRAY = "\033[1;30m"
#     LIGHT_RED = "\033[1;31m"
#     LIGHT_GREEN = "\033[1;32m"
#     YELLOW = "\033[1;33m"
#     LIGHT_BLUE = "\033[1;34m"
#     LIGHT_PURPLE = "\033[1;35m"
#     LIGHT_CYAN = "\033[1;36m"
#     LIGHT_WHITE = "\033[1;37m"
#     BOLD = "\033[1m"
#     FAINT = "\033[2m"
#     ITALIC = "\033[3m"
#     UNDERLINE = "\033[4m"
#     BLINK = "\033[5m"
#     NEGATIVE = "\033[7m"
#     CROSSED = "\033[9m"
#     END = "\033[0m"
#
#     # cancel SGR codes if we don't write to a terminal
#     if not __import__("sys").stdout.isatty():
#         for _ in dir():
#             if isinstance(_, str) and _[0] != "_":
#                 locals()[_] = ""
#     else:
#         # set Windows console in VT mode
#         if __import__("platform").system() == "Windows":
#             kernel32 = __import__("ctypes").windll.kernel32
#             kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
#             del kernel32
