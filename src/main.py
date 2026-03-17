#!/usr/bin/env python3
"""
Photo Collector - Shamlan
Collects photos and videos from drives and organizes them into a destination folder.
"""

import os
import sys
import shutil
import logging
import time
import string
from pathlib import Path
from datetime import datetime

# ─── Configuration ────────────────────────────────────────────────────────────

DESTINATION = str(Path.home() / "OneDrive" / "Pictures")

SUPPORTED_EXTENSIONS = {
    "JPEG", "JPG", "PNG", "GIF", "BMP", "TIFF", "TIF", "WEBP", "SVG", "ICO",
    "HEIC", "HEIF", "AVIF", "MP4", "AVI", "MOV", "MPEG", "MPG", "WMV", "WEBM",
    "PDF", "TTF", "3GP", "3G2", "8BPS", "AAI", "AI", "ANI", "ANIM", "APNG",
    "ART", "ARW", "AVS", "BAYER", "BGR", "BPM", "CALS", "CAP", "CIN", "CMT",
    "CR2", "CR3", "CRW", "CUR", "CUT", "DDS", "DIB", "DICOM", "DJVU", "DNG",
    "DPX", "DRF", "EMF", "EPID", "EPS", "ERF", "EXR", "FAX", "FITS", "FLV",
    "FPX", "GPLT", "GRAY", "HDR", "HRZ", "ICON", "IFF", "ILBM", "IMG", "INDD",
    "IPL", "JBG", "JBIG", "JNG", "JP2", "JPC", "JPE", "JPX", "K25", "KDC",
    "M4V", "MAT", "MEF", "MIFF", "MNG", "MOD", "MRW", "MSL", "MTV", "MVG",
    "NEF", "NRW", "OGV", "ORF", "OTB", "P7", "PAL", "PAM", "PBM", "PCD",
    "PCDS", "PCL", "PCT", "PCX", "PDB", "PEF", "PES", "PFA", "PFB", "PFM",
    "PGM", "PICON", "PICT", "PIX", "PJPEG", "PLASMA", "PNG8", "PNG24", "PNG32",
    "PNM", "PPM", "PS", "PSB", "PSD", "PTX", "PWP", "QTI", "QTIF", "RAF",
    "RAS", "RGB", "RGBA", "RGF", "RLA", "RLE", "RMF", "RW2", "RWL", "SCT",
    "SFW", "SGI", "SHTML", "SIX", "SIXEL", "SMS", "SR2", "SRF", "SRW", "SUN",
    "SVGZ", "TGA", "TIM", "TOD", "UBRL", "UIL", "UYVY", "VDA", "VICAR", "VID",
    "VIFF", "VOB", "VST", "WBMP", "WMF", "WPG", "X3F", "XBM", "XCF", "XWD",
    "YCbCr", "YUV"
}

EXCLUDED_FOLDERS = {
    "windows", "program files", "program files (x86)", "programdata",
    "system volume information", "recycler", "recycled", "$recycle.bin",
    "appdata", "temp", "tmp", "cache"
}

LOG_FILE = Path(os.environ.get("TEMP", "/tmp")) / "photo_collector_errors.log"

# ─── Globals ──────────────────────────────────────────────────────────────────

stats = {
    "file_count": 0,
    "duplicate_count": 0,
    "error_count": 0,
    "scan_count": 0,
    "total_size": 0,
}

destination = DESTINATION
min_size = None
max_size = None
start_time = None

# ─── Logging ──────────────────────────────────────────────────────────────────

logger = logging.getLogger("photo_collector")
logger.setLevel(logging.ERROR)

def _setup_logger():
    """Attach a fresh FileHandler to the logger."""
    for h in logger.handlers[:]:
        h.close()
        logger.removeHandler(h)
    fh = logging.FileHandler(str(LOG_FILE), encoding="utf-8")
    fh.setFormatter(logging.Formatter("[%(asctime)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
    logger.addHandler(fh)

def _close_logger():
    """Close and detach all handlers (required before deleting the file on Windows)."""
    for h in logger.handlers[:]:
        h.close()
        logger.removeHandler(h)

def clear_log_file():
    """Safely close the logger, delete the log file, then re-initialise the logger."""
    _close_logger()
    try:
        LOG_FILE.unlink()
    except FileNotFoundError:
        pass
    except OSError as e:
        print(f"  Could not delete log: {e}")
    _setup_logger()

_setup_logger()

# ─── Helpers ──────────────────────────────────────────────────────────────────

def clear():
    os.system("cls" if os.name == "nt" else "clear")


def banner():
    print("""
┌──────────────────────────────────────────────────────────────────────────┐
│███╗   ███╗ █████╗ ██╗███╗   ██╗    ███╗   ███╗███████╗███╗   ██╗██╗   ██╗│
│████╗ ████║██╔══██╗██║████╗  ██║    ████╗ ████║██╔════╝████╗  ██║██║   ██║│
│██╔████╔██║███████║██║██╔██╗ ██║    ██╔████╔██║█████╗  ██╔██╗ ██║██║   ██║│
│██║╚██╔╝██║██╔══██║██║██║╚██╗██║    ██║╚██╔╝██║██╔══╝  ██║╚██╗██║██║   ██║│
│██║ ╚═╝ ██║██║  ██║██║██║ ╚████║    ██║ ╚═╝ ██║███████╗██║ ╚████║╚██████╔╝│
│╚═╝     ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝    ╚═╝     ╚═╝╚══════╝╚═╝  ╚═══╝ ╚═════╝ │
└──────────────────────────────────────────────────────────────────────────┘""")


def progress_bar(percent: int, width: int = 28) -> str:
    filled = int(width * percent / 100)
    return "█" * filled + "░" * (width - filled)


def format_size(bytes_: int) -> str:
    mb = bytes_ / 1_048_576
    if mb >= 1024:
        return f"{mb / 1024:.2f} GB"
    return f"{mb:.2f} MB"


def elapsed_time(start: float) -> str:
    secs = int(time.time() - start)
    return f"{secs // 60}m {secs % 60}s"


def is_excluded(path: Path) -> bool:
    for part in path.parts:
        if part.lower() in EXCLUDED_FOLDERS:
            return True
    return False


def get_available_drives() -> list[str]:
    """Return all accessible drive roots (Windows) or just '/' on Unix."""
    if os.name == "nt":
        drives = []
        for letter in string.ascii_uppercase:
            drive = f"{letter}:\\"
            if os.path.exists(drive):
                drives.append(drive)
        return drives
    return ["/"]


# ─── Core logic ───────────────────────────────────────────────────────────────

def create_destination() -> bool:
    global destination
    dest = Path(destination)
    try:
        dest.mkdir(parents=True, exist_ok=True)
    except OSError:
        print("  ✗ Cannot create destination — using fallback.")
        destination = str(Path.home() / "Downloads" / "Collected Photos")
        dest = Path(destination)
        try:
            dest.mkdir(parents=True, exist_ok=True)
        except OSError:
            print("  ✗ Critical: Cannot create any destination folder.")
            return False

    collected_sub = dest / "Collected Photos"
    try:
        collected_sub.mkdir(exist_ok=True)
        destination = str(collected_sub)
        print(f"  ✓ Destination ready: {destination}")
    except OSError:
        pass

    return True


def process_file(filepath: Path) -> None:
    global destination

    if not filepath.exists():
        logger.error("File not found: %s", filepath)
        stats["error_count"] += 1
        return

    file_size = filepath.stat().st_size

    if min_size is not None and file_size < min_size:
        return
    if max_size is not None and file_size > max_size:
        return

    filename = filepath.name
    stem = filepath.stem
    suffix = filepath.suffix
    dest_path = Path(destination) / filename

    counter = 1
    while dest_path.exists():
        stats["duplicate_count"] += 1
        dest_path = Path(destination) / f"{stem}_({counter}){suffix}"
        counter += 1

    try:
        shutil.copy2(filepath, dest_path)
        stats["file_count"] += 1
        stats["total_size"] += file_size
    except (OSError, shutil.Error) as e:
        logger.error("Copy failed: %s → %s | %s", filepath, dest_path, e)
        stats["error_count"] += 1


def scan_directory(root: str) -> None:
    root_path = Path(root)
    print(f"  Scanning {root_path} ...")
    batch = 0

    for dirpath, dirnames, filenames in os.walk(root_path, onerror=None):
        current = Path(dirpath)
        if is_excluded(current):
            dirnames.clear()
            continue

        # Prune excluded sub-directories in-place
        dirnames[:] = [
            d for d in dirnames
            if d.lower() not in EXCLUDED_FOLDERS
        ]

        for filename in filenames:
            ext = Path(filename).suffix.lstrip(".").upper()
            if ext not in SUPPORTED_EXTENSIONS:
                continue

            stats["scan_count"] += 1
            batch += 1
            if batch >= 50:
                batch = 0
                pct = min(stats["scan_count"] // 100, 100)
                print(
                    f"\r  [{progress_bar(pct)}] "
                    f"Scanned: {stats['scan_count']} | "
                    f"Collected: {stats['file_count']}",
                    end="",
                    flush=True,
                )

            process_file(current / filename)

    print()  # newline after progress


# ─── Menu actions ─────────────────────────────────────────────────────────────

def reset_stats() -> None:
    for key in stats:
        stats[key] = 0


def collect_all(drives: list[str] | None = None) -> None:
    global start_time
    reset_stats()
    clear_log_file()

    if not create_destination():
        input("\nPress Enter to return to menu...")
        return

    start_time = time.time()
    roots = drives or get_available_drives()
    print(f"\n  Drives to scan: {', '.join(roots)}\n")
    for drive in roots:
        scan_directory(drive)

    show_results()


def collect_pictures_only() -> None:
    global start_time
    reset_stats()
    clear_log_file()

    pictures = Path.home() / "Pictures"
    if not pictures.exists():
        print("  Error: Pictures folder not found.")
        input("\nPress Enter...")
        return

    if not create_destination():
        input("\nPress Enter to return to menu...")
        return

    start_time = time.time()
    scan_directory(str(pictures))
    show_results()


def collect_videos_only() -> None:
    global start_time
    reset_stats()
    clear_log_file()

    videos = Path.home() / "Videos"
    if not videos.exists():
        print("  Error: Videos folder not found.")
        input("\nPress Enter...")
        return

    if not create_destination():
        input("\nPress Enter to return to menu...")
        return

    start_time = time.time()
    scan_directory(str(videos))
    show_results()


def collect_by_size() -> None:
    global min_size, max_size
    print("""
┌─── SIZE FILTER OPTIONS ───┐
│ 1. Small  (under 1 MB)    │
│ 2. Medium (1 MB – 10 MB)  │
│ 3. Large  (over 10 MB)    │
│ 4. Custom range           │
└───────────────────────────┘""")
    choice = input("  Choose size filter [1-4]: ").strip()

    if choice == "1":
        min_size, max_size = 0, 1_048_576
    elif choice == "2":
        min_size, max_size = 1_048_576, 10_485_760
    elif choice == "3":
        min_size, max_size = 10_485_760, None
    elif choice == "4":
        try:
            min_size = int(input("  Minimum size in bytes: ").strip())
            max_size_input = input("  Maximum size in bytes (blank = no limit): ").strip()
            max_size = int(max_size_input) if max_size_input else None
        except ValueError:
            print("  Invalid input. Skipping size filter.")
            min_size = max_size = None
    else:
        print("  Invalid choice — no size filter applied.")
        min_size = max_size = None

    collect_all()


def show_results() -> None:
    elapsed = elapsed_time(start_time) if start_time else "N/A"
    clear()
    print("""
┌─── COLLECTION COMPLETE ───┐
│ ████████████████████████ 100% │
└───────────────────────────┘""")
    print(f"""
┌─── FINAL STATISTICS ───────────────┐
│  Photos collected : {stats['file_count']}
│  Duplicates handled: {stats['duplicate_count']}
│  Errors encountered: {stats['error_count']}
│  Total scanned    : {stats['scan_count']}
│  Total size       : {format_size(stats['total_size'])}
│  Time elapsed     : {elapsed}
└─────────────────────────────────────┘""")

    if stats["file_count"] == 0:
        print("  No images found or accessible.")
    else:
        print(f"  ✓ SUCCESS: {stats['file_count']} photos safely collected!")
        print(f"  Location: {destination}")

    if stats["error_count"] > 0:
        print(f"\n  ⚠  {stats['error_count']} errors occurred. Choose option 7 in the main menu to view the error log.")

    open_folder = input("\n  Open destination folder? [Y/N]: ").strip().lower()
    if open_folder == "y" and os.path.exists(destination):
        if os.name == "nt":
            os.startfile(destination)
        elif sys.platform == "darwin":
            os.system(f'open "{destination}"')
        else:
            os.system(f'xdg-open "{destination}"')

    input("\n  Press Enter to return to menu...")


def show_stats() -> None:
    dest = Path(destination)
    if not dest.exists():
        print("  No collection found.")
        input("\nPress Enter...")
        return

    files = list(dest.rglob("*"))
    files = [f for f in files if f.is_file()]
    total_size = sum(f.stat().st_size for f in files)

    from collections import Counter
    ext_counts = Counter(f.suffix.lower() for f in files)
    top5 = ext_counts.most_common(5)

    print(f"""
┌─── COLLECTION STATISTICS ──────────────────┐
│  Files in collection : {len(files)}
│  Total size          : {format_size(total_size)}
│  Top file types:""")
    for ext, count in top5:
        print(f"│    {ext or '(no ext)':<12} : {count} files")
    print("└─────────────────────────────────────────────┘")
    input("\n  Press Enter...")


def show_error_log() -> None:
    if LOG_FILE.exists():
        print("\n┌─── ERROR LOG ───")
        print(LOG_FILE.read_text(encoding="utf-8", errors="replace"))
        clear_it = input("  Clear error log? [Y/N]: ").strip().lower()
        if clear_it == "y":
            clear_log_file()
            print("  Log cleared.")
    else:
        print("  No errors logged yet.")
    input("\n  Press Enter...")


def change_destination() -> None:
    global destination
    print(f"\n  Current destination: {destination}")
    new_dest = input("  Enter new destination path: ").strip()
    if new_dest:
        destination = new_dest
        print(f"  ✓ Destination changed to: {destination}")
        time.sleep(1)


# ─── Main menu ────────────────────────────────────────────────────────────────

def main_menu() -> None:
    while True:
        clear()
        banner()
        print(f"""
┌──────────────────────────────────────────────────────────────────────────┐
│ 1. Collect ALL photos/videos from ALL accessible drives (TURBO MODE)     │
│ 2. Collect photos from Pictures folder only                              │
│ 3. Collect videos from Videos folder only                                │
│ 4. Collect photos by file size filter                                    │
│ 5. Change destination folder                                             │
│ 6. View collection statistics                                            │
│ 7. View error log                                                        │
│ 8. Exit                                                                  │
└──────────────────────────────────────────────────────────────────────────┘
  Current destination: {destination}
""")
        choice = input("  Enter your choice [1-8]: ").strip()

        if choice == "1":
            collect_all()
        elif choice == "2":
            collect_pictures_only()
        elif choice == "3":
            collect_videos_only()
        elif choice == "4":
            collect_by_size()
        elif choice == "5":
            change_destination()
        elif choice == "6":
            show_stats()
        elif choice == "7":
            show_error_log()
        elif choice == "8":
            print("\n  Goodbye!\n")
            sys.exit(0)
        else:
            print("  Invalid choice. Press any key to try again...")
            input()


def press_win_up():
    """Press Win+Up to maximize the console window (Windows only)."""
    if os.name != 'nt':
        return
    try:
        import ctypes
        VK_LWIN = 0x5B
        VK_UP   = 0x26
        KEYEVENTF_KEYUP = 0x0002
        user32 = ctypes.windll.user32
        user32.keybd_event(VK_LWIN, 0, 0, 0)
        user32.keybd_event(VK_UP,   0, 0, 0)
        user32.keybd_event(VK_UP,   0, KEYEVENTF_KEYUP, 0)
        user32.keybd_event(VK_LWIN, 0, KEYEVENTF_KEYUP, 0)
    except Exception:
        pass


if __name__ == "__main__":
    time.sleep(0.015)   # 15 ms — then maximize window
    press_win_up()
    time.sleep(0.025)   # 25 ms — then show menu
    main_menu()