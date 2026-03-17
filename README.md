# 📸 PhotoCollector
**PhotoCollector** is a **Python script** that scans drives or folders and consolidates image and video files into a single destination folder.  
It supports a **huge range of formats** and handles **duplicates automatically**. Perfect for learning Python scripting and file management!

---

> ⚠️ **WARNING:** The author is **not responsible** for any misuse of this script.  
> Use this tool **only on systems and files you own** or have explicit permission to access.  
> Unauthorized use may violate local laws and regulations.

---

## ⚡ Features

- Scan **all drives** or **specific folders** for image and video files.
- Consolidate files into a single **destination folder**.
- **Automatic duplicate handling** (renames files if a conflict exists).
- **Filter by file size** (small / medium / large / custom range).
- **Error logging** for files that fail to copy, with the ability to clear the log from the menu.
- **Progress display** during scanning.
- **Auto-maximizes** the console window on launch (Windows).
- Collection **statistics** (file count, total size, top file types).
- Falls back to `~/Downloads/Collected Photos` if the destination can't be created.

---

## 🖼️ Supported Formats

JPEG, JPG, PNG, GIF, BMP, TIFF, TIF, WebP, SVG, ICO, HEIC, HEIF, AVIF, MP4, AVI, MOV, MPEG, MPG, WMV, WebM, PDF, TTF, 3GP, 3G2, 8BPS, AAI, AI, ANI, ANIM, APNG, ART, ARW, AVS, BAYER, BGR, BPM, CALS, CAP, CIN, CMT, CR2, CR3, CRW, CUR, CUT, DDS, DIB, DICOM, DJVU, DNG, DPX, DRF, EMF, EPID, EPS, ERF, EXR, FAX, FITS, FLV, FPX, GPLT, GRAY, HDR, HRZ, ICON, IFF, ILBM, IMG, INDD, IPL, JBG, JBIG, JNG, JP2, JPC, JPE, JPX, K25, KDC, M4V, MAT, MEF, MIFF, MNG, MOD, MRW, MSL, MTV, MVG, NEF, NRW, OGV, ORF, OTB, P7, PAL, PAM, PBM, PCD, PCDS, PCL, PCT, PCX, PDB, PEF, PES, PFA, PFB, PFM, PGM, PICON, PICT, PIX, PJPEG, PLASMA, PNG8, PNG24, PNG32, PNM, PPM, PS, PSB, PSD, PTX, PWP, QTI, QTIF, RAF, RAS, RGB, RGBA, RGF, RLA, RLE, RMF, RW2, RWL, SCT, SFW, SGI, SHTML, SIX, SIXEL, SMS, SR2, SRF, SRW, SUN, SVGZ, TGA, TIM, TOD, UBRL, UIL, UYVY, VDA, VICAR, VID, VIFF, VOB, VST, WBMP, WMF, WPG, X3F, XBM, XCF, XWD, YCbCr, YUV

---

## 🚀 Usage

### Running directly
1. Make sure **Python 3.8+** is installed.
2. Download this repository.
3. Run the script:
   ```bash
   cd src
   python main.py
   ```
4. Follow the on-screen menu:
   - **1** — Collect all photos/videos from all accessible drives (Turbo Mode).
   - **2** — Collect from the `Pictures` folder only.
   - **3** — Collect from the `Videos` folder only.
   - **4** — Collect with a file size filter.
   - **5** — Change the destination folder.
   - **6** — View collection statistics.
   - **7** — View / clear the error log.
   - **8** — Exit.

### Building a standalone `.exe` (Windows)
1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```
2. Build:
   ```bash
   cd src
   python -m PyInstaller --onefile --console main.py --name PhotoCollector
   ```
3. The compiled executable will appear in the `dist\` folder.

---

## 📝 Notes

- Requires **Python 3.8 or later**. No third-party packages needed to run the script itself.
- Designed primarily for **Windows**, but the core scanning logic works on macOS and Linux too (the auto-maximize and Win+Up shortcut are Windows-only and are silently skipped on other platforms).
- Make sure you have **write permissions** for the destination folder.
- The error log is saved to `%TEMP%\photo_collector_errors.log` and can be cleared from the menu without crashing.
- Excluded folders (e.g. `Windows`, `AppData`, `$Recycle.Bin`) are automatically skipped during full-drive scans.

---

> 💡 **Tip:** Try experimenting with the script to learn how Python interacts with the file system. You can extend `SUPPORTED_EXTENSIONS` or `EXCLUDED_FOLDERS` at the top of `src/main.py` to customise behaviour without touching any other logic!

---
