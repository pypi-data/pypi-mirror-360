import argparse

from teklia_yolo.extract import add_extract_parser


def main():
    parser = argparse.ArgumentParser(prog="YOLO")

    # To add a sub-command, you can un-comment this snippet
    # More information on https://docs.python.org/3/library/argparse.html#sub-commands
    commands = parser.add_subparsers()
    add_extract_parser(commands)

    args = vars(parser.parse_args())
    if "func" in args:
        args.pop("func")(**args)
    else:
        parser.print_help()
