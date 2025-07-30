import argparse
import time
from pathlib import Path

from file_swirl.constants import FILE_EXTENSIONS
from file_swirl.file_sorter import FileSorter
from file_swirl.file_structs import NestedOrder, ProcessType, ShiftType


def main():
    """
    cli execution starts here
    """
    args_parser = argparse.ArgumentParser(
        description='Organize files by keys with optional geo filter.'
    )

    # Add the input & output path argument
    args_parser.add_argument(
        '--input_paths', nargs='+', required=True, type=str,
        help='Path to the input file, can take multiple path as well.'
    )
    args_parser.add_argument(
        '--output_path', type=str, required=True,
        help='Path to the output file, default is current directory', default='.'
    )
    args_parser.add_argument(
        '--shift_type', type=str, choices=[e.value for e in ShiftType],
        default=ShiftType.COPY.value, help='Copy or Move?, default is copy'
    )
    args_parser.add_argument(
        '--file_extensions', nargs='+', type=str, default=FILE_EXTENSIONS,
        help='Select given file extensions, will override existing extensions'
    )
    args_parser.add_argument("--location", type=str, help="Groups files based on gps coords")
    args_parser.add_argument(
        "--nested_order",
        nargs='+',
        type=str,
        default=[NestedOrder.DATE.value],
        choices=[e.value for e in NestedOrder],
        help="Nested sorting order"
    )

    args_parser.add_argument(
        "--process_type",
        type=str,
        default=ProcessType.LINEAR.value,
        choices=[p.value for p in ProcessType],
        help="Process data speed"
    )
    args_parser.add_argument(
        "--dry-run", type=bool,
        help="Will just show result without actually processing it"
    )
    # Parse the command-line arguments
    args = args_parser.parse_args()
    print("Nested Order received:", args.nested_order)

    output_path_check = Path(args.output_path)
    output_path_check.mkdir(parents=True, exist_ok=True)

    start_time = time.time()

    # Call the process_file function with the provided paths
    file_sorter = FileSorter(
        input_folders=args.input_paths,
        output_folder=args.output_path,
        shift_type= args.shift_type,
        file_extensions= args.file_extensions,
        location=args.location,
        nested_order=args.nested_order,
        dry_run=args.dry_run
    )
    file_sorter.process_files(
        process_type=ProcessType(args.process_type)
    )

    end_time = time.time()
    runtime = end_time - start_time
    print(f"\n\nRuntime: {runtime:.2f} seconds")

if __name__ == "__main__":
    main()
