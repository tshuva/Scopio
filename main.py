import os
import re
import argparse
import subprocess
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

PROGRESS_RE = re.compile(r"\s+[\d.]+\w+\s+(\d+)%")


def parse_progress(line: str) -> int | None:
    """Extract percentage from rsync output line."""
    m = PROGRESS_RE.search(line)
    return int(m.group(1)) if m else None


def is_file(path: str) -> bool:
    """Find if the path is a file (even if it does not exist)."""
    if os.path.exists(path):
        return os.path.isfile(path)
    basename = os.path.basename(path)
    return '.' in basename and not basename.startswith('.')


def run_rsync(src: str, dst: str, bwlimit: int = 100, position: int = 0) -> int:
    """Run rsync for a single source with a progress bar."""
    print(f"Starting transfer: {src} -> {dst}")

    cmd = ["rsync", "-avh", "--progress", f"--bwlimit={bwlimit}", src, dst]
    process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1
    )

    bar = tqdm(total=100, desc=os.path.basename(src), unit="%",
               position=position, ncols=100, leave=True)

    last_percent = 0
    for line in iter(process.stdout.readline, ""):
        percent = parse_progress(line)
        if percent is not None:
            increment = max(percent - last_percent, 0)
            if increment > 0:
                bar.update(increment)
                last_percent = percent

    _, err = process.communicate()
    bar.close()

    if process.returncode != 0:
        print(f"Transfer failed for {src}: {err.strip()}")

    return process.returncode


def transfer(sources: list[str], dst_paths: list[str], bwlimit: int = 100) -> int:
    """Transfer sources in parallel."""

    print("Starting parallel transfer...\n")
    exit_codes = []

    with ThreadPoolExecutor(max_workers=len(sources)) as executor:
        futures = {
            executor.submit(run_rsync, src, dst, bwlimit, pos): src
            for pos, (src, dst) in enumerate(zip(sources, dst_paths))
        }

    exit_codes = (
        (futures[future], future.result() if not future.exception() else 1)
        for future in as_completed(futures))

    return 0 if all(code == 0 for _, code in exit_codes) else 1


def init_dir_cp(dst, srcs):
    os.makedirs(dst, exist_ok=True)
    return [os.path.join(dst, os.path.basename(src)) for src in srcs]


def safe_get_size(src, parser):
    try:
        return os.path.getsize(src)
    except:
        parser.error(
            f"File '{src}' is a not a file ")


def main():
    parser = argparse.ArgumentParser(description="Transfer files/folders.")
    parser.add_argument("sources", nargs="+", help="Source files/folders")
    parser.add_argument("dst", help="Destination file/folder")
    parser.add_argument("--bwlimit", type=int, default=100,
                        help="Bandwidth limit KB/s per transfer")
    args = parser.parse_args()

    # Determine destination type
    dst_is_file = is_file(args.dst)
    if dst_is_file and len(args.sources) > 1:
        parser.error(
            f"Destination '{args.dst}' is a file, but multiple sources were provided.")

    # Sort sources by size (largest first)
    sources_by_size = sorted(
        args.sources, key=lambda f: safe_get_size(f, parser), reverse=True)

    # Build per-source destinations
    dst_paths = [args.dst]if dst_is_file else init_dir_cp(
        args.dst, sources_by_size)

    exit_code = transfer(sources_by_size, dst_paths, args.bwlimit)

    if exit_code == 0:
        print("\nAll transfers completed successfully")
    else:
        print("\nSome transfers failed")
        exit(exit_code)


if __name__ == "__main__":
    main()
