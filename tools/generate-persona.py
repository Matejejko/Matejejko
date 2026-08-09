#!/usr/bin/env python3
"""
Build assets/persona-{dark,light}.svg -- the identity card under "Persona".

Both themes come out of one layout so the pair can never drift apart; only
the palette changes between them.

    python3 tools/generate-persona.py
"""
import os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

W, H = 840, 264

DARK = dict(
    surface="#161b22", inset="#0d1117", border="#30363d", track="#21262d",
    text="#e6edf3", muted="#8b949e", dim="#484f58",
    accent="#3fb950", accent_bg="#0d2417",
)
LIGHT = dict(
    surface="#f6f8fa", inset="#ffffff", border="#d0d7de", track="#e4e8ed",
    text="#1f2328", muted="#57606a", dim="#8c959f",
    accent="#1a7f37", accent_bg="#dafbe1",
)

NAME = "Matej Papaj"
TAGLINE = "DevOps intern @ Deutsche Telekom · Košice, Slovakia"
STATUS = "OPEN TO COLLAB"

STATS = [
    ("2024", "ON GITHUB", "SINCE"),
    ("12+", "PUBLIC", "REPOS"),
    ("50/50", "SCHOOL &", "WORK"),
]

# name, level, share of the bar
LANGS = [
    ("Slovak", "native", 1.00),
    ("English", "C1", 0.78),
    ("Japanese", "N4", 0.38),
    ("German", "A2", 0.20),
]

TILE_X, TILE_W, TILE_GAP = 28, 124, 8
TILE_Y, TILE_H = 126, 86
BAR_X, BAR_W = 566, 176
LANG_X, LEVEL_X = 452, 758
LANG_Y, LANG_STEP = 152, 28


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build(t):
    tiles = []
    for i, (num, l1, l2) in enumerate(STATS):
        x = TILE_X + i * (TILE_W + TILE_GAP)
        cx = x + TILE_W / 2
        tiles.append(f'''    <g class="unit" style="animation-delay:{0.30 + i * 0.10:.2f}s">
      <rect x="{x}" y="{TILE_Y}" width="{TILE_W}" height="{TILE_H}" rx="8" fill="{t['inset']}" stroke="{t['border']}"/>
      <text class="num" x="{cx:.0f}" y="{TILE_Y + 42}" text-anchor="middle" fill="{t['text']}">{esc(num)}</text>
      <text class="cap" x="{cx:.0f}" y="{TILE_Y + 62}" text-anchor="middle" fill="{t['muted']}">{esc(l1)}</text>
      <text class="cap" x="{cx:.0f}" y="{TILE_Y + 75}" text-anchor="middle" fill="{t['muted']}">{esc(l2)}</text>
    </g>''')

    bars = []
    for i, (lang, level, pct) in enumerate(LANGS):
        y = LANG_Y + i * LANG_STEP
        bars.append(f'''    <g class="unit" style="animation-delay:{0.45 + i * 0.10:.2f}s">
      <text class="lang" x="{LANG_X}" y="{y}" fill="{t['text']}">{esc(lang)}</text>
      <rect x="{BAR_X}" y="{y - 9}" width="{BAR_W}" height="8" rx="4" fill="{t['track']}"/>
      <rect class="bar" style="animation-delay:{0.60 + i * 0.10:.2f}s" x="{BAR_X}" y="{y - 9}" width="{BAR_W * pct:.0f}" height="8" rx="4" fill="{t['accent']}"/>
      <text class="lvl" x="{LEVEL_X}" y="{y}" fill="{t['muted']}">{esc(level)}</text>
    </g>''')

    return f'''<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Persona card for Matej Papaj, DevOps intern at Deutsche Telekom in Košice, Slovakia. On GitHub since 2024, 12+ public repos, a 50/50 school and work split. Languages: Slovak native, English C1, Japanese N4, German A2.">
  <style>
    text {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Inter, Roboto, Helvetica, Arial, sans-serif; }}
    .name {{ font-size: 19px; font-weight: 700; }}
    .tag  {{ font-size: 13px; }}
    .sec  {{ font-size: 10px; font-weight: 600; letter-spacing: 2px; }}
    .cap  {{ font-size: 9px;  font-weight: 600; letter-spacing: 1px; }}
    .pill {{ font-size: 10px; font-weight: 700; letter-spacing: 1.5px; }}
    .mono, .num, .lang, .lvl {{ font-family: ui-monospace, 'SF Mono', 'Cascadia Mono', Menlo, Consolas, 'DejaVu Sans Mono', monospace; }}
    .num  {{ font-size: 26px; font-weight: 700; }}
    .lang {{ font-size: 13px; }}
    .lvl  {{ font-size: 12px; }}
    .mono {{ font-size: 15px; font-weight: 700; }}

    .unit {{ opacity: 0; transform: translateY(8px); animation: rise 0.5s ease-out forwards; }}
    .bar  {{ transform-box: fill-box; transform-origin: left center; transform: scaleX(0); animation: grow 0.9s cubic-bezier(.2,.7,.3,1) forwards; }}
    .led  {{ animation: blink 2.4s ease-in-out infinite; }}
    .ring {{ transform-box: fill-box; transform-origin: center; opacity: 0; animation: pulse 3s ease-out 1s infinite; }}
    @keyframes rise  {{ to {{ opacity: 1; transform: translateY(0); }} }}
    @keyframes grow  {{ to {{ transform: scaleX(1); }} }}
    @keyframes blink {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.25; }} }}
    @keyframes pulse {{
      0%   {{ transform: scale(0.6); opacity: 0.7; }}
      70%  {{ transform: scale(2.4); opacity: 0; }}
      100% {{ transform: scale(2.4); opacity: 0; }}
    }}
    @media (prefers-reduced-motion: reduce) {{
      .unit {{ animation: none; opacity: 1; transform: none; }}
      .bar  {{ animation: none; transform: none; }}
      .led  {{ animation: none; }}
      .ring {{ display: none; }}
    }}
  </style>

  <rect x="1.5" y="1.5" width="{W - 3}" height="{H - 3}" rx="12" fill="{t['surface']}" stroke="{t['border']}" stroke-width="1.5"/>

  <!-- header -->
  <g class="unit" style="animation-delay:.05s">
    <rect x="28" y="24" width="48" height="48" rx="10" fill="{t['accent_bg']}" stroke="{t['accent']}" stroke-width="1.5"/>
    <text class="mono" x="52" y="54" text-anchor="middle" fill="{t['accent']}">MP</text>
    <text class="name" x="92" y="46" fill="{t['text']}">{esc(NAME)}</text>
    <text class="tag"  x="92" y="67" fill="{t['muted']}">{esc(TAGLINE)}</text>
  </g>

  <g class="unit" style="animation-delay:.18s">
    <rect x="654" y="35" width="158" height="26" rx="13" fill="{t['accent_bg']}" stroke="{t['accent']}"/>
    <circle class="ring" cx="672" cy="48" r="4" fill="none" stroke="{t['accent']}" stroke-width="1.5"/>
    <circle class="led"  cx="672" cy="48" r="3.5" fill="{t['accent']}"/>
    <text class="pill" x="686" y="52" fill="{t['accent']}">{esc(STATUS)}</text>
  </g>

  <line x1="28" y1="94" x2="812" y2="94" stroke="{t['border']}"/>

  <!-- section labels -->
  <text class="sec" x="28"  y="116" fill="{t['dim']}">AT A GLANCE</text>
  <text class="sec" x="452" y="116" fill="{t['dim']}">LANGUAGES</text>

  <!-- stat tiles -->
  <g>
{chr(10).join(tiles)}
  </g>

  <!-- language proficiency -->
  <g>
{chr(10).join(bars)}
  </g>
</svg>
'''


if __name__ == "__main__":
    for name, theme in (("dark", DARK), ("light", LIGHT)):
        path = os.path.join(ROOT, "assets", f"persona-{name}.svg")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(build(theme))
        print("wrote", os.path.relpath(path, ROOT), os.path.getsize(path), "bytes")
