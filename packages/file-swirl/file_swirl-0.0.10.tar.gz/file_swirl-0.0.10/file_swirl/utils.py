"""
Store utils methods
"""
import math
from datetime import datetime
from functools import wraps
from os import sep as file_sep
from pathlib import Path
from typing import Callable, Generator, Set

from file_swirl.constants import FILE_EXTENSIONS_MAP


def memo_file(seen: Set = None):
    if seen is None:
        seen = set()

    def decorator(fn: Callable[[Path], Generator[Path, None, None]]):
        @wraps(fn)
        def wrapper(path: Path, *args, **kwargs):
            for result in fn(path, *args, **kwargs):
                try:
                    fid = (result.stat().st_dev, result.stat().st_ino)
                except Exception:
                    continue

                if fid not in seen:
                    seen.add(fid)
                    yield result
        return wrapper
    return decorator

def is_valid_date(year, month, day):
    try:
        datetime(int(year), int(month), int(day))
        return True
    except (ValueError, TypeError):
        return False

def convert_size(size_bytes: int) -> str:
    """
    Converts bytes to nearest read-able words
    """
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"

def get_date_subpath(creation_date: datetime, sep: str = file_sep) -> str:
    """
    Returns a subpath string like 'YYYY/MM/DD' based on the given datetime object.

    Args:
        creation_date (datetime): The datetime to format.
        sep (str): The path separator to use (default is OS-specific).

    Returns:
        str: A formatted path string like '2025/06/26'.
    """
    return f"{creation_date.year}{sep}{creation_date.month:02}{sep}{creation_date.day:02}"

def get_category(extension: str) -> str:
    for category, exts in FILE_EXTENSIONS_MAP.items():
        if extension.lower() in exts:
            return category
    return 'NEW'

