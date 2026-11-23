# Varve counter

Counting varves on scanned thin sections. One file, [`index.html`](index.html):
open it in a browser (Chrome or Edge recommended), nothing to install, works offline,
and images never leave the computer.

The full design (three modules, Method C, file formats) is in [DESIGN.md](DESIGN.md).
**Version 1.1** contains the project setup, Module 1 (blind counting) and image export.

## Workflow

### 1. Project (once, by one person)

1. **Project → New**, give the composite profile a name (e.g. `ZAB-12`).
2. **People:** add everyone who will count (short ids such as `P1`, `MZ`).
3. **Add sections…:** choose the thin-section images, in order from top to bottom
   (reorder with ↑ ↓). Supported: TIFF (uncompressed, LZW, Deflate, PackBits; 8 or 16 bit),
   BMP, PNG, JPEG. DPI is read from the file.
4. **Save** the project (`ZAB-12.project.json`). It stores image names and SHA-256
   hashes, not the images.

### 2. Setup (per section, by one person)

- Check the **DPI**, or calibrate it from a scale bar (two clicks + known length).
- **Draw segment:** click along the counting line, top → bottom; double-click, Enter or
  right-click to finish. Several segments form one path. The next segment starts on the
  **same lamina** where the previous one ended: a pink guide line shows it, and the first
  click snaps to it (Shift+click to ignore).
- Enter the **core depth** of the path start and end (cm). A section's path end must equal
  the next section's path start; the Project tab checks for gaps and overlaps.
- **Save** the project and give it to the counters together with the images.

### 3. Count (Module 1, each counter, blind)

1. Open the project, **Load images…**, choose yourself in **I am**.
2. **1 Count → New count** (or **Open…** your earlier counts file).
3. Click every varve boundary you see. Clicks snap to the path; drag a mark to move it,
   right-click (or Delete) to remove it. Only your own marks are shown.
4. **Save** → `ZAB-12.P1.counts.json` (one file per counter, all sections).
   **Export CSV** → one row per boundary with its position and core depth.

### Export an image

**Export…** (top right, or <kbd>E</kbd>) saves the current section with whatever is marked at
that moment, as a PNG with the scan DPI written into the file. A live preview shows the result.

- Default: the **whole section at full resolution**; tick **Current view only** for exactly
  what is on screen.
- Layers (path, marks, numbers, labels), brightness/contrast, a scale bar, a caption strip
  (project, section, counter, date, depths) and the mark size can be set.
- In **1 Count** only your own boundaries are drawn; in **Setup** only the path.

Unsaved work is also kept in the browser and offered back the next time the same file is
opened, but the JSON files are the real record.

## Depth

`core_depth = top + s / L × (base − top)`, where `s` is the position along the path
(segments joined into one length) and `L` the path length. Crack correction is applied
later, in Module 3.

## Not yet

- Module 2: matching the counters' boundaries and Method C (version 2).
- Module 3: cracks, final varve depths, thickness (versions 3–4).
