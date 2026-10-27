#!/usr/bin/env python3
"""Generate static GitHub-profile stat cards (light + dark SVG variants).

Usage:  python3 scripts/generate_stats.py
Output: img/stats/{stats,top-langs}-{light,dark}.svg

Numbers are plain constants below (snapshot of public repos as of 2026-10-27).
Edit them and re-run to refresh the cards. No network access needed.
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "img" / "stats"
OUT.mkdir(parents=True, exist_ok=True)

# ---- data -----------------------------------------------------------------
HEADLINE = [
    ("Years in telecom", "12+"),
    ("Current role", "Roaming Expert"),
    ("Employer", "Rakuten Mobile Intl"),
    ("Public repos", "5"),
    ("Open-source skills", "1"),
]

# bytes per language across own public projects (Portfolio-Website, lynx,
# Old-Website). The Anonymous tools collection is excluded so it doesn't swamp
# the numbers.
LANG_BYTES = {
    "TypeScript": 355087,
    "HTML": 163333 + 10420,
    "CSS": 11690 + 34947 + 65338,
    "JavaScript": 805 + 4411 + 13516,
    "Shell": 7747,
    "PowerShell": 7518,
}
LANG_COLORS = {
    "TypeScript": "#3178c6",
    "HTML": "#e34c26",
    "CSS": "#9b6bdc",
    "JavaScript": "#f1e05a",
    "Shell": "#89e051",
    "PowerShell": "#5391fe",
}

THEMES = {
    "light": dict(bg="#ffffff", border="#d0d7de", title="#1a7f37", text="#24292f",
                  muted="#57606a", track="#eaeef2", accent="#00a000"),
    "dark": dict(bg="#0d1117", border="#30363d", title="#00cc00", text="#e6edf3",
                 muted="#8b949e", track="#21262d", accent="#00cc00"),
}
FONT = "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif"
W, H = 495, 195


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def frame(t, title, body, desc):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t d">
  <title id="t">{esc(title)}</title>
  <desc id="d">{esc(desc)}</desc>
  <rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="6" fill="{t['bg']}" stroke="{t['border']}"/>
  <text x="25" y="35" font-family="{FONT}" font-size="18" font-weight="600" fill="{t['title']}">{esc(title)}</text>
{body}
</svg>
"""


def stats_card(t):
    rows = []
    y = 70
    for label, value in HEADLINE:
        rows.append(
            f'  <circle cx="30" cy="{y-5}" r="3.5" fill="{t["accent"]}"/>\n'
            f'  <text x="44" y="{y}" font-family="{FONT}" font-size="14" fill="{t["muted"]}">{esc(label)}</text>\n'
            f'  <text x="{W-25}" y="{y}" text-anchor="end" font-family="{FONT}" font-size="14" font-weight="600" fill="{t["text"]}">{esc(value)}</text>'
        )
        y += 25
    desc = "; ".join(f"{a}: {b}" for a, b in HEADLINE)
    return frame(t, "Ahmed's Profile Stats", "\n".join(rows), desc)


def langs_card(t):
    total = sum(LANG_BYTES.values())
    items = sorted(LANG_BYTES.items(), key=lambda kv: kv[1], reverse=True)
    bar_x, bar_w, bar_y, bar_h = 25, W - 50, 55, 10
    # stacked bar
    segs, x = [], bar_x
    for i, (name, b) in enumerate(items):
        w = bar_w * b / total
        segs.append(f'<rect x="{x:.2f}" y="{bar_y}" width="{w:.2f}" height="{bar_h}" fill="{LANG_COLORS[name]}"/>')
        x += w
    bar = (f'  <clipPath id="c"><rect x="{bar_x}" y="{bar_y}" width="{bar_w}" height="{bar_h}" rx="5"/></clipPath>\n'
           f'  <g clip-path="url(#c)">{"".join(segs)}</g>')
    # legend, two columns of three
    legend = []
    for i, (name, b) in enumerate(items):
        col, row = divmod(i, 3)
        lx = 25 + col * 230
        ly = 100 + row * 26
        pct = 100 * b / total
        legend.append(
            f'  <circle cx="{lx+5}" cy="{ly-5}" r="5" fill="{LANG_COLORS[name]}"/>\n'
            f'  <text x="{lx+18}" y="{ly}" font-family="{FONT}" font-size="13" fill="{t["text"]}">{esc(name)}</text>\n'
            f'  <text x="{lx+205}" y="{ly}" text-anchor="end" font-family="{FONT}" font-size="13" fill="{t["muted"]}">{pct:.1f}%</text>'
        )
    desc = "; ".join(f"{n} {100*b/total:.1f}%" for n, b in items)
    return frame(t, "Top Languages", bar + "\n" + "\n".join(legend), desc)


for mode, t in THEMES.items():
    (OUT / f"stats-{mode}.svg").write_text(stats_card(t), encoding="utf-8")
    (OUT / f"top-langs-{mode}.svg").write_text(langs_card(t), encoding="utf-8")
    print("wrote", mode)
