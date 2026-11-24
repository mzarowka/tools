"""Synthetic thin-section scans for the manual's screenshots (not real data).

Usage: python varves/dev/demo_images.py OUTDIR
Sections are vertical, as they are counted: depth runs down the image (top of
the section at the top), laminae run across it.

Writes demo-1.tif, demo-2.tif (2400 dpi, LZW; ACROSS px wide, ALONG px high)
and demo.json with the true boundaries. A boundary with base b lies at the row
  y(x) = b + tilt * (x - ACROSS/2) + amp * sin(2*pi*x/wave + phase) + wobble[x]
so the screenshot script can place clicks on it.
"""

import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

DPI = 2400
# generated with depth along x, then turned so that depth runs down the image
W, H, MARGIN = 3600, 900, 70
rng = np.random.default_rng(7)

# lamina geometry shared by both sections: gentle tilt + lateral waviness
TILT, AMP, WAVE = 0.035, 7.0, 1500.0


def couplet(f):
    """Colour across one varve, f = 0 at its base (spring calcite) to 1 at its top."""
    stops = np.array([0.0, 0.07, 0.13, 0.20, 0.70, 0.86, 0.93, 1.0])
    cols = np.array([[236, 228, 200], [228, 218, 186], [150, 132, 96], [118, 101, 72],
                     [104, 88, 62], [80, 66, 47], [46, 37, 27], [58, 47, 34]], float)
    rgb = np.stack([np.interp(f, stops, cols[:, c]) for c in range(3)], -1)
    sub = 1 + 0.07 * np.sin(f * 2 * np.pi * 6.5) * ((f > 0.2) & (f < 0.8))   # faint sub-laminae
    return rgb * sub[..., None]


def blurred_noise(shape, sigma, amp):
    n = rng.normal(0, 1, shape)
    im = Image.fromarray(((n + 4) * 32).clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(sigma))
    a = np.asarray(im, float)
    return (a - a.mean()) / (a.std() + 1e-9) * amp


def section(first_x, n_varves_hint, phase, crack_at=None):
    # varve bases along x; depth increases with x, so the youngest varve is at the left
    xs = [first_x]
    trend = rng.uniform(95, 130)
    while xs[-1] < W + 200:
        trend = np.clip(trend + rng.normal(0, 6), 70, 165)
        xs.append(xs[-1] + max(45, rng.normal(trend, 18)))
    xs = np.array(xs)
    yy, xx = np.mgrid[0:H, 0:W].astype(float)
    wobble = np.cumsum(rng.normal(0, 0.35, H)); wobble -= wobble.mean()
    shift = TILT * (yy - H / 2) + AMP * np.sin(2 * np.pi * yy / WAVE + phase) + wobble[:, None]
    u = xx - shift                       # position in "unfolded" lamina coordinates
    i = np.clip(np.searchsorted(xs, u, side="right") - 1, 0, len(xs) - 2)
    f = (u - xs[i]) / (xs[i + 1] - xs[i])
    f = 1 - f                            # calcite at the base (right side = deeper)
    img = couplet(f)
    img *= (0.85 + 0.25 * rng.random(len(xs)))[i][..., None]     # varve-to-varve tone
    img *= (1 + blurred_noise((H, W), 9, 0.07) + blurred_noise((H, W), 0.8, 0.10))[..., None]
    sparks = rng.random((H, W)) > 0.997
    img[sparks] = img[sparks] * 0.4 + np.array([235, 228, 205]) * 0.6
    dark = rng.random((H, W)) > 0.9975
    img[dark] *= 0.45
    if crack_at is not None:            # open crack along one boundary, filled with dark resin
        b = xs[crack_at]
        d = u - b
        gap = (d > -5) & (d < 6)
        img[gap] = [24, 27, 34]
    resin = (yy < MARGIN + 6 * np.sin(xx / 400)) | (yy > H - MARGIN + 6 * np.sin(xx / 500 + 1))
    img[resin] = [196, 204, 212]
    img = np.clip(img + rng.normal(0, 4, img.shape), 0, 255).astype(np.uint8)
    img = np.ascontiguousarray(img.transpose(1, 0, 2))           # depth down the image
    return Image.fromarray(img, "RGB"), xs, wobble


def main(out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    meta = {"across": H, "along": W, "tilt": TILT, "amp": AMP, "wave": WAVE, "sections": []}
    for k, (phase, crack) in enumerate([(0.4, 14), (1.7, None)], 1):
        im, xs, wobble = section(rng.uniform(40, 90), 30, phase, crack)
        name = f"demo-{k}.tif"
        im.save(out / name, compression="tiff_lzw", dpi=(DPI, DPI))
        meta["sections"].append({"file": name, "phase": phase, "bases": [float(v) for v in xs if 0 < v < W],
                                 "crack_x": float(xs[crack]) if crack is not None else None,
                                 "wobble": [round(float(v), 3) for v in wobble]})
    (out / "demo.json").write_text(json.dumps(meta))
    print("wrote", out)


if __name__ == "__main__":
    main(sys.argv[1])
