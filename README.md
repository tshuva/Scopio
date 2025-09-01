# File Transfer Tool

A Python-based command-line tool for transferring files and folders using `rsync` with parallel processing and real-time progress display.

## Features

- 🚀 **Parallel transfers**: Transfer multiple files/folders simultaneously
- 📊 **Real-time progress**: Individual progress bars for each transfer
- 🔧 **Bandwidth limiting**: Control transfer speed to avoid network congestion

## Requirements

- Python 3.9+ (uses union type annotations `int | None`)
- `rsync` installed on your system
- Required Python packages:




**Windows:**
Install through WSL or use rsync for Windows.

## Installation
## Installation
```bash
uv sync
```

## Usage

```bash
uv run main.py [sources...] destination [options]
```

### Arguments

- `sources`: One or more source files or folders to transfer
- `destination`: Destination file or folder
- `--bwlimit`: Bandwidth limit in KB/s per transfer (default: 100)

## Examples

### Basic Examples

**Transfer a single file:**
```bash
uv run main.py document.pdf /backup/folder/
```

**Transfer multiple files:**
```bash
uv run main.py file1.txt file2.pdf folder1/ /backup/destination/
```

**Transfer with custom bandwidth limit:**
```bash
uv run main.py large_file.zip /backup/ --bwlimit 50
```

### Advanced Examples

**Transfer to a specific filename** (only works with single source):
```bash
uv run main.py source.txt /backup/renamed_file.txt
```

**Transfer large dataset with slow bandwidth:**
```bash
uv run main.py dataset1/ dataset2/ dataset3/ /external_drive/backups/ --bwlimit 25
```

**Transfer system logs with high bandwidth:**
```bash
uv run main.py /var/log/app1/ /var/log/app2/ /backup/logs/ --bwlimit 1000
```

## How It Works

1. **Validation**: Checks that all source paths exist
2. **Sorting**: Sorts sources by size (largest first) for optimal load balancing
3. **Destination Setup**: Creates destination directories as needed
4. **Parallel Execution**: Runs up to 4 concurrent rsync processes
5. **Progress Display**: Shows individual progress bars for each transfer
6. **Results Summary**: Reports successful and failed transfers

## Progress Display

The tool shows real-time progress for each transfer:

```
Starting parallel transfer...

dataset1/: 45%|████▌     | 45/100 [00:23<00:28, 1.95%/s]
dataset2/: 78%|███████▊  | 78/100 [00:15<00:04, 5.20%/s]
large_file.zip: 23%|██▎   | 23/100 [00:45<02:30, 0.51%/s]
```

## Technical Details

- Uses `ThreadPoolExecutor` for parallel processing
- Parses rsync's `--progress` output to extract percentages
- Implements smart file/folder detection for destination handling
- Graceful handling of interrupted transfers (Ctrl+C)
