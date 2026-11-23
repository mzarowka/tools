# Varve counter — design

Status: **version 3 implemented** (project setup, Module 1, Module 2, Module 3 step 1 and image export) in [`index.html`](index.html). Module 3 step 2 (thickness) is designed but not built yet.

A browser tool for counting varves on scanned thin sections, building a varve
chronology with uncertainty (Method C of Żarczyński, Tylmann & Goslar 2018,
*Quaternary Geochronology* 47: 107–119) and measuring varve thickness. It is a
lightweight, open replacement for the CooRecorder part of that workflow.

## 1. Principles

- **One HTML file**, run locally in a browser. No installation, no server, no
  upload: images and data never leave the computer (same as the other tools in
  this repository).
- **Three modules, one app.** The modules are tabs of the same page and share
  the image viewer, calibration and paths. They are decoupled through **files**:
  each module reads the files the previous one wrote.
- **JSON for state, CSV for analysis.** JSON files hold the full, re-openable
  state. CSV exports are tidy (one row per observation) and meant for R
  (`readr::read_csv()`; the JSON reads with `jsonlite::read_json()`).
- **Nothing is hard-coded to a particular lake or to three counters.**

```
images (BMP/TIFF + DPI)
        │
        ▼
project file ── sections, paths, depth anchors, people, settings
        │
        ▼
Module 1  Counting ──────────► one counts file per counter (blind)
        │
        ▼
Module 2  Varve decision (Method C) ► chronology file: matched boundaries, ±uncertainty
        │
        ▼
Module 3  Final depths + thickness ─► cracks, final varve-depth table,
                                      traced horizons, thickness measurements
```

## 2. Terms

| Term | Meaning |
|---|---|
| **Project** | One composite sediment profile (e.g. `ZAB-12`). Holds people, sections and settings. |
| **Section** | One thin section = one scanned image. |
| **Path** | The counting line of a section. Made of one or more **segments**. |
| **Segment** | A polyline drawn on the image. Several segments let the path avoid cracks or disturbed parts. |
| **s** | Position along the path: distance from the path start, with all segments joined into one length. |
| **Anchors** | Core depth of the path start and of the path end, in the composite profile. |
| **Person** | Someone who draws paths, counts, reviews or measures. Identified by a short id (`P1`, `MZ`, …). |
| **Crack** | A void in the section, marked in Module 3 as a pair (upper and lower edge) and subtracted from thickness. |
| **Boundary** | A click marking the end of a varve, placed on the path. |
| **Horizon** | A short polyline tracing one final varve boundary sideways across the section (Module 3). |

## 3. Geometry and depth

### 3.1 Calibration

- DPI comes from the image header (BMP: pixels per metre; TIFF:
  `XResolution` + `ResolutionUnit`). It can always be overridden by hand,
  because scanners often write wrong or default values.
- Optional: calibration from a scale bar (two clicks + known length). This
  overrides the DPI and is recorded as `dpi_source: "scale_bar"`.
- `mm = px / dpi × 25.4`.

### 3.2 Paths and segments

- Segments are ordered top → bottom and **joined into one length**:
  segment 1 covers `s = 0 … L1`, segment 2 covers `s = L1 … L1+L2`, and so on.
  The total length is `L`.
- **Joint rule:** each segment starts on the same lamina on which the
  previous segment ended, only shifted sideways. When the next segment is drawn,
  the tool shows a short guide from the end of the previous segment, so the
  same layer is easy to find.
- **Ownership rule (no double counting):** a segment owns its start but not
  its end (half-open interval `[start, end)`). A click exactly on a joint
  belongs to the next segment.

### 3.3 Depth anchors and correction

The person drawing the path enters the core depth of the path start
(`d_top`) and the path end (`d_bottom`). Every position on the path is mapped
linearly:

```
core_depth = d_top + (s / L) × (d_bottom − d_top)
```

Once cracks are measured in Module 3, this is refined by leaving out the crack
widths (see 3.5).

- The stretch is spread evenly over the whole path. This corrects for
  shrinkage during freeze-drying and impregnation, and for small errors of
  correlation.
- **Stretch factor** = `(d_bottom − d_top) / (L in mm from DPI)`. It is shown as
  a sanity check (values far from 1 suggest a wrong DPI or wrong anchors).
- **Between sections** the same ownership rule applies: section *n* owns
  `[d_top, d_bottom)`, and its `d_bottom` must equal `d_top` of section *n + 1*.
  The project checks this and warns about gaps or overlaps.
- All lengths are stored in **mm**. The interface accepts cm where it is more
  natural (core depths).

### 3.4 What a boundary means

A boundary marks the **end of a varve** (the base of the varve above it).
The top of the record is the path start of the first section. So:

- the number of varves = the number of boundaries;
- a varve cut by the end of section *n* is finished by the first boundary of
  section *n + 1*, and is counted once.

### 3.5 Cracks

Cracks (opened during freeze-drying or impregnation) often cross the whole
section, so going around them with extra segments is not practical. They are
**not marked during setup or counting**. They are handled in Module 3 (see
7.1 and 7.4), because that is where they matter:

- **Counting and Method C do not need them.** All counters click on the same
  image along the same path, so a crack shifts everyone's positions equally,
  and matching in Module 2 is unaffected. A counter simply clicks a boundary
  where they see it, including at the edge of a crack.
- **Thickness needs them.** A crack inside a varve directly inflates its
  thickness. This is the large, local error.
- **Depth is only slightly affected.** A crack adds its width to the path
  length; the linear stretch then spreads that error over the section. When
  Module 3 has measured the cracks where they cross the path, depths are
  refined: `s_eff = s − (crack width above s)`, `L_eff = L − (total crack
  width)`, and `core_depth = d_top + (s_eff / L_eff) × (d_bottom − d_top)`.
  The stretch factor is recomputed from `L_eff` in the same way.

## 4. People

- The project file holds a list of people: `id`, `name`, optional `note`.
- On opening a project, the user chooses who they are. The choice is
  remembered in the browser as a convenience, but is always written into the
  files that person creates.
- Every file records its author and timestamps; the project file records who
  drew each path and the chronology file records who reviewed the matching.
- Exports use the short ids, so the full names can stay out of shared
  tables.

## 5. Module 1 — Counting

Goal: "do I see a varve here?", one click per boundary, along the path.

1. **Set up (once per section, by one person):** load the image, check the
   DPI, draw the segments, enter the depth anchors. This is saved in the
   project file, so all counters work on exactly the same geometry.
2. **Count (each counter, independently):** load the project and the image,
   choose your id, click boundaries.
   - Clicks are projected onto the nearest point of the **active segment**,
     the segment you are currently counting on. The tool moves to the next
     segment when you reach the end of the current one.
   - Stored per click: `s` (px) and the raw `x, y` (px). Nothing else:
     there is deliberately **no "uncertain" flag and no note**. A click
     means "I see a boundary here". Grading boundaries would bias Method C,
     whose uncertainty comes only from agreement between counters.
   - Drag to move a click, Delete to remove it, undo/redo, autosave in the
     browser between saves.
   - Live readout: number of boundaries, last varve thickness, current
     core depth.
3. **Blind counting:** the counts of other people are never shown in
   Module 1. Each counter saves their own counts file.

## 6. Module 2 — Chronology (Method C)

### 6.1 Rule

For each boundary, count how many counters marked it (`n_agree` of `N`).
The threshold is always a **strict majority**, `k = floor(N/2) + 1`
(3 counters → 2, 4 → 3, 5 → 3). It is not a setting.

| Agreement | Effect |
|---|---|
| `n_agree = N` | boundary accepted, no uncertainty added |
| `k ≤ n_agree < N` | boundary accepted, **negative** uncertainty +1 |
| `n_agree < k` | boundary rejected, **positive** uncertainty +1 |

With `N = 3` this reproduces the paper exactly. With an even `N` a tie
(e.g. 2 of 4) is not a majority, so the boundary is rejected and adds
positive uncertainty. Positive and
negative uncertainties are summed **separately** from the top of the record
down, across sections in project order, which gives asymmetric ranges such
as +34/−53.

### 6.2 Matching boundaries between counters

The rule above needs to know which clicks of different counters are the same
boundary. This is done in two steps.

**Automatic proposal**

- Work per section, on `s`. All counters used the same path on the same
  image, so their positions are directly comparable.
- **Local tolerance:** for each counter, take a running median of the spacing
  between their boundaries (window of about 10 boundaries). Two clicks may be
  matched only if they are closer than `tolerance_fraction × local thickness`.
  The default fraction is **0.5** (anything further is closer to the next
  boundary anyway). Because changes in varve thickness are mostly gradual,
  this follows changes between microfacies without manual zones.
- **Alignment:** an order-preserving alignment of the counters' sorted
  positions. Each group holds at most one click per counter, and boundaries
  never cross. For `N = 3` this is done pairwise and then merged. The same
  approach extends to larger `N`.

**Manual review (required)**

- The counters are shown as parallel tracks over the image (as in Fig. 9 of
  the paper), with lines linking matched clicks.
- The reviewer can break a link, merge two groups, or move a click to another
  group. Groups near the tolerance limit are flagged for checking.
- Manual edits are stored in the chronology file, so the result can be
  reproduced and re-checked. Re-running the automatic step never overwrites
  them silently.

### 6.3 Implementation notes (version 2)

- **Input:** the counts files of all counters, loaded together. Module 2 shows
  everyone's marks, so it is meant for after counting is finished.
- **Counters per section:** `N` is the number of counters with boundaries in
  that section, and `k = floor(N/2) + 1` is taken from it. The panel warns when
  someone did not count a section.
- **Local thickness:** for each counter, the median spacing of a window of
  `window` consecutive spacings around the boundary. The tolerance of a match is
  `tolerance_fraction × (T_group + T_boundary) / 2`. Without spacings (a single
  boundary), the median spacing of the section is used.
- **Alignment:** counters are added one at a time (in the project's people
  order). Each step is a dynamic-programming alignment of the counter's sorted
  boundaries to the current groups: a match costs `distance / tolerance`
  (only within tolerance), leaving either side unmatched costs 0.5. So a match
  is always preferred to two unmatched boundaries, and the order is preserved.
- **Flags:** a group is flagged for review when not all counters agree, when its
  spread exceeds 80 % of its tolerance, or when it is new (see below). The
  reviewer marks groups as checked; Prev / Next steps through flagged groups
  across sections.
- **Edits:** *detach* takes one boundary out of its group; *merge*
  (Shift+click) joins two groups. A merge is refused when both groups hold a
  boundary of the same counter, or when the result would cross another
  boundary of the same counter. Edited groups are marked `manual` and every
  edit is logged (`edits`: op, time, person, ids).
- **Re-run:** the automatic matching can be re-run (e.g. with another
  tolerance). The reviewer chooses whether manually edited groups are kept.
- **Changed counts:** when a chronology is opened with counts that changed
  since the matching, matched boundaries that no longer exist are removed from
  their groups and new boundaries are added as single groups flagged “new”.
  The chronology must be opened with the counts of every counter it was built
  from.
- **Varve depths:** an accepted boundary closes the varve above it (3.4), so a
  varve spans from the previous accepted boundary (or the top of the record)
  to this one, across section joints.

### 6.4 Output

- The accepted boundaries define the **final varves**.
- For each varve: number, section, top and bottom core depth, `n_agree`,
  which counters marked it, and the cumulative ± uncertainty.
- Rejected boundaries are kept (with `included = false`), because they carry
  the positive uncertainty and show where the counters disagree.

## 7. Module 3 — Final depths and thickness

Two steps. Step 1 is quick and gives the final varve-depth relation. Step 2
is the slow, detailed work and can be done later, or only for some intervals.

### 7.1 Step 1: cracks on the path → final varve depths

1. Mark every crack where it crosses the path (crack pair: upper and lower
   edge, see 7.4).
2. Depths of all accepted boundaries are recomputed with crack widths left
   out (3.5), and the stretch factor is updated.
3. Result: the **final varve-depth table**. One row per accepted varve:
   varve number (counted from the top of the record), top and bottom core
   depth, and the cumulative +/− uncertainty from Module 2.

Implementation notes (version 3):

- Module 3 reads the **chronology file** only (no counts needed). When saved,
  the chronology stores for every group its position on the path (`s_px`) and
  the number of counters who marked it (`n`), and for every section the number
  of counters (`n_counters`). In the same session the chronology can also be
  taken directly from “2 Decide”.
- The decision is re-derived from `n` and `n_counters` with the same majority
  rule, so the varve numbers and uncertainties are identical to Module 2.
- A crack is stored as its two clicked edge points; their positions on the
  path are recomputed from the current path. Overlapping cracks are refused.
- Each section has a flag **“all cracks on the path are marked”**. It is
  exported as `crack_corrected`, so a section without cracks is distinguishable
  from a section that was not checked.
- If the path of a section changed after the matching, a warning is shown.

The tool works with **varve numbers only**. It does not convert them to
calendar ages, so floating chronologies need no special handling. Anchoring
to a year (coring year, tephra, etc.) and the year convention are left to the
analysis in R.

### 7.2 Step 2: thickness — traced horizons (default)

Goal: varve thickness across the width of the section, not only along one
line, and correct where laminae bend.

A line drawn "at an angle" is only a true thickness if it is perpendicular to
the lamina, and on bent laminae that is a guess. Instead:

1. The final boundaries from Module 2 are shown as marks on the path.
2. For each final boundary, the user **traces a short horizon**: a polyline of
   a few clicks following that boundary sideways, starting from its mark on the
   path.
3. **One horizon serves two varves.** It is the base of the varve above and
   the top of the varve below. Each boundary is traced once.
4. The thickness of a varve is measured between its top and base horizons at
   several positions (default 3, spread across the part where both horizons
   exist). At each position the thickness is the **shortest distance** from
   the base horizon to the top horizon, which is perpendicular to the lamina
   even where it bends.
5. A **mean thickness** is also computed from the area between the two
   horizons divided by their shared width. This is robust and does not depend
   on where the sample positions fall.

The effort is similar to drawing three lines per varve (a 3–4-click horizon per
boundary instead of 3 × 2 clicks per varve), but the result is geometrically
well defined.

### 7.3 Fallback: quick lines

For simple, parallel laminae, a quicker mode: draw up to 3 lines per varve,
each from base to top. The thickness is the line length. Results are marked
with `method = "line"` so the two modes are never mixed silently.

### 7.4 Cracks in Module 3

The crack tool **always produces a pair**: an upper edge and a lower edge.
The edges are traced sideways, as two short horizons.

- **Crack inside a varve:** at each measuring position the crack width (the
  shortest distance between its edges) is subtracted from the thickness, and
  the area between its edges is subtracted from the area-based mean. In
  quick-line mode, the crack is a pair of points on the line and its length is
  subtracted.
- **Crack along a boundary** (the common case): the crack pair replaces the
  single horizon. The upper edge is the base of the varve above, and the
  lower edge is the top of the varve below. The crack itself belongs to
  neither varve.
- Each measurement records the subtracted crack width, so it can be checked
  later.
- **Where a crack crosses the path**, its width along the path is stored too.
  This is what refines the depths and the stretch factor (3.5). Boundaries
  already counted keep their depth order; only their depth values shift
  slightly.

### 7.5 Units

Each measurement is reported in two ways:

- `thickness_mm`: physical thickness on the thin section (from DPI);
- `thickness_corr_mm`: multiplied by the stretch factor, consistent with
  core depth.

## 8. Files

All files are JSON, pretty-printed, with a `schema` version. Images are
identified by file name **and SHA-256 hash**, so a file can never be attached
to the wrong image.

| File | Written by | Content |
|---|---|---|
| `<project>.project.json` | setup | people, sections, images, DPI, segments, anchors, settings |
| `<project>.<person>.counts.json` | Module 1 | one counter's boundaries for all sections |
| `<project>.chronology.json` | Module 2 | matching parameters, groups, manual edits, result |
| `<project>.thickness.json` | Module 3 | horizons, cracks, measurements |

One counts file per counter for the whole project keeps the number of files
small, and keeps counters independent.

### 8.1 Sketches

```json
// <project>.project.json
{
  "schema": "varves/project@1",
  "project": "ZAB-12",
  "people": [
    { "id": "P1", "name": "…" },
    { "id": "P2", "name": "…" },
    { "id": "P3", "name": "…" }
  ],
  "settings": {
    "method_c": { "tolerance_fraction": 0.5, "window": 10 }
  },
  "sections": [
    {
      "id": "ZAB-12-1_0-10",
      "image": { "file": "ZAB-12-1_0-10.tif", "sha256": "…", "width": 9450, "height": 1890 },
      "dpi": 2400,
      "dpi_source": "header",
      "segments": [
        { "id": 1, "points": [[120, 940], [9300, 960]] }
      ],
      "anchors": { "top_mm": 0.0, "bottom_mm": 96.0 },
      "drawn_by": "P1",
      "modified": "2026-11-23T12:00:00Z"
    }
  ]
}
```

```json
// <project>.P2.counts.json
{
  "schema": "varves/counts@1",
  "project": "ZAB-12",
  "person": "P2",
  "sections": {
    "ZAB-12-1_0-10": {
      "image_sha256": "…",
      "boundaries": [
        { "id": "b0001", "s_px": 412.6, "x": 532, "y": 951 }
      ]
    }
  },
  "created": "…",
  "modified": "…"
}
```

## 9. CSV exports

| Export | One row per | Columns |
|---|---|---|
| `counts.csv` | click | `project, section, person, seq, boundary_id, segment, s_mm, core_depth_mm, x_px, y_px` |
| `chronology.csv` | matched group | `project, section, group_id, varve_no, included, status, n_agree, n_counters, persons, s_mm, core_depth_mm, top_mm, bottom_mm, unc_pos_cum, unc_neg_cum, checked, manual` |
| `varves.csv` | accepted varve (final) | `project, section, varve_no, status, top_depth_mm, bottom_depth_mm, bottom_depth_uncorrected_mm, unc_pos_cum, unc_neg_cum, crack_corrected` |
| `cracks.csv` | crack | `project, section, crack_id, crosses_path, s_upper_mm, s_lower_mm, width_mm, core_depth_mm` |
| `thickness.csv` | measurement | `project, section, varve_no, method, position_no, x_px, thickness_px, crack_px, thickness_mm, thickness_corr_mm, measured_by` |

`varve_no` is empty for rejected groups. Summaries (mean, SD, n per varve) are
left to R.

## 10. Images

- **BMP** is shown natively by the browser.
- **TIFF** is decoded by the tool's own code (uncompressed, LZW, Deflate,
  PackBits; strips or tiles; 8 or 16 bit), which also reads the DPI tags. No
  external library, so the tool works offline.
- A 10 cm thin section at 2400 DPI is about 9,500 × 1,900 px, which a plain
  canvas viewer handles easily, so no tiling is needed. Very large scans
  (stitched cores, 4800 DPI) are out of scope for now.
- Saving uses the File System Access API where available (Chrome, Edge: save
  in place). Other browsers fall back to downloading the file.

## 11. Image export

At any moment, in any module, the current section can be exported as an image
with whatever is marked at that time. It is meant for figures, supplementary
material, lab notes and checking work with others. It is **not** a data
record: the JSON and CSV files remain the record.

### 11.1 What is drawn

The overlay is the one of the current module, as it is on screen:

| Module | Overlay |
|---|---|
| Setup | path segments, joints, top/base labels with core depth |
| 1 Count | path + **only the exporting counter's** boundaries (blindness is kept) |
| 2 Decide | path + all counters' boundaries as parallel tracks, match links, accepted / rejected marks (as Fig. 9 of the paper) |
| 3 Final | path, cracks, final varve marks with numbers, traced horizons, measurements |

Each layer can be switched off before export: path, marks, numbers, labels.
Unsaved work is included, because the export shows the state at that moment.

### 11.2 Extent and resolution

Export opens a dialog with a **live preview** of the file that will be
written; every option below updates it.

- **Whole section, full resolution (default)**: the full image at its native
  pixel size, in its original orientation, with the overlay redrawn on top.
  For figures. Line widths and label sizes are scaled to the image (a set size
  in mm on the section, not in screen pixels: at size 1× labels are about
  0.35 mm high), so they stay readable when printed. A size slider (0.5–4×)
  adjusts them.
- **Current view only (toggle)**: exactly what is on screen (zoom, rotation,
  brightness and contrast), at screen resolution. Quick, for notes and
  messages. Its DPI is the scan DPI × zoom.
- Brightness and contrast are applied as set on screen (an option allows the
  untouched image).

### 11.3 Format

- **PNG** (lossless). The section's DPI is written into the file (`pHYs`), so
  the exported image keeps its scale and can be measured in other software.
- Optional **caption strip** under the image: project, section, module,
  person, date and time, core depth range, number of marks, DPI. Off by
  default for clean figure panels.
- Optional **scale bar** (e.g. 1 mm) drawn in a corner.
- File name: `<project>.<section>.<module>[.<person>].<yyyymmdd-hhmm>.png`,
  e.g. `ZAB-12.ZAB-12-1_0-10.count.P2.20261123-1530.png`.
- A full-resolution 2400 DPI section (about 9,500 × 1,900 px) is a few MB,
  well within browser limits.

## 12. Plan

1. **Version 1:** project setup (people, sections, DPI, segments with the
   joint guide, anchors, gap/overlap check) + Module 1 (blind counting) +
   counts JSON/CSV. *(Done.)*
   **Version 1.1:** image export (section 11) for Setup and Module 1. Later
   modules add their overlays to the same export. *(Done.)*
2. **Version 2:** Module 2 (matching, review, Method C, chronology CSV). *(Done.)*
3. **Version 3:** Module 3 step 1 (cracks on the path, final varve depths,
   varves and cracks CSV). *(Done.)*
4. **Version 4:** Module 3 step 2 (horizons, quick lines, thickness CSV).

## 13. Open questions

None at the moment.

Decided: traced horizons are the Module 3 default, with quick lines as the
fallback; no "uncertain" flag in Module 1; the Method C threshold is always a
strict majority; cracks are marked only in Module 3; image export defaults to
the whole section at full resolution, with a toggle for the current view; the tool exports varve
numbers only, with no calendar ages (floating chronologies are fine).
