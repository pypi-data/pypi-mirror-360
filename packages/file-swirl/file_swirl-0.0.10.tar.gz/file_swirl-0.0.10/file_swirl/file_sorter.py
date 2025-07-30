"""
docstring
"""
import os
import shutil
import traceback
from itertools import chain
from pathlib import Path
from queue import Empty, Full, Queue
from threading import Event, Lock, Thread
from typing import List, Optional

from file_swirl.file_structs import NestedOrder, ProcessType, ShiftType, WorkerStats
from file_swirl.logger import get_dict_logger
from file_swirl.meta_extract import MetaExtract
from file_swirl.utils import convert_size, get_category, get_date_subpath

logger = get_dict_logger(name= 'file_sorter')

SENTINEL = None
QUEUE_SIZE = 4  # Only keep enough to feed all workers
MAX_WORKERS = 4


class FileSorter:
    """
    Main class which handles args and i/o operations
    """

    def __init__(
            self, output_folder: str, input_folders: str,
            file_extensions: List[str], shift_type: ShiftType,
            location: str, nested_order: List[str],
            dry_run : bool
        ) -> None:
        """
        Init cli commands
        """

        self.total_counter = 0
        self.total_files_size = 0
        self.files_tracked = {}
        self.output_folder =  Path(output_folder)
        self.input_folders = input_folders
        if shift_type == ShiftType.COPY.value:
            self.shift_type = shutil.copy2
        else:
            self.shift_type = shutil.move

        if not isinstance(file_extensions, set):
            file_extensions = set(file_extensions)

        self.file_extensions = file_extensions
        self.location = location
        self.nested_order = nested_order
        self.dry_run = dry_run


    def get_sort_value(self, file_path: Path, key: str, file_meta_data: dict) -> str:
        """
        Extract file details based on key passed
        """
        result = ''
        if key == NestedOrder.ALPHABET.value:
            result = file_path.stem[0]
        elif key == NestedOrder.DATE.value:
            if file_meta_data:
                creation_date = MetaExtract.get_date_from_meta(file_meta_data)
            else:
                creation_date = (
                    MetaExtract.get_date_taken(file_path) or
                    MetaExtract.get_file_name_date(file_path) or
                    MetaExtract.get_file_creation_date(file_path)
                )

            if creation_date is None or creation_date == '':
                result = "DateNotFound"
            else:
                result = get_date_subpath(creation_date= creation_date)

        elif key == NestedOrder.FILE_EXTENSION.value:
            result = str(file_path).lower().rsplit('.', 1)[-1]

        elif key == NestedOrder.FILE_EXTENSION_GROUP.value:
            result = str(file_path).lower().rsplit('.', 1)[-1]
            result = get_category(extension= result)

        elif key == NestedOrder.MAKE.value:
            result = file_meta_data[0].get('Make')

        elif key == NestedOrder.MODEL.value:
            result = file_meta_data[0].get('Model')

        else:
            raise ValueError(f"Invalid sort key: {key}")

        if result is None:
            result = "UNKNOWN"
        return result

    def arrange_files(self, file_path: Path) -> Optional[Path]:
        """
        Re-arrange files accordinly
        """
        try:
            file_meta_data = MetaExtract.get_metadata(file_path)
            subdirs = [
                self.get_sort_value(file_path, key, file_meta_data)
                for key in self.nested_order
            ]
            dest_path = self.output_folder.joinpath(*subdirs)

            if self.dry_run:
                dest_path = f"{dest_path}{os.sep}{file_path.name}"
                print(f"[DRY-RUN] Would move: {file_path} → {dest_path}")
            else:
                dest_path.mkdir(parents=True, exist_ok=True)
                dest_path = f"{dest_path}{os.sep}{file_path.name}"
                print(f"Processing: {dest_path}")
                self.shift_type(str(file_path), dest_path)
                self.total_files_size += os.path.getsize(dest_path)

            self.total_counter += 1

        except Exception as e:
            print(f"[Exception]  : {e}")
            traceback.print_exc()
            return None

        return Path(dest_path)

    @staticmethod
    def safe_scandir(path: str):
        """
        Runs safety check on given dir and scan & yeilds all folder/files
        """
        try:
            with os.scandir(path) as entries:
                for entry in entries:
                    yield entry
        except (PermissionError, FileNotFoundError) as e:
            print(f"[WARN] Skipped {path}: {e}")

    @staticmethod
    def walk_iterative(root_dir, file_extensions):
        """
        Memory-efficient and stack-safe replacement for os.walk
        """
        stack = [root_dir]
        while stack:
            current_dir = stack.pop()
            for entry in FileSorter.safe_scandir(current_dir):
                if entry.is_dir(follow_symlinks=False):
                    stack.append(entry.path)
                elif entry.is_file(follow_symlinks=False):
                    extension = str(entry.path).rsplit('.', 1)[-1].lower()
                    if extension in file_extensions:
                        yield entry.path

    @staticmethod
    def file_producer(generator, queue: Queue, stop_event: Event):
        """
        Streams file paths from generator into the queue.
        Bounded queue prevents overfilling.
        """
        for file_path in generator:
            if stop_event.is_set():
                break

            while not stop_event.is_set():
                try:
                    queue.put(file_path, timeout=1)
                    break
                except Full:
                    continue

        # Signal done
        for _ in range(MAX_WORKERS):
            queue.put(SENTINEL)

    def file_worker(
        self, thread_id: int, queue: Queue,
        stop_event: Event, stats: WorkerStats, lock: Lock
    ):
        """
        Processes file paths from the queue.
        """
        while not stop_event.is_set():
            try:
                file_path = queue.get(timeout=1)
            except Empty:
                continue

            if file_path is SENTINEL:
                queue.task_done()
                break

            try:
                print(f"\n[Worker-{thread_id}] Processing: {file_path}")
                dest = self.arrange_files(file_path= Path(file_path))
                with lock:
                    stats.total_files_processed += 1
                    stats.total_files_size += os.path.getsize(dest)

            except Exception as e:
                print(f"[Worker-{thread_id}] ERROR: {file_path} → {e}")
            finally:
                queue.task_done()

        stats.done()

    def process_parallel(self, paths: List[Path]) -> None:
        """
        Process files in queue system
        """
        stop_event = Event()
        queue = Queue(maxsize=QUEUE_SIZE)

        # Start producer
        generator = chain.from_iterable(
            FileSorter.walk_iterative(path, self.file_extensions)
            for path in paths
        )
        producer = Thread(
            target=FileSorter.file_producer,
            args=(generator, queue, stop_event), daemon=True
        )
        producer.start()

        worker_stats = [WorkerStats() for _ in range(MAX_WORKERS)]
        lock = Lock()  # To safely update stats

        # Start consumers
        threads = []
        for i in range(MAX_WORKERS):
            t = Thread(
                target=self.file_worker,
                args=(i, queue, stop_event,  worker_stats[i], lock), daemon=True
            )
            t.start()
            threads.append(t)


        # Wait for processing
        try:
            producer.join()
            queue.join()
        except KeyboardInterrupt:
            print("Interrupted !1")
            stop_event.set()

        self.print_summary(worker_stats)

    def process_linear(self, paths: List[Path]) -> None:
        """
        Scans one folder at a time
        """
        for path in paths:
            for file_path in self.walk_iterative(
                root_dir=path,
                file_extensions=self.file_extensions
            ):
                self.arrange_files(file_path= Path(file_path))

        self.print_summary()

    def print_summary(self, worker_stats: List[WorkerStats] = []) -> None:
        """
        Print file's processed and save into logs
        """
        print(f"\n{'#'*15} Processing Completed {'#'*15}")
        print(f"\nTotal Files counted: {self.total_counter}")

        if not worker_stats:
            print(f"\nTotal files size: {convert_size(size_bytes= self.total_files_size)}")
            return

        total_time = 0
        total_files = 0
        total_files_size = 0
        for i, stat in enumerate(worker_stats):
            duration = stat.duration()
            tput = stat.throughput()
            total_files += stat.total_files_processed
            total_time = max(total_time, duration)
            total_files_size += stat.total_files_size
            print(
                f" - Worker-{i}: {stat.total_files_processed} files in {duration:.2f}s "
                f"({tput:.2f} files/sec)"
            )

        print(f"\nTotal files processed: {total_files}")
        print(f"\nTotal files size: {convert_size(size_bytes= total_files_size)}")

    def process_files(self, process_type: ProcessType):
        """
        Start processing files & folders
        """

        paths = [Path(p) for p in self.input_folders]
        for path in paths:
            assert path.exists(), f"Start path does not exist: {path}"

        if process_type == ProcessType.LINEAR:
            self.process_linear(paths= paths)
        elif process_type == ProcessType.PARALLEL:
            self.process_parallel(paths= paths)

