"""Make the cited static fallback chart for the NASA environment card (Member 4 plan item).

Owner: Member 4 (Environment & Radiation); generated during integration.

If the NASA EDA export ever becomes unavailable, this image is shown instead of an ingested
series, clearly labelled as a static reference image (not ingested data), with its citation.
It is drawn from the committed 300-point sample, so it needs no network and no extra packages:

    python backend/scripts/make_fallback_chart.py
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[2]
SAMPLE = ROOT / "frontend" / "src" / "features" / "environment-context" / "fixtures" / "environment.sample.json"
OUT = ROOT / "data" / "fallback" / "eda-rr1-co2-iss.svg"

W, H = 960, 420
LEFT, RIGHT, TOP, BOTTOM = 70, 20, 70, 90


def when(iso: str) -> datetime:
    return datetime.fromisoformat(iso.replace("Z", "+00:00"))


def build_svg(data: dict) -> str:
    series = data["series"][0]
    pts = [(when(p["timestamp_utc"]), p["value"]) for p in series["points"] if p["value"] is not None]
    t0, t1 = pts[0][0].timestamp(), pts[-1][0].timestamp()
    lo, hi = min(v for _, v in pts), max(v for _, v in pts)
    pad = (hi - lo) * 0.08 or 1
    lo, hi = lo - pad, hi + pad

    def x(t: datetime) -> float:
        return LEFT + (t.timestamp() - t0) / (t1 - t0) * (W - LEFT - RIGHT)

    def y(v: float) -> float:
        return TOP + (hi - v) / (hi - lo) * (H - TOP - BOTTOM)

    path = " ".join(f"{'M' if i == 0 else 'L'}{x(t):.1f},{y(v):.1f}" for i, (t, v) in enumerate(pts))
    ticks_y = [lo + (hi - lo) * k / 4 for k in range(5)]
    ticks_x = [pts[round(k * (len(pts) - 1) / 4)][0] for k in range(5)]
    grid = "".join(
        f'<line x1="{LEFT}" x2="{W - RIGHT}" y1="{y(v):.1f}" y2="{y(v):.1f}" stroke="#d5deea"/>'
        f'<text x="{LEFT - 8}" y="{y(v) + 4:.1f}" text-anchor="end" font-size="12" fill="#5b687a">{v:.0f}</text>'
        for v in ticks_y
    )
    anchors = ["start", "middle", "middle", "middle", "end"]  # keep the end labels inside the image
    xlabels = "".join(
        f'<text x="{x(t):.1f}" y="{H - BOTTOM + 18}" text-anchor="{anchors[i]}" font-size="12" fill="#5b687a">{t:%d %b %Y}</text>'
        for i, t in enumerate(ticks_x)
    )
    title = escape(f"{data['display_title']}: {series['label']} ({series['units']})")
    cite = escape(data["citation"])
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="system-ui, sans-serif" role="img" aria-label="{title}. Static reference image, not ingested data.">
  <rect width="{W}" height="{H}" fill="#ffffff"/>
  <text x="{LEFT}" y="28" font-size="17" font-weight="700" fill="#0e1a2b">{title}</text>
  <text x="{LEFT}" y="50" font-size="13" font-weight="700" fill="#b3261e">STATIC REFERENCE IMAGE: NOT INGESTED DATA. Historical instrument data, not personal exposure or dose.</text>
  {grid}
  <path d="{path}" fill="none" stroke="#2a78d6" stroke-width="1.6"/>
  {xlabels}
  <text x="{LEFT}" y="{H - 44}" font-size="11" fill="#3d4b5e">Mission {escape(data['mission'])}, {escape(data['location'])}. {len(pts)} of {data['row_count']:,} readings shown (evenly downsampled), UTC.</text>
  <text x="{LEFT}" y="{H - 26}" font-size="11" fill="#3d4b5e">{cite}</text>
</svg>
"""


def main() -> None:
    data = json.loads(SAMPLE.read_text(encoding="utf-8"))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(build_svg(data), encoding="utf-8", newline="\n")
    print("Wrote", OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
