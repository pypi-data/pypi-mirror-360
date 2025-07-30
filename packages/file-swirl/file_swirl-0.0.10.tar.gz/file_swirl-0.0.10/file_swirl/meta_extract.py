"""
Module contains logic for meta extraction
"""
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional

import exifread

from file_swirl.constants import DATE_FIELDS, FILE_EXTENSIONS
from file_swirl.file_structs import FileDate
from file_swirl.utils import is_valid_date


class MetaExtract:
    """
    Use this class as meta extrcing functions
    """

    @staticmethod
    def get_date_taken(file_path: str) -> Optional[FileDate]:
        """
        Extracts file data information from exif file method
        """
        file_data = None
        try:
            with open(file_path, 'rb') as f:
                tags = exifread.process_file(f)
                date_taken = tags.get('EXIF DateTimeOriginal') or tags.get('Image DateTime')
                if date_taken is not None:
                    date_taken = date_taken.values[0:10].split(':')
                    file_data = FileDate(
                        year=date_taken[0],
                        month=date_taken[1].zfill(2),
                        day=date_taken[2].zfill(2),
                    )

        except Exception as e:
            print(f'Error {e} tried to read = {file_path}')

        return file_data

    @staticmethod
    def get_date_from_meta(meta_data: dict) -> Optional[FileDate]:
        """
        Extract date details from meta data
        # DateTimeOriginal-jpg, SubSecDateTimeOriginal-heic, MediaCreateDate - mp4
        """
        file_data = None

        taken_date = None
        for key in DATE_FIELDS:
            taken_date = meta_data[0].get(key)
            if taken_date:
                # print(f"[INFO] Found date in {key}: {taken_date}")
                break

        if taken_date is not None:
            taken_date = taken_date[0:10].split(':')
            file_data = FileDate(
                year=taken_date[0],
                month=taken_date[1],
                day=taken_date[2]
            )

        return file_data

    @staticmethod
    def get_file_creation_date(file_path: Path) -> FileDate:
        """
        from file properties get file creation date
        """
        timestamp = file_path.stat().st_ctime
        file_date_created= datetime.fromtimestamp(timestamp)
        return FileDate(
            year= str(file_date_created.year),
            month= str(file_date_created.month).zfill(2),
            day= str(file_date_created.day).zfill(2)
        )

    @staticmethod
    def get_file_name_date(file_path: Path) -> Optional[FileDate]:
        """
        In case meta data is not found use this function
        to extract file data from file name using regex
        """
        filename = file_path.name
        regex_file_name_patterns = {
            rf".*?(\d{{4}})(\d{{2}})(\d{{2}}).*?\.({FILE_EXTENSIONS})$": (1, 2, 3),
            r"(IMG[_-]|IMG|PXL_)?(\d{4})(\d{2})(\d{2}).*?\.(jpg|jpeg|png|gif|heic|mov)" : (2,3,4),
            r"(VIDEO_|VID_|PXL_)?(\d{4})(\d{2})(\d{2}).*?\.(mp4|mov|mvk|avi|3gp|mts)" : (2,3,4),
        }

        for pattern, group_indexs in regex_file_name_patterns.items():
            match = re.search(pattern, filename, flags=re.IGNORECASE)
            if match and is_valid_date(
                    year= match.group(group_indexs[0]),
                    month=match.group(group_indexs[1]),
                    day=match.group(group_indexs[2])
                ):
                return FileDate(
                    year= match.group(group_indexs[0]),
                    month=match.group(group_indexs[1]),
                    day=match.group(group_indexs[2])
                )

        return None

    @staticmethod
    def get_metadata(input_file_path: Path, save_json:bool = False) -> dict:
        """
        Extract file meta data through exiftool
        """
        command = ['exiftool', '-json', input_file_path]
        result = subprocess.run(command, capture_output=True, text=True, check=True)

        metadata = {}
        if result.stdout and result.returncode == 0:
            # Parse the JSON output
            metadata = json.loads(result.stdout)

            if save_json:
                fil_path = input_file_path / 'meta_data.json'
                with open(fil_path, mode='w', encoding='UTF-8') as f:
                    json_data = json.dumps(metadata, indent=4)
                    f.write(json_data)

        return metadata

    @staticmethod
    def extract_gps_from_meta(meta_data: dict):
        """
        lat = "78 deg 58' 12.59\" N"
        lon = 2 deg 49' 7.71\" E"
        """
        def dms_to_decimal(dms_str: str) -> float:
            match = re.match(r"(\d+) deg (\d+)' ([\d.]+)\" ([NSEW])", dms_str)
            if not match:
                raise ValueError("Invalid DMS format")

            deg, minutes, seconds, direction = match.groups()
            decimal = float(deg) + float(minutes)/60 + float(seconds)/3600
            if direction in ['S', 'W']:
                decimal *= -1
            return decimal

        try:
            lat = meta_data[0].get("GPSLatitude")
            lon = meta_data[0].get("GPSLongitude")
            lat = dms_to_decimal(dms_str=lat)
            lon = dms_to_decimal(dms_str=lon)

        except Exception as e:
            print(e)
            return None

        return None

    @staticmethod
    def extract_coordinates_from_name(name: str):
        match = re.search(r'(-?\d+\.\d+)[_,-](-?\d+\.\d+)', name)
        if match:
            return float(match.group(1)), float(match.group(2))
        return None

    @staticmethod
    def extract_coordinates_from_file(file: Path):
        try:
            content = file.read_text(errors='ignore')
            match = re.search(r'(-?\d+\.\d+)[,\s:]+(-?\d+\.\d+)', content)
            if match:
                return float(match.group(1)), float(match.group(2))
        except Exception as e:
            print(e)
        return None
