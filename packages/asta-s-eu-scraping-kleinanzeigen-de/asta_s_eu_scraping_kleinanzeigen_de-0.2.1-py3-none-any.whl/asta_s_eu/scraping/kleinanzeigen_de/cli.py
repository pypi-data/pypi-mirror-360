"""Command line interface module"""
import argparse

from . import VERSION


def cli() -> None :
    """Command line interface function"""
    parser = argparse.ArgumentParser()
    # Add global version option
    parser.add_argument(
        '-v', '--version',
        action='version',
        version=f"%(prog)s {VERSION}",
        help="Show program's version number and exit."
    )

    subparsers = parser.add_subparsers(dest='command', required=True)

    subparsers.add_parser('search-all', help='Search all items')

    subparsers.add_parser('follow-person', help='Follow a person')

    args = parser.parse_args()

    from .ciur import (  # pylint: disable=import-outside-toplevel
        follow_person, search_all)

    if args.command == 'search-all':
        search_all()
    elif args.command == 'follow-person':
        follow_person()


if __name__ == "__main__":
    cli()
