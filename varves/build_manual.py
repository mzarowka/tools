"""Build manual.html from MANUAL.md.

Usage:  python varves/build_manual.py      (needs: pip install markdown==3.7)

The output is one self-contained HTML file (no external resources), so it
opens offline next to index.html. It is regenerated automatically on every
push to main that changes MANUAL.md (.github/workflows/varves-manual.yml).
Do not edit manual.html by hand.
"""

import html
import re
from pathlib import Path

import markdown

HERE = Path(__file__).resolve().parent
SRC = HERE / "MANUAL.md"
OUT = HERE / "manual.html"


def github_slug(value, separator="-"):
    """Heading ids as GitHub makes them, so the manual's own links keep working."""
    value = re.sub(r"<[^>]+>", "", value).strip().lower()
    value = re.sub(r"[^\w\- ]", "", value)
    return value.replace(" ", separator)


def normalise_indent(text):
    """GitHub accepts 2-3 spaces for nested lists; Python-Markdown needs 4."""
    out, fenced = [], False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            fenced = not fenced
        if not fenced and line.strip():
            n = len(line) - len(line.lstrip(" "))
            if 0 < n:
                line = " " * (4 * ((n + 1) // 3 if n < 4 else (n + 3) // 4)) + line.lstrip(" ")
        out.append(line)
    return "\n".join(out) + "\n"


def build():
    text = SRC.read_text(encoding="utf-8")
    source = normalise_indent(text)
    md = markdown.Markdown(
        extensions=["tables", "fenced_code", "sane_lists", "toc"],
        extension_configs={"toc": {"slugify": github_slug, "toc_depth": "2-2"}},
    )
    body = md.convert(source)
    title = re.search(r"^# (.+)$", text, re.M).group(1)
    page = TEMPLATE.replace("{{title}}", html.escape(title)).replace("{{toc}}", md.toc).replace("{{body}}", body)
    OUT.write_text(page, encoding="utf-8")
    print(f"Wrote {OUT.relative_to(HERE.parent)} ({len(page) // 1024} kB)")


TEMPLATE = """<!doctype html>
<!-- Generated from MANUAL.md by build_manual.py. Do not edit by hand. -->
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{title}}</title>
<style>
  :root {
    --bg: #f6f7f9; --paper: #fff; --ink: #1d2327; --muted: #5f6b73; --line: #d9dee3;
    --accent: #1f6feb; --code-bg: #f1f3f5; --note-bg: #eef4ff; --note-line: #9cbcf5;
  }
  @media (prefers-color-scheme: dark) {
    :root:not([data-theme="light"]) {
      --bg: #15181b; --paper: #1c2024; --ink: #e3e7ea; --muted: #9aa5ad; --line: #30363c;
      --accent: #6ea8fe; --code-bg: #252a2f; --note-bg: #1d2a3d; --note-line: #3d5f94;
    }
  }
  :root[data-theme="dark"] {
    --bg: #15181b; --paper: #1c2024; --ink: #e3e7ea; --muted: #9aa5ad; --line: #30363c;
    --accent: #6ea8fe; --code-bg: #252a2f; --note-bg: #1d2a3d; --note-line: #3d5f94;
  }
  * { box-sizing: border-box; }
  html { scroll-padding-top: 16px; }
  body {
    margin: 0; background: var(--bg); color: var(--ink);
    font: 16px/1.6 system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  }
  .layout { display: grid; grid-template-columns: 280px minmax(0, 1fr); max-width: 1240px; margin: 0 auto; }
  nav.toc {
    position: sticky; top: 0; align-self: start; height: 100vh; overflow-y: auto;
    padding: 28px 18px 28px 22px; font-size: 14px; border-right: 1px solid var(--line);
  }
  nav.toc .brand { font-weight: 700; margin-bottom: 12px; }
  nav.toc ul { list-style: none; margin: 0; padding: 0; }
  nav.toc li { margin: 2px 0; }
  nav.toc a { color: var(--muted); text-decoration: none; display: block; padding: 3px 8px; border-radius: 5px; }
  nav.toc a:hover { color: var(--ink); background: var(--code-bg); }
  nav.toc a.active { color: var(--accent); background: var(--note-bg); }
  main { padding: 28px 48px 80px; min-width: 0; }
  article { background: var(--paper); border: 1px solid var(--line); border-radius: 10px; padding: 34px 44px; }
  h1 { font-size: 30px; line-height: 1.25; margin: 0 0 14px; }
  h2 { font-size: 22px; margin: 44px 0 12px; padding-top: 18px; border-top: 1px solid var(--line); }
  h3 { font-size: 17px; margin: 28px 0 8px; }
  a { color: var(--accent); }
  hr { display: none; }
  p, li { max-width: 76ch; }
  code { font: 0.88em ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; background: var(--code-bg); padding: 1px 5px; border-radius: 4px; }
  pre { background: var(--code-bg); padding: 14px 16px; border-radius: 8px; overflow-x: auto; line-height: 1.45; }
  pre code { background: none; padding: 0; font-size: 13.5px; }
  blockquote { margin: 16px 0; padding: 10px 16px; background: var(--note-bg); border-left: 4px solid var(--note-line); border-radius: 0 8px 8px 0; }
  blockquote p { margin: 6px 0; }
  .table-wrap { overflow-x: auto; margin: 14px 0; }
  table { border-collapse: collapse; font-size: 14.5px; min-width: 60%; }
  th, td { border: 1px solid var(--line); padding: 6px 10px; text-align: left; vertical-align: top; }
  th { background: var(--code-bg); }
  .theme { position: fixed; right: 14px; top: 12px; font: inherit; font-size: 13px; padding: 4px 10px;
    border: 1px solid var(--line); border-radius: 6px; background: var(--paper); color: var(--ink); cursor: pointer; }
  @media (max-width: 900px) {
    .layout { display: block; }
    nav.toc { position: static; height: auto; border-right: 0; border-bottom: 1px solid var(--line); padding: 16px; }
    main { padding: 16px; }
    .theme { position: absolute; }
    article { padding: 20px 16px; border-radius: 8px; }
    h1 { font-size: 24px; }
  }
  @media print {
    nav.toc, .theme { display: none; }
    .layout { display: block; }
    main { padding: 0; }
    article { border: 0; padding: 0; }
    body { background: #fff; color: #000; }
    h2 { break-after: avoid; }
  }
</style>
</head>
<body>
<button class="theme" id="theme" title="Switch light / dark">Light / dark</button>
<div class="layout">
  <nav class="toc" aria-label="Contents">
    <div class="brand">Varve counter · manual</div>
    {{toc}}
  </nav>
  <main><article>
{{body}}
  </article></main>
</div>
<script>
  // tables scroll sideways on narrow screens
  document.querySelectorAll('article table').forEach(t => {
    const w = document.createElement('div'); w.className = 'table-wrap';
    t.parentNode.insertBefore(w, t); w.appendChild(t);
  });
  // theme toggle (remembered in this browser when possible)
  const root = document.documentElement;
  try { const t = localStorage.getItem('varves-manual-theme'); if (t) root.dataset.theme = t; } catch (e) {}
  document.getElementById('theme').addEventListener('click', () => {
    const dark = root.dataset.theme ? root.dataset.theme === 'dark' : matchMedia('(prefers-color-scheme: dark)').matches;
    root.dataset.theme = dark ? 'light' : 'dark';
    try { localStorage.setItem('varves-manual-theme', root.dataset.theme); } catch (e) {}
  });
  // highlight the current chapter in the contents
  const links = [...document.querySelectorAll('nav.toc a')];
  const heads = links.map(a => document.getElementById(decodeURIComponent(a.hash.slice(1)))).filter(Boolean);
  const mark = () => {
    let cur = heads[0];
    for (const h of heads) if (h.getBoundingClientRect().top < 120) cur = h;
    links.forEach(a => a.classList.toggle('active', cur && a.hash === '#' + cur.id));
  };
  addEventListener('scroll', mark, { passive: true }); mark();
</script>
</body>
</html>
"""

if __name__ == "__main__":
    build()
