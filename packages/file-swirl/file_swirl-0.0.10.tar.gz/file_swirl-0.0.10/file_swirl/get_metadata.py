"""
command:
    > python media_metadata.py --input_path  E:\\src\\IMG_4267.HEIC
    python media_metadata.py --input_path E:\\src\\IMG20250406135334.jpg
"""

import argparse
import json
import subprocess
from pathlib import Path


def get_metadata(input_file_path, output_file_path):

    """
    Extract file meta data through exiftool and saves it into json
    """


    command = ['exiftool', '-json', input_file_path]
    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode == 0:
        # Parse the JSON output
        metadata = json.loads(result.stdout)

        # DateTimeOriginal-jpg, SubSecDateTimeOriginal-heic, MediaCreateDate - mp4
        taken_date = metadata[0].get('DateTimeOriginal') or\
            metadata[0].get('SubSecDateTimeOriginal') or\
            metadata[0].get('MediaCreateDate')

        lat = metadata[0].get("GPSLatitude")
        lon = metadata[0].get("GPSLongitude")
        make = metadata[0].get("Make")
        model = metadata[0].get("Model")
        print("Taken Date:", taken_date)
        print("GPS Data: {lat} | {lon}", )
        print(f"Make:{make} model: {model} ")


        with open(output_file_path, mode='w', encoding='utf-8') as f:
            json_data = json.dumps(metadata, indent=4)
            f.write(json_data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Media metadata')

    # Add the input & output path argument
    parser.add_argument(
        '--input_path', required=True, type=str,
        help='Path to the input file'
    )
    parser.add_argument(
        '--output_path', type=str, required=False, default="{file_name}_metadata",
        help='Path to the output file to store json'
    )

    args = parser.parse_args()
    input_path = Path(args.input_path)
    if input_path.exists():
        if 'metadata' in args.output_path:
            file_name_json = input_path.parts[-1].rsplit('.')[0]
            output_path = args.output_path.format(
                file_name= file_name_json
            )
            output_path = f"{output_path}.json"
        output_path = Path(output_path)
        get_metadata(input_path, output_path)
    else:
        print("Path does not exist:", input_path)

