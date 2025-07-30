#!/usr/bin/python

import csv
import sys
from pathlib import Path
from typing import List, Optional, Tuple

import click

from .. import __version__, __version_message__


@click.command(
    help="""
Read the specified file and write out just the specified columns to stdout.

The column_spec is a comma separated list of column headers, column indexes (one-based),
or column ranges (e.g. 4-6 for columns 4 through 6 inclusive).

If no file_to_read is specified, then input is read from stdin.
"""
)
@click.option(
    "-d", "--delimiter", type=str, help="column delimiter (default=TAB)", default="\t"
)
@click.option(
    "-o",
    "--output-delimiter",
    type=str,
    help="output column delimiter (default=input delimiter)",
)
@click.version_option(__version__, message=__version_message__)
@click.argument("column_spec", type=str, required=True)
@click.argument("file_to_read", type=click.Path(exists=True), required=False)
def getcol(
    column_spec: str,
    file_to_read: Optional[Path] = None,
    delimiter: str = "\t",
    output_delimiter: Optional[str] = None,
) -> None:
    if output_delimiter is None:
        output_delimiter = delimiter
    column_list, includes_headers = _parse_column_spec(column_spec)
    writer = csv.writer(sys.stdout, delimiter=output_delimiter)
    try:
        fh = sys.stdin
        if file_to_read is not None:
            fh = open(file_to_read)
        reader = csv.reader(fh, delimiter=delimiter)

        for irow, row in enumerate(reader):
            if irow == 0 and includes_headers:
                column_list = _process_headers(column_list, row)
            output_row = [row[int(i)] for i in column_list]
            writer.writerow(output_row)
    finally:
        if fh is not None:
            fh.close()


def _parse_column_spec(column_spec: str) -> Tuple[List[str | int], bool]:
    column_list: List[str | int] = []
    includes_headers = False
    for spec in column_spec.split(","):
        if "-" in spec:
            range_parts = spec.split("-", 1)
            if (
                len(range_parts) == 2
                and range_parts[0].isnumeric()
                and range_parts[1].isnumeric()
            ):
                column_list.extend(range(int(range_parts[0]) - 1, int(range_parts[1])))
            else:
                column_list.append(spec)
                includes_headers = True
        elif spec.isnumeric():
            column_list.append(int(spec) - 1)
        else:
            column_list.append(spec)
            includes_headers = True
    return column_list, includes_headers


def _process_headers(
    column_list: List[str | int], headers: List[str]
) -> List[str | int]:
    updated_column_list: List[str | int] = []
    for col in column_list:
        if isinstance(col, str):
            try:
                updated_column_list.append(headers.index(col))
            except ValueError:
                pass
        elif isinstance(col, int):
            updated_column_list.append(col)
    return updated_column_list


if __name__ == "__main__":
    getcol()  # pragma: no cover
