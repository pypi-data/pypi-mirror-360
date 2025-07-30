from pathlib import Path
from unittest.mock import patch

import pytest

from file_swirl.file_structs import FileDate
from file_swirl.meta_extract import MetaExtract


@pytest.mark.parametrize("filename,expected", [
    ("20240708_image.jpg", FileDate("2024", "07", "08")),
    ("IMG_20230701_120000.jpg", FileDate("2023", "07", "01")),
    ("PXL_20220115_123456789.mp4", FileDate("2022", "01", "15")),
    ("VID_20191231_235959.avi", FileDate("2019", "12", "31")),
    ("VID_20190230_235959.avi", None),  # Invalid date
    ("randomfile.txt", None),
    ("IMG_2024ABCD.jpg", None),
])
@patch("file_sort.meta_extract.is_valid_date")
def test_get_file_name_date(mock_is_valid_date, filename, expected):
    # Setup mock
    if expected:
        mock_is_valid_date.return_value = True
    else:
        mock_is_valid_date.return_value = False

    file_path = Path(filename)
    result = MetaExtract.get_file_name_date(file_path)

    if expected:
        assert result == expected
    else:
        assert result is None
