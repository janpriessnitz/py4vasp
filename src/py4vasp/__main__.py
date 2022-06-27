import argparse
import sys
from py4vasp.raw import _contract

parser = argparse.ArgumentParser(
    prog="python -m py4vasp",
    description="A helper tool for the command line.",
)
parser.add_argument("--example", nargs="+", type=str)
parser.add_argument("--foo")


def main(args):
    print(args)
    args = parser.parse_args(args)
    print(args)
    if args.example:
        _contract.example(args.example)


if __name__ == "__main__":
    main(sys.argv[1:])
