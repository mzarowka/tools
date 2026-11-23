# Varve counter

Counting varves on scanned thin sections. One file, [`index.html`](index.html):
open it in a browser (Chrome or Edge recommended), nothing to install, works offline,
and images never leave the computer.

The full design (three modules, Method C, file formats) is in [DESIGN.md](DESIGN.md).
**Version 2** contains the project setup, Module 1 (blind counting), Module 2 (Method C) and image export.

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

### 4. Decide (Module 2, Method C — after all counts are finished)

1. Open the project and images, then **2 Decide → Load counts files…** and choose the
   counts files of all counters at once.
2. **Match automatically.** Boundaries of different counters within the tolerance
   (default 0.5 × the local varve thickness) are matched into groups, in order.
3. Each group is decided by majority:
   - all counters → a varve;
   - a majority → a varve, negative uncertainty +1;
   - a minority → not a varve, positive uncertainty +1.
   Uncertainties are summed from the top of the record down.
4. **Review:** **Next ▸** / **◂ Prev** (or <kbd>.</kbd> / <kbd>,</kbd>) jump through the flagged
   groups (disagreements, members far apart, new boundaries). On the image every counter has
   its own track (coloured dots) and matched marks are linked (green = all, yellow = majority,
   red ring = rejected).
   - Click a mark to select its group; **Shift+click** a mark of another group to merge them.
   - **Detach (X)** takes the selected boundary out of its group.
   - **Checked (C)** marks the group as reviewed.
   The decision itself always follows the majority rule and cannot be changed by hand.
5. **Save** → `ZAB-12.chronology.json` (matching, edits and settings).
   **Export CSV** → one row per group: varve number, depths, cumulative +/− uncertainty.

### Export an image

**Export…** (top right, or <kbd>E</kbd>) saves the current section with whatever is marked at
that moment, as a PNG with the scan DPI written into the file. A live preview shows the result.

- Default: the **whole section at full resolution**; tick **Current view only** for exactly
  what is on screen.
- Layers (path, marks, numbers, labels), brightness/contrast, a scale bar, a caption strip
  (project, section, counter, date, depths) and the mark size can be set.
- In **1 Count** only your own boundaries are drawn; in **2 Decide** all counters, the
  matching and varve numbers; in **Setup** only the path.

Unsaved work is also kept in the browser and offered back the next time the same file is
opened, but the JSON files are the real record.

## Depth

`core_depth = top + s / L × (base − top)`, where `s` is the position along the path
(segments joined into one length) and `L` the path length. Crack correction is applied
later, in Module 3.

## Not yet

- Module 3: cracks, final varve depths, thickness (versions 3–4).
