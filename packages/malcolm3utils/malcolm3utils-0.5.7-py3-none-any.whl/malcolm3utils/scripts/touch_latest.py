#!/usr/bin/python

import os
from collections.abc import Iterable
from fnmatch import fnmatch
from pathlib import Path

import click

from .. import __version__, __version_message__

# be sure to update docstring if you change DEFAULT_IGNORE_GLOBS
DEFAULT_IGNORE_GLOBS = ["*~", "*.pyc", "#*", ".*", "*.OLD", "OLD"]


@click.command()
@click.option(
    "-i",
    "--ignore",
    "ignore_patterns",
    multiple=True,
    type=str,
    help="glob patterns to ignore (likely needs to be quoted, and can be repeated)",
)
@click.option(
    "-f",
    "--ignore-file",
    "ignore_pattern_files",
    multiple=True,
    type=click.Path(exists=True),
    help="file with glob patterns (one per line) to ignore (can be repeated)",
)
@click.option(
    "-n", "--no-default-ignore", is_flag=True, help="do not use default ignore globs"
)
@click.version_option(__version__, message=__version_message__)
@click.argument("touch_file", type=str)
@click.argument("paths_to_check", nargs=-1, type=click.Path(exists=True), required=True)
def touch_latest(
    touch_file: str,
    paths_to_check: list[str | Path],
    ignore_patterns: Iterable[str] = (),
    ignore_pattern_files: Iterable[str | Path] = (),
    no_default_ignore: bool = False,
) -> None:
    """
    Find the latest changed date of file under the specified PATHS_TO_CHECK
    and touch the TOUCH_FILE with that date (creating it if necessary).

    Files that match ignore patterns will be ignored when locating searching
    for the file with the latest change date.
    Patterns that contain slashes either need to be absolute (i.e. start
    with a slash) or they need to start with an asterisk in order
    to match anything. So any such pattern that doesn't have either
    will have an asterisk prepended.

    Directories which match an ignore pattern will not be traversed.
    Paths can be specified to ignore only from specific directories,
    e.g. '*/test/*.out'.

    Default ignore globs: '*~', '*.pyc', '#*', '.*' '*.OLD' 'OLD'

    \b
    touch_file: file to be touchead with the latest date
    paths_to_check: paths to search for the latest change date
    \f

    :param touch_file: file to be touchead with the latest date
    :param paths_to_check: paths to search for the latest change date
    :param ignore_patterns: glob patterns to ignore
    :param ignore_pattern_files: files of glob patterns to ignore
    :param no_default_ignore: if True do not include default glob patterns

    """
    all_ignore_patterns = IgnorePatterns()

    if not no_default_ignore:
        all_ignore_patterns.add_patterns(DEFAULT_IGNORE_GLOBS)
    for fn in ignore_pattern_files:
        with open(fn) as fh:
            all_ignore_patterns.add_patterns(fh)
    all_ignore_patterns.add_patterns(ignore_patterns)

    latest_timestamp = 0

    for path in paths_to_check:
        apath = os.path.abspath(path)
        for root, dirs, files in os.walk(apath):
            dirs[:] = [dn for dn in dirs if not all_ignore_patterns.ignore(root, dn)]
            for fn in files:
                if not all_ignore_patterns.ignore(root, fn):
                    statinfo = os.stat(os.path.join(root, fn))
                    if statinfo.st_mtime > latest_timestamp:
                        latest_timestamp = int(statinfo.st_mtime)
    if not os.path.exists(touch_file):
        with open(touch_file, "w"):
            pass
    os.utime(touch_file, (latest_timestamp, latest_timestamp))


class IgnorePatterns:
    """
    Class to handle checking glob patterns to be ignored
    """

    def __init__(self, patterns: Iterable[str] = ()) -> None:
        self.names: list[str] = []
        self.paths: list[str] = []
        self.add_patterns(patterns)

    def add_patterns(self, patterns: Iterable[str]) -> None:
        """
        Add these patterns to the list of glob patterns to be ignored.

        Whitespace is stripped from the ends of each pattern since they may have been read from a file.

        Patterns that contain a '/' must either start with a '/' (i.e. be absolute), of start
        with a '*', or there is no chance of a match.
        Accordingly, patterns that contain a '/' and start with something else have '*' prepended to them.

        :param patterns: list of glob patterns to be ignored
        :return: None
        """
        for pattern in patterns:
            pattern = pattern.strip()
            if "/" in pattern:
                if pattern[0] not in "/*":
                    pattern = "*" + pattern
                self.paths.append(pattern)
            else:
                self.names.append(pattern)

    def ignore(self, dn: str, fn: str) -> bool:
        """
        Check to see whether to exclude the file named fn in directory namded dn
        should be ignored or not.

        :param dn: directory name
        :param fn: file name
        :return: True if the path matches an ignore pattern, False otherwise
        """
        for ignore_name in self.names:
            if fnmatch(fn, ignore_name):
                return True
        path = os.path.join(dn, fn)
        for ignore_path in self.paths:
            if fnmatch(path, ignore_path):
                return True
        return False


if __name__ == "__main__":
    touch_latest()  # pragma: no cover
