// Screenshots for MANUAL.md, taken from the real tool on synthetic demo images.
//
//   python varves/dev/demo_images.py /tmp/demo
//   node varves/dev/screenshots.js /tmp/demo varves/manual-img
//
// Needs Node.js with Playwright and Chromium. The demo data are synthetic:
// three counters are simulated from the known boundaries, with a few planted
// disagreements, so that every module has something to show.

const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const [demoDir, outDir] = process.argv.slice(2).map(p => path.resolve(p));
if (!demoDir || !outDir) { console.error('usage: node screenshots.js DEMO_DIR OUT_DIR'); process.exit(1); }
fs.mkdirSync(outDir, { recursive: true });
const meta = JSON.parse(fs.readFileSync(path.join(demoDir, 'demo.json'), 'utf8'));
const TOOL = 'file://' + path.resolve(__dirname, '..', 'index.html');

// Sections are vertical: depth runs down the image, laminae across it.
// Depth (row) of a boundary with base b at column x of section k (0-based):
const shift = (k, x) => {
  const s = meta.sections[k], xi = Math.max(0, Math.min(meta.across - 1, Math.round(x)));
  return meta.tilt * (x - meta.across / 2) + meta.amp * Math.sin(2 * Math.PI * x / meta.wave + s.phase) + s.wobble[xi];
};
const by = (k, b, x) => b + shift(k, x);
const P = (x, y) => [x, y];   // image point: x across, y depth

(async () => {
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width: 1360, height: 820 }, deviceScaleFactor: 1 });
  await ctx.addInitScript(() => { window.showOpenFilePicker = undefined; window.showSaveFilePicker = undefined; });
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  page.on('dialog', d => (d.type() === 'prompt' ? d.accept('DEMO-1') : d.accept()));
  const shot = async (name, settle = 250, panelSel = null) => {
    await page.evaluate(sel => {
      document.getElementById('toast').className = 'toast';              // no stale messages
      const panel = document.querySelector('.panel');
      const el = sel && document.querySelector(sel);
      panel.scrollTop = el ? Math.max(0, el.getBoundingClientRect().top - panel.getBoundingClientRect().top + panel.scrollTop - 330) : 0;
    }, panelSel);
    await page.waitForTimeout(settle);
    await page.screenshot({ path: path.join(outDir, name + '.jpg'), type: 'jpeg', quality: 86 });
    console.log('  ' + name);
  };
  const view = (x, y, scale) => page.evaluate(([x, y, scale]) => {
    view.scale = scale; updM();
    const q = toScreen([x, y]); view.tx += W() / 2 - q[0]; view.ty += H() / 2 - q[1]; updM(); requestDraw();
  }, [x, y, scale]);

  await page.goto(TOOL);

  // ---- Step A: project ------------------------------------------------------
  await page.click('#btnNew');
  for (let i = 0; i < 3; i++) await page.click('#btnAddPerson');
  await page.setInputFiles('#addImgs', meta.sections.map(s => path.join(demoDir, s.file)));
  await page.waitForFunction(() => state.project.sections.length === 2 && state.images.size === 2);
  await page.selectOption('#personSel', 'P1');

  // ---- Step B: setup ---------------------------------------------------------
  const X1 = 450, X2 = 260, J = 1700;                // segment 1 at column 450 down to depth 1700
  const j2 = J + shift(0, X2) - shift(0, X1);         // segment 2 starts on the same lamina, shifted sideways
  await page.evaluate(([J, X1, j2, X2]) => {
    const [s1, s2] = state.project.sections;
    s1.segments = [{ id: 1, points: [[X1, 25], [X1 - 15, 900], [X1, J]] }];
    s2.segments = [{ id: 1, points: [[450, 25], [450, 3575]] }];
    s2.anchors = { top_mm: null, bottom_mm: null };
    touchPath(s1); touchPath(s2);
    selectSection(s1.id);
  }, [J, X1, j2, X2]);
  await page.click('[data-tab="setup"]');
  await page.evaluate(([j2, X2]) => { setTool('draw'); state.draft = [[X2, Math.round(j2)], [X2 + 10, 2300]]; state.cursor = [X2 + 4, 2650]; }, [j2, X2]);
  await view(360, 1900, 0.62);
  await shot('02-setup-path', 250, '#segList');
  await page.evaluate(([j2, X2]) => {
    const s1 = state.project.sections[0];
    state.draft = null; setTool('edit');
    s1.segments.push({ id: 2, points: [[X2, Math.round(j2 * 10) / 10], [X2 + 10, 2300], [X2, 3575]] });
    s1.anchors = { top_mm: 0, bottom_mm: 39.5 };
    state.project.sections[1].anchors = { top_mm: 39.5, bottom_mm: 78.6 };
    touchPath(s1); refreshAll();
  }, [j2, X2]);

  await page.click('[data-tab="project"]');
  await page.evaluate(() => fitView());
  await shot('01-project');

  // ---- Step C: simulated counts of three counters -------------------------------
  const jitter = (i, k) => ((i * 7 + k * 5) % 7) - 3;
  const sec1 = meta.sections[0].bases.map(b => {
    const d1 = by(0, b, X1);
    return d1 < J ? P(X1, d1) : P(X2, by(0, b, X2));
  }).filter(p => p[1] > 30 && p[1] < 3570 && !(p[0] === X2 && p[1] < j2));
  const sec2 = meta.sections[1].bases.map(b => P(450, by(1, b, 450))).filter(p => p[1] > 30 && p[1] < 3570);
  const mk = (pts, k, skip, extra) => pts.map((p, i) => (skip.includes(i) ? null : [p[0], p[1] + jitter(i, k)])).filter(Boolean).concat(extra);
  const mid = (pts, i) => [pts[i][0], (pts[i][1] + pts[i + 1][1]) / 2];
  const spec = {
    P1: { [meta.sections[0].file.replace('.tif', '')]: mk(sec1, 1, [], []), [meta.sections[1].file.replace('.tif', '')]: mk(sec2, 1, [], [mid(sec2, 4)]) },
    P2: { [meta.sections[0].file.replace('.tif', '')]: mk(sec1, 2, [6, 21], [mid(sec1, 11)]), [meta.sections[1].file.replace('.tif', '')]: mk(sec2, 2, [], []) },
    P3: { [meta.sections[0].file.replace('.tif', '')]: mk(sec1, 3, [6, 30], []), [meta.sections[1].file.replace('.tif', '')]: mk(sec2, 3, [9], []) },
  };
  const files = await page.evaluate(spec => {
    const out = {};
    for (const [P, secs] of Object.entries(spec)) {
      const c = { schema: SCHEMA_COUNTS, app: APP, project: state.project.project, person: P, sections: {}, created: nowISO(), modified: nowISO() };
      for (const [sid, pts] of Object.entries(secs)) {
        const sec = secById(sid), cs = { image_sha256: sec.image.sha256, path_sig: pathSig(sec), boundaries: [] };
        pts.sort((a, b) => locate(sec, a).s - locate(sec, b).s).forEach((q, i) => {
          const l = locate(sec, q);
          cs.boundaries.push({ id: 'b' + String(i + 1).padStart(4, '0'), seg: l.seg, s_px: round(l.s, 2), x: round(q[0], 1), y: q[1] });
        });
        c.sections[sid] = cs;
      }
      out[P] = JSON.stringify(c);
    }
    return out;
  }, spec);

  await page.click('[data-tab="count"]');
  await page.evaluate(t => { state.counts = JSON.parse(t); state.countsDirty = true; state.selB = 'b0009'; refreshAll(); }, files.P1);
  await view(450, 1050, 0.78);
  await shot('03-count');

  // ---- Step D: Method C ---------------------------------------------------------
  await page.click('[data-tab="decide"]');
  await page.evaluate(async files => {
    await loadCountsFiles(Object.entries(files).map(([P, t]) => new File([t], `DEMO-1.${P}.counts.json`)));
  }, files);
  await page.click('#dMatch');
  await page.evaluate(() => {
    const r = m2Result().rows.find(x => x.sec === state.secId && x.status === 'majority');
    m2.sel = { secId: r.sec, gid: r.g.id, p: r.ms[0].p, b: r.ms[0].b };
    renderDecide();
    view.scale = 0.95; updM(); centerOnS(curSec(), r.s);
  });
  await shot('04-decide', 250, '#dSel');

  // ---- Step E: cracks on the path -------------------------------------------------
  await page.click('[data-tab="final"]');
  await page.click('#fTake');
  const cy = by(0, meta.sections[0].crack_x, X1);
  await page.evaluate(([a, b, x]) => { const sec = curSec(); crackClick(sec, [x, a]); crackClick(sec, [x, b]); }, [cy - 5, cy + 6, X1]);
  await page.check('#fDone');
  await view(X1, cy, 1.9);
  await shot('05-final-cracks', 250, '#fSecStats');

  // ---- Step F: horizons -------------------------------------------------------------
  await page.evaluate(() => setM3Tool('horizon'));
  const xs = [120, 300, 640, 790];
  const rows = await page.evaluate(() => finalRows(state.secId).map(r => ({ gid: r.g.id, s: r.s })));
  const bases = meta.sections[0].bases;
  const crackB = meta.sections[0].crack_x;
  const seg1 = await page.evaluate(() => segLength(curSec().segments[0]));
  for (const r of rows) {
    const p = await page.evaluate(s => pathPointAtS(curSec(), s).pt, r.s);
    if (r.s >= seg1 || p[1] < 700 || p[1] > 1690) continue;       // a stretch of segment 1
    const b = bases.reduce((a, v) => (Math.abs(by(0, v, X1) - p[1]) < Math.abs(by(0, a, X1) - p[1]) ? v : a), bases[0]);
    const pts = xs.map(x => P(x, by(0, b, x)));
    await page.evaluate(([gid, pts, crack]) => {
      m3.hsel = gid;
      if (crack) {
        m3.stage = 'upper'; m3.draft = pts.map(q => [q[0], q[1] - 5]); finishM3Draft();
        m3.draft = pts.map(q => [q[0], q[1] + 6]); finishM3Draft();
      } else { m3.stage = 'single'; m3.draft = pts; finishM3Draft(); }
    }, [r.gid, pts, b === crackB]);
  }
  await page.evaluate(() => { const r = finalRows(state.secId).filter(x => pathPointAtS(curSec(), x.s).pt[1] > 1100)[0]; selectBoundary(state.secId, r.g.id, false); });
  await view(450, 1200, 0.82);
  await shot('06-final-horizons', 250, '#m3Sel');

  // ---- Export dialog ----------------------------------------------------------------------
  await page.click('[data-tab="decide"]');
  await view(450, 1050, 0.95);
  await page.keyboard.press('e');
  await page.check('#exCap'); await page.check('#exBar');
  await shot('07-export', 600);

  if (errors.length) { console.error('page errors:', errors); process.exit(1); }
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
