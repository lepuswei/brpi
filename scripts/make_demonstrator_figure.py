#!/usr/bin/env python
"""Write a manuscript demonstration figure (SVG) for the BRPI research demonstrator."""

from __future__ import annotations

from pathlib import Path

from model_registry.engine import PAPER_EXAMPLE_INPUTS, get_active_model

OUT = Path(__file__).resolve().parent.parent / "doc" / "figures" / "figure_brpi_demonstrator_report.svg"


def _scale(v: float, a0: float, a1: float, b0: float, b1: float) -> float:
    return b0 + (v - a0) / (a1 - a0) * (b1 - b0)


def main() -> None:
    model = get_active_model()
    result = model.predict(PAPER_EXAMPLE_INPUTS, include_paper_uncertainty=True)
    curve = model.frequency_curve(PAPER_EXAMPLE_INPUTS, vary="HF")
    p = float(result.probability)
    hf = float(PAPER_EXAMPLE_INPUTS["HF"])

    # Panel A: horizontal probability bar with zones
    ax, ay, aw, ah = 70, 90, 420, 48
    x_p = _scale(p, 0, 1, ax, ax + aw)
    x_lo = _scale(0.20, 0, 1, ax, ax + aw)
    x_hi = _scale(0.80, 0, 1, ax, ax + aw)

    # Panel B: frequency curve
    bx, by, bw, bh = 70, 260, 420, 200
    pts = []
    for pt in curve:
        px = _scale(pt["x"], 0, 7, bx, bx + bw)
        py = _scale(pt["y"], 0, 1, by + bh, by)
        pts.append(f"{px:.1f},{py:.1f}")
    polyline = " ".join(pts)
    mx = _scale(hf, 0, 7, bx, bx + bw)
    my = _scale(p, 0, 1, by + bh, by)

    # zone bands behind curve
    y0 = by + bh
    y02 = _scale(0.20, 0, 1, by + bh, by)
    y08 = _scale(0.80, 0, 1, by + bh, by)

    tick_x = "".join(
        f'<line x1="{_scale(i,0,7,bx,bx+bw):.1f}" y1="{by+bh}" x2="{_scale(i,0,7,bx,bx+bw):.1f}" y2="{by+bh+6}" stroke="#1c2a24"/>'
        f'<text x="{_scale(i,0,7,bx,bx+bw):.1f}" y="{by+bh+20}" text-anchor="middle" font-size="11" fill="#1c2a24">{i}</text>'
        for i in range(0, 8)
    )
    tick_y = "".join(
        f'<line x1="{bx-6}" y1="{_scale(v,0,1,by+bh,by):.1f}" x2="{bx}" y2="{_scale(v,0,1,by+bh,by):.1f}" stroke="#1c2a24"/>'
        f'<text x="{bx-10}" y="{_scale(v,0,1,by+bh,by)+4:.1f}" text-anchor="end" font-size="11" fill="#1c2a24">{v:.1f}</text>'
        for v in (0.0, 0.2, 0.4, 0.6, 0.8, 1.0)
    )

    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="560" height="520" viewBox="0 0 560 520" role="img"
     aria-label="BRPI research demonstrator paper-example output">
  <rect width="560" height="520" fill="#ffffff"/>
  <text x="28" y="36" font-family="Georgia, Times New Roman, serif" font-size="16" fill="#1c2a24">
    Figure. BRPI research demonstrator — illustrative paper-example output
  </text>
  <text x="28" y="56" font-family="Arial, Helvetica, sans-serif" font-size="11" fill="#5a6b63">
    Research prototype — not clinically validated. HF=5, HI=6, RF=4, RI=5, N=2, P=1, S=1, E=1.
  </text>

  <!-- Panel A -->
  <text x="28" y="82" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="700" fill="#1c2a24">
    A. Illustrative probability and demonstration zones
  </text>
  <rect x="{ax}" y="{ay}" width="{x_lo-ax:.1f}" height="{ah}" fill="#d9efe6"/>
  <rect x="{x_lo:.1f}" y="{ay}" width="{x_hi-x_lo:.1f}" height="{ah}" fill="#f3efd7"/>
  <rect x="{x_hi:.1f}" y="{ay}" width="{ax+aw-x_hi:.1f}" height="{ah}" fill="#f2d6d0"/>
  <rect x="{ax}" y="{ay}" width="{aw}" height="{ah}" fill="none" stroke="#1c2a24" stroke-width="1.2"/>
  <line x1="{x_p:.1f}" y1="{ay-8}" x2="{x_p:.1f}" y2="{ay+ah+8}" stroke="#0f6a5a" stroke-width="3"/>
  <circle cx="{x_p:.1f}" cy="{ay+ah/2}" r="6" fill="#0f6a5a"/>
  <text x="{x_p:.1f}" y="{ay-14}" text-anchor="middle" font-family="Arial, Helvetica, sans-serif"
        font-size="12" font-weight="700" fill="#0f6a5a">P = {p:.2f}</text>
  <text x="{_scale(0.10,0,1,ax,ax+aw):.1f}" y="{ay+ah+22}" text-anchor="middle" font-size="10" fill="#5a6b63"
        font-family="Arial, Helvetica, sans-serif">Low</text>
  <text x="{_scale(0.50,0,1,ax,ax+aw):.1f}" y="{ay+ah+22}" text-anchor="middle" font-size="10" fill="#5a6b63"
        font-family="Arial, Helvetica, sans-serif">Indeterminate</text>
  <text x="{_scale(0.90,0,1,ax,ax+aw):.1f}" y="{ay+ah+22}" text-anchor="middle" font-size="10" fill="#5a6b63"
        font-family="Arial, Helvetica, sans-serif">High</text>
  <text x="{ax}" y="{ay+ah+40}" font-family="Arial, Helvetica, sans-serif" font-size="11" fill="#1c2a24">
    Zone: high-probability demonstration zone · η = {float(result.eta):.2f}
  </text>
  <text x="{ax}" y="{ay+ah+56}" font-family="Arial, Helvetica, sans-serif" font-size="10" fill="#5a6b63">
    Prewritten manuscript illustration interval 0.74–0.94 (not a calculated CI).
  </text>

  <!-- Panel B -->
  <text x="28" y="240" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="700" fill="#1c2a24">
    B. Patient-specific heartburn-frequency curve (other inputs held fixed)
  </text>
  <rect x="{bx}" y="{y08:.1f}" width="{bw}" height="{y0-y08:.1f}" fill="#f2d6d0" opacity="0.45"/>
  <rect x="{bx}" y="{y02:.1f}" width="{bw}" height="{y08-y02:.1f}" fill="#f3efd7" opacity="0.45"/>
  <rect x="{bx}" y="{by}" width="{bw}" height="{y02-by:.1f}" fill="#d9efe6" opacity="0.45"/>
  <rect x="{bx}" y="{by}" width="{bw}" height="{bh}" fill="none" stroke="#1c2a24" stroke-width="1.2"/>
  <polyline points="{polyline}" fill="none" stroke="#0f6a5a" stroke-width="2.5"/>
  {"".join(f'<circle cx="{_scale(pt["x"],0,7,bx,bx+bw):.1f}" cy="{_scale(pt["y"],0,1,by+bh,by):.1f}" r="3.2" fill="#0f6a5a"/>' for pt in curve)}
  <circle cx="{mx:.1f}" cy="{my:.1f}" r="7" fill="#7a4b00"/>
  <text x="{mx+10:.1f}" y="{my-10:.1f}" font-family="Arial, Helvetica, sans-serif" font-size="11" fill="#7a4b00">
    Entered HF = {hf:.0f}
  </text>
  {tick_x}
  {tick_y}
  <text x="{bx+bw/2}" y="{by+bh+42}" text-anchor="middle" font-family="Arial, Helvetica, sans-serif"
        font-size="12" fill="#1c2a24">Heartburn days (0–7)</text>
  <text x="24" y="{by+bh/2}" transform="rotate(-90 24,{by+bh/2})" text-anchor="middle"
        font-family="Arial, Helvetica, sans-serif" font-size="12" fill="#1c2a24">Illustrative probability</text>
  <text x="28" y="500" font-family="Arial, Helvetica, sans-serif" font-size="10" fill="#5a6b63">
    Illustrative—not clinically validated. Demonstration zones at 0.20 and 0.80 are not clinical cutoffs.
  </text>
</svg>
'''
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(svg, encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
