
import argparse
import subprocess
import time
from pathlib import Path

from dateutil import parser

from file_swirl.constants import FILE_EXTENSIONS


class FileUpdate:

    def __init__(self, input_folders, file_extensions, update_date) -> None:
        self.input_folders = input_folders
        self.file_extensions = file_extensions
        self.total_counter = 0
        self.update_date = parser.parse(update_date).strftime('%Y:%m:%d %H:%M:%S')

    def update_exif_metadata(self, file_path):
        """
        Update the creation and modification date metadata of a file using ExifTool.

        :param file_path: Path to the image or video file
        :param creation_time: New creation date (optional, in datetime format)
        :param modification_time: New modification date (optional, in datetime format)
        """

        # Prepare the ExifTool command to update the metadata
        command = ['exiftool', '-overwrite_original']

        command.append(f'-DateTimeOriginal="{self.update_date}"')  # Set creation date

        command.append(f'-FileModifyDate="{self.update_date }"')  # Set modification date

        # Add the file to the command
        command.append(file_path)

        # Run the ExifTool command using subprocess
        try:
            subprocess.run(command, check=True)
            print(f"Updated metadata for {file_path}")
            self.total_counter += 1

        except subprocess.CalledProcessError as e:
            print(f"Error updating metadata for {file_path}: {e}")

    def process_folder_with_exiftool(self, input_folder):
        """
        Process all files in the folder and update metadata using ExifTool.

        :param folder_path: Path to the folder
        :param creation_time: New creation date (optional, in datetime format)
        :param modification_time: New modification date (optional, in datetime format)
        """
        for file_path in input_folder.rglob("**/*"):
            if file_path.is_file() and file_path.suffix.lower() in self.file_extensions:
                self.update_exif_metadata(file_path)

    def print_result(self):
        print(f"\n{'#'*15} Processing Completed {'#'*15}")
        print(self.total_counter)

    def process_files(self):
        for input_folder in self.input_folders:
            self.process_folder_with_exiftool(input_folder= Path(input_folder))

        self.print_result()


def main():
    args_parser = argparse.ArgumentParser(description='WIP')
    # Add the input & output path argument
    args_parser.add_argument(
        '--input_folders', nargs='+', required=True, type=str,
        help='Path to the input file'
    )
    args_parser.add_argument(
        '--update_date', type=str, required=True,
        help='Update the file creation & update date'
    )
    args_parser.add_argument(
        '--file_extensions', nargs='+', type=str, default=FILE_EXTENSIONS,
        help='Select given file extensions, will override existing extensions'
    )

    # Parse the command-line arguments
    args = args_parser.parse_args()

    start_time = time.time()

    # Process the folder and update metadata for all files
    file_update = FileUpdate(
        input_folders= args.input_folders,
        file_extensions= args.file_extensions,
        update_date = args.update_date
    )
    file_update.process_files()

    end_time = time.time()
    runtime = end_time - start_time
    print("\n\nRuntime: {:.2f} seconds".format(runtime))

# Example usage :
# python -m file_update --input_folders "D:\Mushroom" --update_date "2024-08-08"
if __name__ == "__main__":
    main()

