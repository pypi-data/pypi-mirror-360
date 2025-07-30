from duneflow.ops.reader._get_html import get_html
from duneflow.ops.reader._scraper import TableScraperActor, TableScraperArgs
from duneflow.ops.reader._table_file_reader import (
    RawCell,
    RawTable,
    read_table_from_file,
)

__all__ = [
    "TableScraperActor",
    "TableScraperArgs",
    "read_table_from_file",
    "RawTable",
    "RawCell",
    "get_html",
]
