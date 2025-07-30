import argparse
from salute.cli.actions import InitScenarioAction


def command():
    parser = argparse.ArgumentParser(
        description="Salute CLI tool for managing your application"
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="%(prog)s 0.7.4",
        help="Show program's version number and exit",
    )
    parser.add_argument(
        "-i",
        "--init",
        action=InitScenarioAction,
        help="Execute init scenario to prepare your application",
        nargs=0,
    )

    args = parser.parse_args()

    if not any(vars(args).values()):
        parser.print_help()
        return
