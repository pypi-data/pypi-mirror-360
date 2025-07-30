#!/usr/bin/python

import csv
import logging
import sys
from typing import Dict, Iterable, List, Optional, TextIO

import click
import click_logging

from .. import __version__, __version_message__

logger = logging.getLogger(__name__)
click_logging.basic_config(logger)


@click.command(
    help="""
Merge the specified delimited files with column headings, joining entries with
the same key field value.

The files do not need to be sorted on the key field as with join(1). This does
require that all of the data be read into memory. If that is a problem, using
the system join(1) command is recommended.

Rows will be printed in the order that the unique key values are encountered
when reading through the input files.

To read from stdin, use '-' as the filename.

The output key column will be the first column of the output file and the
header will be the header from the first file.

If -k is used to specify alternative keys columns for subsequent files, but
those files have a column with the same name as the output key column, that
will be ignored.
"""
)
@click_logging.simple_verbosity_option(logger)
@click.option(
    "-d", "--delimiter", type=str, help="column delimiter (default=TAB)", default="\t"
)
@click.option(
    "-o",
    "--output-delimiter",
    type=str,
    help="output column delimiter (default=input delimiter)",
)
@click.option(
    "--all-delimiter",
    type=str,
    help='when keep=="all" this will be the delimiter between entries where there are multiple '
    '(default=";")',
    default=";",
)
@click.option(
    "-k",
    "--key-column",
    type=str,
    help="comma separated list of key column identifiers. "
    "each new file will use the next identifier. "
    "the last identifier will be used for all remaining files, "
    'so just use "-k identifier" if the identifier is the same for all files. '
    "The identifier can either be the header string or the one-based column index. "
    "(default=1 (i.e. the first column of each file))",
    default="1",
)
@click.option(
    "--keep",
    type=click.Choice(["first", "last", "uniq", "all"], case_sensitive=False),
    default="all",
    help="specifies how to handle multiple values for the same field with the same key",
)
@click.option(
    "-I",
    "--ignore",
    type=str,
    help="comma separated list of column identifiers to ignore",
)
@click.version_option(__version__, message=__version_message__)
@click.argument("files_to_read", nargs=-1, type=click.File("r"), required=False)
def merge(
    files_to_read: Iterable[TextIO] = (),
    key_column: str = "1",
    delimiter: str = "\t",
    output_delimiter: Optional[str] = None,
    keep: str = "all",
    all_delimiter: str = ";",
    ignore: str | None = None,
) -> None:
    if output_delimiter is None:
        output_delimiter = delimiter
    key_column_list = key_column.split(",")
    ignore_set = set()
    if ignore is not None:
        ignore_set.update(ignore.split(","))

    data: Dict[str, Dict[str, str]] = {}
    output_key = None
    data_field_list = []
    for ifile, fh in enumerate(files_to_read):
        logger.debug('processing file "%s"', fh.name)
        if ifile >= len(key_column_list):
            ifile = -1
        key = key_column_list[ifile]
        reader = csv.DictReader(fh, delimiter=delimiter)
        if reader.fieldnames is None:
            logger.warning('No fieldnames found in file "%s", skipping file.', fh.name)
            continue
        this_data_field_list = [x for x in reader.fieldnames if x not in ignore_set]
        if key.isnumeric():
            key = this_data_field_list[int(key) - 1]
        elif key not in this_data_field_list:
            logger.warning(
                'Key "%s" not found in file "%s", skipping file.', key, fh.name
            )
            continue
        logger.debug('...using key "%s"', key)
        this_data_field_list.remove(key)
        if output_key is None:
            output_key = key
            data_field_list.append(output_key)
        if output_key in this_data_field_list:
            this_data_field_list.remove(output_key)
        _process_rows(
            reader,
            fh.name,
            key,
            output_key,
            keep,
            all_delimiter,
            this_data_field_list,
            data,
        )
        data_field_list.extend(
            [x for x in this_data_field_list if x not in data_field_list]
        )

    logger.debug("writing output")
    writer = csv.DictWriter(
        sys.stdout, fieldnames=data_field_list, delimiter=output_delimiter
    )
    writer.writeheader()
    writer.writerows(data.values())


def _process_rows(
    reader: csv.DictReader,
    fname: str,
    key: str,
    output_key: str,
    keep: str,
    all_delimiter: str,
    data_field_list: List[str],
    data: Dict[str, Dict[str, str]],
) -> None:
    irow = 0
    for irow, row in enumerate(reader):
        key_value = row.get(key, None)
        if key_value is None or len(key_value) == 0:
            logger.warning(
                'No key value found for line %d in file "%s", skipping line.',
                irow + 2,
                fname,
            )
            continue
        if key_value not in data:
            data[key_value] = {output_key: key_value}
        entry = data[key_value]
        _process_row(row, data_field_list, keep, all_delimiter, entry)

    logger.debug("...processed %d entries", irow + 1)
    logger.debug("...total unique entries is now %d", len(data))


def _process_row(
    row: Dict[str, str],
    data_field_list: List[str],
    keep: str,
    all_delimiter: str,
    entry: Dict[str, str],
) -> None:
    for data_field in data_field_list:
        data_value = row[data_field]
        if data_value is None or len(data_value) == 0:
            pass
        elif data_field not in entry or keep == "last":
            entry[data_field] = data_value
        elif keep == "all":
            entry[data_field] += all_delimiter
            entry[data_field] += data_value
        elif keep == "uniq":
            if data_value not in entry[data_field].split(all_delimiter):
                entry[data_field] += all_delimiter
                entry[data_field] += data_value
        else:  # keep == 'first' so ignore subsequent values
            pass


if __name__ == "__main__":
    merge()  # pragma: no cover
