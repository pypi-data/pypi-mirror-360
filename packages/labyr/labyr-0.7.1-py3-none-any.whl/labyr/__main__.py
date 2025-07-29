import argparse
import hashlib
import os
from importlib.metadata import PackageNotFoundError, version


def get_version():
    try:
        return version("labyr")
    except PackageNotFoundError:
        return "unknown"


def run_labyr(level=None):
    from .__init__ import labyr

    labyr(level=level)


def hash_secret(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def dev_test():
    if (
        os.environ.get("DEV_TEST_KEY", "")
        == "9e0fa8e2ae379dc69e30b77507f50075f6d627487f10275a87e3d9c32ac72d71"
    ):
        print("success authentication")


def main():
    parser = argparse.ArgumentParser(
        description="labyr: a labyrinth game || DISCLAIMER: if you run labyr, each frame will clear the terminal screen."
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"labyr {get_version()}",
        help="Show labyr version",
    )
    parser.add_argument(
        "-l",
        "--level",
        type=int,
        metavar="x",
        help="Set the labyrinth level (number)",
    )
    parser.add_argument("--devtest", action="store_true", help="devtest")
    parser.add_argument(
        "action",
        choices=["run", "nil"],
        nargs="?",
        help="Action to perform. Allowed values: run, nil",
    )
    args = parser.parse_args()
    if args.devtest:
        dev_test()
        return
    if not args.action:
        parser.error("the following arguments are required: action")
    actions = {"run": lambda: run_labyr(level=args.level), "nil": lambda: None}
    actions[args.action]()


if __name__ == "__main__":
    main()
