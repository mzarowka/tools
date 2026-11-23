# Varve counter — design

Status: **draft for discussion**. Nothing is implemented yet.

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
Module 2  Chronology (Method C) ► chronology file: matched boundaries, ±uncertainty
        │
        ▼
Module 3  Thickness ─────────► thickness file: traced horizons, measurements
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
   - Stored per click: `s` (px), the raw `x, y` (px), and an optional note.
   - Drag to move a click, Delete to remove it, undo/redo, autosave in the
     browser between saves.
   - Live readout: number of boundaries, last varve thickness, current
     core depth.
3. **Blind counting:** the counts of other people are never shown in
   Module 1. Each counter saves their own counts file.

## 6. Module 2 — Chronology (Method C)

### 6.1 Rule

For each boundary, count how many counters marked it (`n_agree` of `N`).
With the agreement threshold `k`:

| Agreement | Effect |
|---|---|
| `n_agree = N` | boundary accepted, no uncertainty added |
| `k ≤ n_agree < N` | boundary accepted, **negative** uncertainty +1 |
| `n_agree < k` | boundary rejected, **positive** uncertainty +1 |

The default is `N = 3`, `k = 2`, which reproduces the paper exactly. Larger
`N` works the same way (`k` defaults to a simple majority). Positive and
negative uncertainties are summed **separately** from the top of the record
down, across sections in project order, which gives asymmetric ranges such
as +34/−53.

### 6.2 Matching boundaries between counters

The rule above needs to know which clicks of different counters are the same
boundary. This is done in two steps.

**Automatic proposal**

- Work per section, on `s`. All counters used the same path, so their
  positions are directly comparable.
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

### 6.3 Output

- The accepted boundaries define the **final varves**.
- For each varve: number, section, top and bottom core depth, `n_agree`,
  which counters marked it, and the cumulative ± uncertainty.
- Rejected boundaries are kept (with `included = false`), because they carry
  the positive uncertainty and show where the counters disagree.

## 7. Module 3 — Thickness

Goal: varve thickness across the width of the section, not only along one
line, and correct where laminae bend.

### 7.1 Proposal: traced horizons

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

### 7.2 Fallback: quick lines

For simple, parallel laminae, a quicker mode: draw up to 3 lines per varve,
each from base to top. The thickness is the line length. Results are marked
with `method = "line"` so the two modes are never mixed silently.

### 7.3 Units

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
| `<project>.thickness.json` | Module 3 | horizons, measurements |

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
    "method_c": { "k": 2, "tolerance_fraction": 0.5, "window": 10 }
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
        { "id": "b0001", "s_px": 412.6, "x": 532, "y": 951, "note": "" }
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
| `counts.csv` | click | `project, section, person, boundary_id, s_mm, core_depth_mm, x_px, y_px, note` |
| `chronology.csv` | matched group | `project, section, group_id, varve_no, included, n_agree, n_counters, persons, core_depth_mm, top_mm, bottom_mm, unc_pos_cum, unc_neg_cum` |
| `thickness.csv` | measurement | `project, section, varve_no, method, position_no, x_px, thickness_px, thickness_mm, thickness_corr_mm, measured_by` |

`varve_no` is empty for rejected groups. Summaries (mean, SD, n per varve) are
left to R.

## 10. Images

- **BMP** is shown natively by the browser.
- **TIFF** needs a small decoder library (e.g. UTIF.js), which also gives the
  DPI tags.
- A 10 cm thin section at 2400 DPI is about 9,500 × 1,900 px, which a plain
  canvas viewer handles easily, so no tiling is needed. Very large scans
  (stitched cores, 4800 DPI) are out of scope for now.
- Saving uses the File System Access API where available (Chrome, Edge: save
  in place). Other browsers fall back to downloading the file.

## 11. Plan

1. **Version 1:** project setup (people, sections, DPI, segments with the
   joint guide, anchors, gap/overlap check) + Module 1 (blind counting) +
   counts JSON/CSV.
2. **Version 2:** Module 2 (matching, review, Method C, chronology CSV).
3. **Version 3:** Module 3 (horizons, measurements, thickness CSV).

## 12. Open questions

- Module 3: are traced horizons (7.1) the right default, with quick lines
  (7.2) as the fallback?
- Should Module 1 allow an optional "uncertain" flag on a click? Method C does
  not need it, but it might help in the Module 2 review.
- Default `k` for even `N` (e.g. 4 counters): 2 or 3?
