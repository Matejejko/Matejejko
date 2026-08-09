#!/usr/bin/env python3
"""
Regenerate the text-art portrait inside assets/terminal.svg.

The portrait is derived from the GitHub avatar: the photo is downscaled to a
monospace character grid, each cell picking a glyph by ink coverage and a
colour by tone. The backdrop of the source photo is near-pure crimson while
skin and the uniform carry real green, so luminance is computed with red
de-weighted -- that drops the background out without any masking.

    pip install pillow
    python3 tools/generate-portrait.py

Requires DejaVu Sans Mono (or set MONO) only for the glyph-coverage pass.
"""
import io
import os
import random
import urllib.request

from PIL import Image, ImageDraw, ImageFilter, ImageFont

AVATAR = "https://avatars.githubusercontent.com/u/155886081?v=4&s=460"
MONO = os.environ.get("MONO", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf")
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

COLS, ROWS = 68, 37
CROP = (0.21, 0.01, 0.81, 0.61)          # square, framed tight on the head
BLACK, WHITE, GAMMA, CRISP = 43, 141, 0.60, 150

# glyph cell metrics inside the SVG
ART_X, ART_Y, ART_FS, ART_LH = 28, 112, 10, 11

CANDIDATES = " .'`^\",:;-~+=<>ilItfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
LEVELS = 14

# --- the portrait keeps moving: a share of cells cycle through glyphs -------
SEED = 7                  # fixed, so regenerating gives the same art
LIVE_FRACTION = 0.35      # share of eligible cells that animate
LIVE_TONE = (0.05, 1.00)  # a same-coverage swap costs no tone, so any cell may move
LIVE_GROUPS = 3           # independent timings per row, so a row never blinks as one
PHASES = 3                # glyphs each animated cell rotates through
BUCKET_SPREAD = 0.055     # how far apart in coverage interchangeable glyphs may be
BUCKET_SIZE = 5           # candidates kept per ramp level
CYCLE = (1.5, 3.0)        # seconds for a full rotation through the phases
CYCLE_START = 2.2         # let the fetch finish drawing before anything moves
SCAN_START = 2.4

# ---------------------------------------------------------------- palettes ---
DARK = dict(
    surface="#161b22", chrome="#0d1117", border="#30363d", rule="#484f58",
    text="#e6edf3", muted="#8b949e", accent="#3fb950", blue="#58a6ff",
    swatches=["#484f58", "#ff7b72", "#3fb950", "#d29922",
              "#58a6ff", "#bc8cff", "#39c5cf", "#e6edf3"],
    # tone ramp for the portrait, darkest cell first
    ink=[(0x17, 0x3d, 0x24), (0x23, 0x86, 0x36), (0x3f, 0xb9, 0x50),
         (0x6d, 0xdc, 0x7c), (0xd2, 0xfa, 0xd8)],
)

# ------------------------------------------------------------------ fetch ----
ROWS_INFO = [
    ("OS:", "CachyOS Linux x86_64"),
    ("Role:", "DevOps Intern @ Deutsche Telekom"),
    ("School:", "SPŠE Košice · dual program"),
    ("Stack:", "Kubernetes · Docker · AWS"),
    ("IaC:", "Terraform"),
    ("Langs:", "Python · JavaScript · Bash"),
    ("Editor:", "Vim · VS Code"),
    ("Locales:", "sk · en C1 · ja N4 · de A2"),
    ("Focus:", "self-hosting · homelab"),
    ("WWW:", "matejejko.github.io"),
]
COMMAND = "fastfetch --logo ~/.face"


def measure_coverage():
    """Ink coverage of every candidate glyph, as a fraction of its cell."""
    font = ImageFont.truetype(MONO, 48)
    cov = {}
    for ch in CANDIDATES:
        img = Image.new("L", (48, 60), 0)
        ImageDraw.Draw(img).text((6, 2), ch, fill=255, font=font)
        cov[ch] = sum(img.convert("L").tobytes()) / (255 * 48 * 60)
    return cov


def build_ramp(cov):
    """Order glyphs by measured ink coverage so tone steps are even."""
    lo, hi = min(cov.values()), max(cov.values())
    ramp = []
    for i in range(LEVELS):
        target = lo + (hi - lo) * i / (LEVELS - 1)
        best = min(cov, key=lambda c: abs(cov[c] - target))
        if best not in ramp:
            ramp.append(best)
    return "".join(ramp)


def build_buckets(cov, ramp):
    """
    Interchangeable glyphs for each ramp level.

    Swapping a cell for its ramp neighbour barely reads at 10px -- `r` and `t`
    are near enough to identical that the change is invisible. Swapping it for
    a *different* character of the same ink coverage is obvious to the eye and
    costs the portrait nothing, because the cell's density, and so the tone,
    does not move.
    """
    span = max(cov.values()) - min(cov.values())
    buckets = []
    for ch in ramp:
        near = sorted((c for c in CANDIDATES if not c.isspace()
                       and abs(cov[c] - cov[ch]) <= span * BUCKET_SPREAD),
                      key=lambda c: abs(cov[c] - cov[ch]))
        if ch in near:
            near.remove(ch)
        buckets.append([ch] + near[:BUCKET_SIZE - 1])
    return buckets


COV = measure_coverage()
RAMP = build_ramp(COV)
BUCKETS = build_buckets(COV, RAMP)


def tonemap():
    with urllib.request.urlopen(AVATAR) as r:
        img = Image.open(io.BytesIO(r.read())).convert("RGB")
    w, h = img.size
    img = img.crop((int(w * CROP[0]), int(h * CROP[1]),
                    int(w * CROP[2]), int(h * CROP[3])))
    small = img.resize((COLS, ROWS), Image.LANCZOS)

    lum = Image.new("L", (COLS, ROWS))
    for y in range(ROWS):
        for x in range(COLS):
            R, G, B = small.getpixel((x, y))
            lum.putpixel((x, y), min(255, round(0.15 * R + 0.65 * G + 0.20 * B)))
    lum = lum.filter(ImageFilter.UnsharpMask(radius=1, percent=CRISP, threshold=0))

    span = WHITE - BLACK
    grid = [[max(0.0, min(1.0, (lum.getpixel((x, y)) - BLACK) / span)) ** GAMMA
             for x in range(COLS)] for y in range(ROWS)]
    return recenter(drop_islands(despeckle(grid)))


def recenter(grid):
    """
    Centre the surviving art in the character grid.

    The tone curve eats the unlit top of the hair and the shadow down one
    side, so the portrait ends up sitting low and left of where the crop put
    it. Shifting by whole cells keeps every column aligned, and staying in
    cell units means the result does not depend on the reader's font metrics.
    """
    live = [(y, x) for y in range(ROWS) for x in range(COLS) if grid[y][x] > 0.0]
    if not live:
        return grid
    y0, y1 = min(y for y, _ in live), max(y for y, _ in live)
    x0, x1 = min(x for _, x in live), max(x for _, x in live)
    dy = (ROWS - (y1 - y0 + 1)) // 2 - y0
    dx = (COLS - (x1 - x0 + 1)) // 2 - x0

    out = [[0.0] * COLS for _ in range(ROWS)]
    for y, x in live:
        out[y + dy][x + dx] = grid[y][x]
    return out


def despeckle(grid, thresh=0.18):
    """Drop lone faint cells so the backdrop reads as empty, not dusty."""
    out = [row[:] for row in grid]
    for y in range(ROWS):
        for x in range(COLS):
            if grid[y][x] >= thresh:
                continue
            nb = [grid[y + dy][x + dx]
                  for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1))
                  if 0 <= y + dy < ROWS and 0 <= x + dx < COLS]
            if nb and max(nb) < thresh:
                out[y][x] = 0.0
    return out


def drop_islands(grid, min_size=14):
    """
    Erase small detached blobs.

    Stray highlights off in the backdrop -- a lit corner of the uniform, a
    glint -- survive the tone curve but land far from the subject, where they
    read as dirt on the terminal rather than as part of the portrait.
    """
    out = [row[:] for row in grid]
    seen = [[False] * COLS for _ in range(ROWS)]
    for sy in range(ROWS):
        for sx in range(COLS):
            if seen[sy][sx] or grid[sy][sx] <= 0.0:
                continue
            stack, comp = [(sy, sx)], []
            seen[sy][sx] = True
            while stack:
                y, x = stack.pop()
                comp.append((y, x))
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        ny, nx = y + dy, x + dx
                        if (0 <= ny < ROWS and 0 <= nx < COLS
                                and not seen[ny][nx] and grid[ny][nx] > 0.0):
                            seen[ny][nx] = True
                            stack.append((ny, nx))
            if len(comp) < min_size:
                for y, x in comp:
                    out[y][x] = 0.0
    return out


def glyph(v):
    """Tone straight to ink: the panel is dark, so a bright cell is a dense glyph."""
    if v <= 0.0:
        return " "
    return RAMP[max(1, min(len(RAMP) - 1, round(v * (len(RAMP) - 1))))]


def shade(v, stops, steps=12):
    q = round(v * steps) / steps
    t = q * (len(stops) - 1)
    i = min(len(stops) - 2, int(t))
    f = t - i
    a, b = stops[i], stops[i + 1]
    return "#%02x%02x%02x" % tuple(round(a[k] + (b[k] - a[k]) * f) for k in range(3))


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text_row(cells, y, cls, style):
    """
    One <text> per line, colour runs collapsed into <tspan>s.

    Cells stay in the text flow rather than being placed at absolute x, so a
    reader whose monospace font has a different advance width still gets
    columns that line up -- spaces reserve exactly the same width as glyphs.
    """
    runs = []
    for cell in cells:
        ch, key = cell if cell else (" ", None)
        if runs and runs[-1][1] == key:
            runs[-1][0] += ch
        else:
            runs.append([ch, key])
    while runs and runs[-1][1] is None:
        runs.pop()
    if not runs:
        return None
    spans = "".join(
        esc(t) if c is None else '<tspan fill="%s">%s</tspan>' % (c, esc(t))
        for t, c in runs
    )
    return ('    <text class="%s" x="%d" y="%d" xml:space="preserve" style="%s">%s</text>'
            % (cls, ART_X, ART_Y + y * ART_LH, style, spans))


def pick_live(grid, rng):
    """
    Choose the cells that will keep cycling through glyphs.

    Only mid-tones are eligible: swapping a glyph nudges a cell's density by
    one ramp step, which is a shimmer in the half-lit areas but would punch
    holes in the highlights that carry the likeness.
    """
    cand = [(y, x) for y in range(ROWS) for x in range(COLS)
            if LIVE_TONE[0] <= grid[y][x] <= LIVE_TONE[1]]
    live = {}
    for y, x in rng.sample(cand, round(len(cand) * LIVE_FRACTION)):
        i = max(1, min(len(RAMP) - 1, round(grid[y][x] * (len(RAMP) - 1))))
        opts = BUCKETS[i][:]
        if len(opts) < 2:
            continue
        rng.shuffle(opts)
        while len(opts) < PHASES:
            opts.append(opts[len(opts) % 2])
        live[(y, x)] = (opts[:PHASES], rng.randrange(LIVE_GROUPS))
    return live


def art_block(grid, theme):
    """
    The portrait, as a static base plus cycling glyph layers.

    A cell that animates is cut out of the base row and re-emitted once per
    phase in a layer of its own; the phases hand opacity to each other on a
    loop, so the character in that cell keeps changing while its colour and
    position hold still. Each row also sits in a group carrying a slow
    brightness wave, offset by row, which reads as a scan drifting down.
    """
    rng = random.Random(SEED)
    live = pick_live(grid, rng)
    ink = theme["ink"]
    out = []

    for y in range(ROWS):
        base = [None] * COLS
        for x in range(COLS):
            if grid[y][x] > 0.0 and (y, x) not in live:
                base[x] = (glyph(grid[y][x]), shade(grid[y][x], ink))
        rows = [text_row(base, y, "art fade", "animation-delay:%.2fs" % (1.45 + y * 0.018))]

        for group in range(LIVE_GROUPS):
            here = {x: opts for (ly, x), (opts, g) in live.items()
                    if ly == y and g == group}
            if not here:
                continue
            dur = rng.uniform(*CYCLE)
            start = CYCLE_START + rng.uniform(0, dur)
            for phase in range(PHASES):
                cells = [None] * COLS
                for x, opts in here.items():
                    cells[x] = (opts[phase], shade(grid[y][x], ink))
                style = "animation:%sph%d %.2fs %.2fs infinite;" % (
                    "show .45s %.2fs ease-out forwards," % (1.45 + y * 0.018) if phase == 0 else "",
                    phase, dur, start)
                rows.append(text_row(cells, y, "art lv p%d" % phase, style))

        rows = [r for r in rows if r]
        if not rows:
            continue
        out.append('    <g class="scan" style="animation-delay:%.2fs">\n%s\n    </g>'
                   % (SCAN_START + y * 0.10, "\n".join(rows)))
    return "\n".join(out)


def typed(text, x, y, theme, start=0.50, step=0.06):
    chars = "".join(
        '<tspan class="c" style="animation-delay:%.2fs">%s</tspan>'
        % (start + i * step, esc(ch)) if ch != " " else
        '<tspan class="c" style="animation-delay:%.2fs"> </tspan>' % (start + i * step)
        for i, ch in enumerate(text)
    )
    end = start + len(text) * step
    return (
        '  <text class="row" x="%d" y="%d" xml:space="preserve">'
        '<tspan fill="%s" font-weight="700">matej@cachyos</tspan>'
        '<tspan fill="%s"> </tspan><tspan fill="%s" font-weight="700">~</tspan>'
        '<tspan fill="%s"> $ </tspan><tspan fill="%s">%s</tspan>'
        '<tspan class="cursor-cmd" fill="%s">█</tspan></text>'
        % (x, y, theme["accent"], theme["muted"], theme["blue"], theme["muted"],
           theme["text"], chars, theme["text"]), end
    )


HEIGHT = 566
INFO_X = 470


def build(grid, theme):
    t = theme
    cmd, cmd_end = typed(COMMAND, 28, 86, t)
    hide = cmd_end + 0.35

    info = []
    y = 190
    for i, (k, v) in enumerate(ROWS_INFO):
        info.append(
            '  <text class="row fade" x="%d" y="%d" xml:space="preserve" '
            'style="animation-delay:%.2fs"><tspan fill="%s" font-weight="700">%s</tspan>'
            '<tspan fill="%s">%s</tspan></text>'
            % (INFO_X, y, 1.60 + i * 0.09, t["accent"], esc(k.ljust(11)),
               t["text"], esc(v))
        )
        y += 30

    swatches = "\n".join(
        '    <rect class="fade" style="animation-delay:%.2fs" x="%d" y="486" '
        'width="24" height="14" rx="2" fill="%s"/>'
        % (2.55 + i * 0.04, INFO_X + i * 28, c)
        for i, c in enumerate(t["swatches"])
    )

    return f'''<svg width="840" height="{HEIGHT}" viewBox="0 0 840 {HEIGHT}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Terminal running fastfetch, with a text-art portrait of Matej rendered from his profile picture beside a summary: DevOps intern at Deutsche Telekom, CS student at SPSE Kosice">
  <style>
    text {{
      font-family: ui-monospace, 'SF Mono', 'Cascadia Mono', Menlo, Consolas, 'DejaVu Sans Mono', monospace;
    }}
    .art {{ font-size: {ART_FS}px; }}
    .row {{ font-size: 13px; }}
    .ttl {{ font-size: 13px; }}
    .c    {{ opacity: 0; animation: show 0.01s forwards; }}
    .fade {{ opacity: 0; animation: show 0.45s ease-out forwards; }}
    .cursor     {{ animation: blink 1.1s step-end infinite; }}
    .cursor-cmd {{ animation: blink 1.1s step-end infinite, hide 0.1s {hide:.2f}s forwards; }}

    /* animated portrait cells: three glyph layers handing opacity to each other */
    .lv   {{ opacity: 0; }}
    .scan {{ animation: scan 6s ease-in-out infinite; }}

    @keyframes show  {{ to {{ opacity: 1; }} }}
    @keyframes blink {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0; }} }}
    @keyframes hide  {{ to {{ opacity: 0; }} }}
    @keyframes scan  {{ 0%, 66%, 100% {{ opacity: 1; }} 83% {{ opacity: 0.78; }} }}
    @keyframes ph0 {{ 0%, 30% {{ opacity: 1; }} 36%, 94% {{ opacity: 0; }} 100% {{ opacity: 1; }} }}
    @keyframes ph1 {{ 0%, 30% {{ opacity: 0; }} 36%, 63% {{ opacity: 1; }} 69%, 100% {{ opacity: 0; }} }}
    @keyframes ph2 {{ 0%, 63% {{ opacity: 0; }} 69%, 94% {{ opacity: 1; }} 100% {{ opacity: 0; }} }}

    @media (prefers-reduced-motion: reduce) {{
      .c, .fade {{ animation: none; opacity: 1; }}
      .cursor-cmd {{ animation: none; opacity: 0; }}
      .lv    {{ animation: none !important; }}
      .lv.p0 {{ opacity: 1; }}
      .scan  {{ animation: none; }}
    }}
  </style>

  <!-- window -->
  <rect x="1.5" y="1.5" width="837" height="{HEIGHT - 3}" rx="12" fill="{t['surface']}" stroke="{t['border']}" stroke-width="1.5"/>
  <circle cx="28" cy="27" r="7" fill="#ff5f57"/>
  <circle cx="52" cy="27" r="7" fill="#febc2e"/>
  <circle cx="76" cy="27" r="7" fill="#28c840"/>
  <text class="ttl" x="420" y="31.5" text-anchor="middle" fill="{t['muted']}">matej@cachyos: ~</text>
  <line x1="1.5" y1="52" x2="838.5" y2="52" stroke="{t['border']}"/>

  <!-- prompt + typed command -->
{cmd}

  <!-- text-art portrait, generated from the GitHub avatar -->
  <g>
{art_block(grid, t)}
  </g>

  <!-- fetch output -->
  <text class="row fade" x="{INFO_X}" y="142" xml:space="preserve" style="animation-delay:1.45s"><tspan fill="{t['accent']}" font-weight="700">matej</tspan><tspan fill="{t['text']}">@</tspan><tspan fill="{t['accent']}" font-weight="700">cachyos</tspan></text>
  <text class="row fade" x="{INFO_X}" y="162" xml:space="preserve" style="animation-delay:1.50s" fill="{t['rule']}">-------------</text>
{chr(10).join(info)}

  <!-- terminal colour palette -->
  <g>
{swatches}
  </g>

  <!-- fresh prompt -->
  <text class="row fade" x="28" y="542" xml:space="preserve" style="animation-delay:3.1s"><tspan fill="{t['accent']}" font-weight="700">matej@cachyos</tspan><tspan fill="{t['muted']}"> </tspan><tspan fill="{t['blue']}" font-weight="700">~</tspan><tspan fill="{t['muted']}"> $ </tspan><tspan class="cursor" fill="{t['text']}">█</tspan></text>
</svg>
'''


if __name__ == "__main__":
    grid = tonemap()
    path = os.path.join(ROOT, "assets", "terminal.svg")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(build(grid, DARK))
    print("wrote", os.path.relpath(path, ROOT), os.path.getsize(path), "bytes")

    print("\n".join("".join(glyph(v) for v in row).rstrip() for row in grid))
