# 📁 File swirl

Now Organizes files from chaos to order with just one command.
Organize photos, videos, documents, and more — cleanly and efficiently — using flexible sorting rules.


## ✨ Organize Features
- 📅 Sort by Date — Organize files into folders by creation or modified date.
- 🧩 Filter by File Extension — Group files like .jpg, .mp4, .pdf, etc
- 🏷️ Sort by Camera Make (EXIF.make) — Useful for photographers to group by device brand.
- 🔍 Sort by File Type (MIME) — Organize images, videos, documents, etc.
- 🗂️ Nested Sorting — Apply multi-level sort: e.g., Date → Extension → Make.
- ⚙️ Custom Sort Key Chains — Chain any supported keys in any order.
- 🎛️ Parallel Processing Support — Fast sorting using multi-threading.



Also supports to arranges file in nested folder structure like `Output/Data/Make/Model` for all the options mentioned above.

This scripts lets you filter out specific file extensions while sorting.
e.g Sort only `.mp4` files from `source` dir into `destination` dir

### System requriments.
- `Python3.10+`
- `ExifTool`

### ✅ Supports
- Windows 11 x64


### Project setup
```
- git clone https://github.com/NishantGhanate/FileSwirl.git
- cd FileSort
- python -m venv venv
- [Win] > venv\Scripts\activate
- [Linux] $ venv/bin/activate
- pip install -r requriments.txt
```

### Download this tool
```
- Download & Install: https://exiftool.org/
- For Windows Installer: https://oliverbetz.de/pages/Artikel/ExifTool-for-Windows
```

## To install project locally
```bash
For development
> pip install -e .

For final build testing
> python -m pip install .
```


## To build project locally
```bash
> python -m build
> pip install dist/file_swirl-0.0.10-py3-none-any.whl
```

### HELP
```bash
> python -m file_swirl.cli -h
```

### Run cli: default command
```bash
> python -m file_swirl.cli --input_paths "E:\\src" --output_path "E:\\dest"
```

### Defaults Args for cli
```bash
--shift_type copy
--nested_order date
--process_type linear
--file_extensions "{pre-defined inside constants}"
```

#### Args and its values
```bash
--shift_type : copy | move
--nested_order : alphabet date file_extension file_extension_group make model
--process_type : linear | parallel
--file_extensions "{pre-defined inside constants all basic formats}"
```

### Examples:

🔁 Move files from a source to a destination
```bash
python -m file_swirl.cli \
  --input_paths "E:\\src" \
  --output_path "E:\\dest" \
  --shift_type "move"
```

🗃️ Move files and organize by nested folders: date file_extension
```bash
python -m file_swirl.cli \
  --input_paths "E:\\src" \
  --output_path "E:\\dest" \
  --shift_type "move" \
  --nested_order date file_extension
```

🏷️ Organize files by camera make/brand
```bash
python -m file_swirl.cli \
  --input_paths "E:\\src" \
  --output_path "E:\\dest" \
  --nested_order make
```

⚡ Copy from multiple folders in parallel mode
```bash
python -m file_swirl.cli \
  --input_paths "E:\\src" "E:\\temp" \
  --output_path "E:\\dest" \
  --shift_type "copy" \
  --process_type "parallel
```




## 🧱 Architecture:
Currently its limited to 1 producer and 4 q each thread will consume from this q
```
+-----------------+       +------------------+
|   Producer(s)   | --->  |  Queue (Stream)  | ---> [Processor 1]
| (dir scanners)  |       |  file paths      | ---> [Processor 2]
+-----------------+       +------------------+ ---> [Processor N]
```


### Set to test code locally
```
Linux : export PYTHONPATH=.
WIN: set PYTHONPATH=.
```
