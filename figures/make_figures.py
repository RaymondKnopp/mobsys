#!/usr/bin/env python3
"""Figures for the EURECOM MobSys 5G NR lectures.

All figures are drawn from scratch (no 3GPP/ETSI artwork is reproduced);
numerical details follow the cited TS 38.xxx clauses.

Usage:
    python3 make_figures.py              # writes <name>.svg next to this file
    python3 make_figures.py --png DIR    # additionally writes PNG previews to DIR
"""
import argparse
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Ellipse, FancyBboxPatch, Polygon, Rectangle

# --------------------------------------------------------------------------
# Shared style
# --------------------------------------------------------------------------
FS = 11            # base font size
FS_S = 9           # small annotations
plt.rcParams.update({
    "font.size": FS,
    "font.family": "DejaVu Sans",
    "mathtext.fontset": "dejavusans",
    "svg.fonttype": "none",
    "figure.facecolor": "white",
    "savefig.facecolor": "white",
    "axes.facecolor": "white",
})

INK = "#222222"      # text / outlines
GREY = "#8A8A8A"     # neutral
LIGHT = "#EDEDED"    # neutral fill
C = {
    "dl": "#3A76AF",      # downlink (generic)
    "pdcch": "#2F5F8A",   # PDCCH / CORESET
    "pdcch_l": "#BFD4EA",
    "pdsch": "#9CC3E6",   # PDSCH / data
    "pusch": "#6AAB5C",   # PUSCH
    "ul": "#6AAB5C",      # uplink (generic)
    "ul_l": "#CBE5C4",
    "guard": "#D5D5D5",   # guard / unused
    "ssb": "#E8A33D",     # SS/PBCH block
    "pss": "#D35F3A",
    "sss": "#9C6BB0",
    "pbch": "#F5CF7A",
    "dmrs": "#3B3B7A",
    "accent": "#C0392B",  # warnings / highlights
}
BEAMS = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728",
         "#9467bd", "#8c564b", "#e377c2", "#17becf"]

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
PNG_DIR = None


# --------------------------------------------------------------------------
# Drawing helpers (canvas units: 1 unit = 0.1 inch)
# --------------------------------------------------------------------------
def canvas(w, h, y0=0.0):
    fig = plt.figure(figsize=(w, h))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, w * 10)
    ax.set_ylim(y0, y0 + h * 10)
    ax.axis("off")
    return fig, ax


def save(fig, name):
    fig.savefig(os.path.join(OUT_DIR, name + ".svg"),
                bbox_inches="tight", pad_inches=0.08)
    if PNG_DIR:
        fig.savefig(os.path.join(PNG_DIR, name + ".png"), dpi=110,
                    bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)


def box(ax, x, y, w, h, text="", fc="white", ec=INK, lw=1.0, ls="-",
        fs=None, tc=INK, weight="normal", rounded=False, z=2, alpha=1.0,
        hatch=None):
    if rounded:
        p = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.8",
                           fc=fc, ec=ec, lw=lw, ls=ls, zorder=z, alpha=alpha,
                           hatch=hatch)
    else:
        p = Rectangle((x, y), w, h, fc=fc, ec=ec, lw=lw, ls=ls, zorder=z,
                      alpha=alpha, hatch=hatch)
    ax.add_patch(p)
    if text:
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
                fontsize=fs or FS, color=tc, weight=weight, zorder=z + 1,
                linespacing=1.25)
    return p


def arrow(ax, x0, y0, x1, y1, color=INK, lw=1.2, style="-|>", ls="-",
          ms=12, z=4):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0), zorder=z,
                arrowprops=dict(arrowstyle=style, color=color, lw=lw,
                                linestyle=ls, shrinkA=0, shrinkB=0,
                                mutation_scale=ms))


def polyarrow(ax, pts, color=INK, lw=1.2, ms=12):
    """Elbow connector through pts, arrow head at the end."""
    xs, ys = zip(*pts[:-1])
    ax.plot(xs, ys, color=color, lw=lw, zorder=4, solid_capstyle="butt")
    arrow(ax, *pts[-2], *pts[-1], color=color, lw=lw, ms=ms)


def dim(ax, x0, x1, y, text="", fs=None, color=INK, below=False, off=0.5,
        ha="center", tx=None):
    """Horizontal dimension arrow with label."""
    arrow(ax, x0, y, x1, y, style="<|-|>", color=color, lw=1.0, ms=8)
    if text:
        ax.text((x0 + x1) / 2 if tx is None else tx,
                y - off if below else y + off, text, ha=ha,
                va="top" if below else "bottom", fontsize=fs or FS_S,
                color=color)


def vdim(ax, y0, y1, x, text="", fs=None, color=INK, left=False, off=0.6):
    arrow(ax, x, y0, x, y1, style="<|-|>", color=color, lw=1.0, ms=8)
    if text:
        ax.text(x - off if left else x + off, (y0 + y1) / 2, text,
                ha="right" if left else "left", va="center",
                fontsize=fs or FS_S, color=color)


def vline(ax, x, y0, y1, color=GREY, ls="--", lw=0.9, z=1):
    ax.plot([x, x], [y0, y1], color=color, ls=ls, lw=lw, zorder=z)


def zoom(ax, a0, a1, b0, b1, color=GREY):
    """Dashed zoom lines from segment a (x0,x1 at y) to segment b."""
    ax.plot([a0[0], b0[0]], [a0[1], b0[1]], color=color, ls=":", lw=1)
    ax.plot([a1[0], b1[0]], [a1[1], b1[1]], color=color, ls=":", lw=1)


def lighten(col, f=0.55):
    c = np.array(matplotlib.colors.to_rgb(col))
    return tuple(c + (1 - c) * f)


# --------------------------------------------------------------------------
# 1. Frame structure
# --------------------------------------------------------------------------
def frame_structure():
    fig, ax = canvas(10, 5.8)
    L, R = 20.0, 98.0
    W = R - L
    # frame
    yf, hf = 50, 4.5
    ax.text(L - 1, yf + hf / 2, "Frame\n10 ms", ha="right", va="center")
    for i in range(10):
        box(ax, L + i * W / 10, yf, W / 10, hf, f"subframe {i}", fs=FS_S,
            fc=lighten(C["dl"], 0.7) if i == 0 else "white")
    ax.text(R, yf + hf + 0.6, "10 subframes × 1 ms", ha="right", va="bottom",
            fontsize=FS_S, color=GREY)
    # numerologies, each spanning one subframe
    rows = [38.5, 31.5, 24.5, 17.5]
    hr = 5
    zoom(ax, (L, yf), (L + W / 10, yf), (L, rows[0] + hr), (R, rows[0] + hr))
    ax.text(L + 1, rows[0] + hr + 0.5, "1 subframe = 1 ms", ha="left",
            va="bottom", fontsize=FS_S, color=GREY)
    for mu, y in enumerate(rows):
        n = 2 ** mu
        dur = 1 / n
        ax.text(L - 1, y + hr / 2,
                f"μ = {mu}:  Δf = {15 * n} kHz\n{n} slot{'s' if n > 1 else ''}"
                f" × {dur:g} ms", ha="right", va="center", fontsize=FS_S + 0.5)
        for s in range(n):
            if mu == 0:
                t = "slot 0  (1 ms)"
            elif mu == 1:
                t = f"slot {s}  (0.5 ms)"
            elif mu == 2:
                t = f"slot {s} (0.25 ms)"
            else:
                t = f"slot {s}"
            box(ax, L + s * W / n, y, W / n, hr, t, fs=FS_S,
                fc=lighten(C["dl"], 0.85 - 0.12 * mu))
    # one slot = 14 symbols
    ys, hs = 4.5, 5
    zoom(ax, (L, rows[3]), (L + W / 8, rows[3]), (L, ys + hs), (R, ys + hs))
    ax.text(L - 1, ys + hs / 2, "1 slot (any μ)\n14 OFDM symbols", ha="right",
            va="center", fontsize=FS_S + 0.5)
    sw = W / 14
    for k in range(14):
        x = L + k * sw
        box(ax, x, ys, sw, hs, fc="white")
        box(ax, x, ys, sw * 0.12, hs, fc=GREY, ec=INK, lw=0.6)
        ax.text(x + sw * 0.56, ys + hs / 2, str(k), ha="center", va="center",
                fontsize=FS_S)
    ax.text(L, 1.0, "Normal CP: 14 symbols per slot for every μ (grey strip = "
            "cyclic prefix; the first symbol of every 0.5 ms has a slightly\n"
            "longer CP).  Extended CP (12 symbols per slot) exists only for μ = 2.",
            fontsize=FS_S - 0.5, color=GREY, va="center")
    save(fig, "frame_structure")


# --------------------------------------------------------------------------
# 2. Resource grid
# --------------------------------------------------------------------------
def resource_grid():
    fig, ax = canvas(10, 5.4)
    x0, y0 = 13.0, 6.0
    sw, sh = 3.4, 1.15
    nsym, nsc = 14, 36
    x1, y1 = x0 + nsym * sw, y0 + nsc * sh
    # highlighted RB (RB 1)
    box(ax, x0, y0 + 12 * sh, nsym * sw, 12 * sh, fc=C["pdsch"], ec="none",
        z=1)
    for k in range(nsym + 1):
        ax.plot([x0 + k * sw] * 2, [y0, y1], color=GREY, lw=0.5, zorder=2)
    for n in range(nsc + 1):
        thick = n % 12 == 0
        ax.plot([x0, x1], [y0 + n * sh] * 2, color=INK if thick else GREY,
                lw=1.4 if thick else 0.4, zorder=2)
    box(ax, x0, y0 + 12 * sh, nsym * sw, 12 * sh, fc="none", ec=C["dl"],
        lw=2.2, z=3)
    # one RE
    re_sym, re_sc = 9, 30
    box(ax, x0 + re_sym * sw, y0 + re_sc * sh, sw, sh, fc=C["accent"],
        ec=INK, lw=0.8, z=3)
    # labels
    for rb in range(3):
        ax.text(x0 - 0.8, y0 + (rb * 12 + 6) * sh, f"RB {rb}", ha="right",
                va="center", fontsize=FS_S + 1)
    for k in range(nsym):
        ax.text(x0 + (k + 0.5) * sw, y0 - 0.7, str(k), ha="center", va="top",
                fontsize=FS_S)
    ax.text((x0 + x1) / 2, 1.2, "OFDM symbol index (time) →", ha="center",
            va="center")
    arrow(ax, 3.0, y0, 3.0, y1, lw=1.2)
    ax.text(1.6, (y0 + y1) / 2, "subcarrier (frequency)", rotation=90,
            ha="center", va="center")
    dim(ax, x0, x1, y1 + 1.0, "14 OFDM symbols = 1 slot (normal CP)",
        fs=FS_S + 1)
    vdim(ax, y0 + 12 * sh, y0 + 24 * sh, x1 + 1.5,
         "1 RB = 12 subcarriers\n(180 kHz at Δf = 15 kHz,\n"
         " 12·15·2^μ kHz in general)", fs=FS_S + 1)
    ax.annotate("1 Resource Element (RE)\n= 1 subcarrier × 1 OFDM symbol",
                xy=(x0 + (re_sym + 0.5) * sw, y0 + (re_sc + 0.5) * sh),
                xytext=(x1 + 3, y0 + 31.5 * sh), va="center", fontsize=FS_S + 1,
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=1,
                                shrinkA=2, shrinkB=1))
    ax.text(x1 + 1.5, y0 + 3 * sh,
            "In NR a resource block is defined\nin frequency only "
            "(12 consecutive\nsubcarriers); it is shaded here over\n"
            "one slot to show the grid.", fontsize=FS_S, color=GREY,
            va="center")
    save(fig, "resource_grid")


# --------------------------------------------------------------------------
# 3. Channel / transmission bandwidth
# --------------------------------------------------------------------------
def channel_bandwidth():
    fig, ax = canvas(10, 4.6)
    e0, e1 = 6.0, 94.0
    g = 10.0
    nrb = 17
    rbw = (e1 - e0 - 2 * g) / nrb
    yr, hr = 15.0, 6.0
    # guard bands
    for x in (e0, e1 - g):
        box(ax, x, yr, g, hr, "guard\nband", fc=C["guard"], ec=GREY, fs=FS_S)
    active = range(4, 12)
    for i in range(nrb):
        x = e0 + g + i * rbw
        box(ax, x, yr, rbw, hr, fc=C["pdsch"] if i in active else "white",
            ec=INK, lw=0.8)
    ax.text(e0 + g + 1.5 * rbw, yr + hr / 2, "RB", ha="center", va="center",
            fontsize=FS_S, color=GREY)
    # channel edges
    for x, ha in ((e0, "center"), (e1, "center")):
        vline(ax, x, 9.5, 41.5, color=INK, ls="-", lw=1.4)
        ax.text(x, 8.6, "channel\nedge", ha=ha, va="top", fontsize=FS_S)
    vline(ax, e0 + g, yr, 33, color=GREY)
    vline(ax, e1 - g, yr, 33, color=GREY)
    a0 = e0 + g + active[0] * rbw
    a1 = e0 + g + (active[-1] + 1) * rbw
    vline(ax, a0, yr + hr, 26.5, color=GREY)
    vline(ax, a1, yr + hr, 26.5, color=GREY)
    dim(ax, e0, e1, 39.5, "Channel bandwidth  [MHz]", fs=FS)
    dim(ax, e0 + g, e1 - g, 32.5,
        r"Transmission bandwidth configuration  $N_{\mathrm{RB}}$  [RB]", fs=FS)
    dim(ax, a0, a1, 25.5, "Transmission bandwidth (active RBs)  [RB]",
        fs=FS_S + 1)
    # frequency axis
    arrow(ax, e0 - 3, 13.5, e1 + 4, 13.5, lw=1)
    ax.text(e1 + 4.3, 13.5, "f", va="center", style="italic")
    ax.text(50, 3.0,
            "Example (FR1): 100 MHz channel, Δf = 30 kHz → "
            r"$N_{\mathrm{RB}}$ = 273 (98.28 MHz occupied), "
            "minimum guard band 845 kHz per side (TS 38.101-1 Table 5.3.3-1)",
            ha="center", va="center", fontsize=FS_S, color=GREY)
    save(fig, "channel_bandwidth")


# --------------------------------------------------------------------------
# 4. Bandwidth parts
# --------------------------------------------------------------------------
def bwp():
    fig, ax = canvas(10, 5.1)
    pa = 18.0          # Point A
    w1 = 2.4           # CRB width at 30 kHz
    w0 = w1 / 2        # CRB width at 15 kHz
    n1 = 32
    # CRB grids
    rows = {"g0": 5.0, "g1": 12.0}
    hg = 4.0
    for i in range(2 * n1):
        box(ax, pa + i * w0, rows["g0"], w0, hg, fc="white", lw=0.5)
        if i % 8 == 0:
            ax.text(pa + (i + 0.5) * w0, rows["g0"] + hg / 2, str(i),
                    ha="center", va="center", fontsize=7)
    for i in range(n1):
        box(ax, pa + i * w1, rows["g1"], w1, hg, fc="white", lw=0.6)
        if i % 4 == 0:
            ax.text(pa + (i + 0.5) * w1, rows["g1"] + hg / 2, str(i),
                    ha="center", va="center", fontsize=7.5)
    ax.text(pa - 1, rows["g0"] + hg / 2, "CRBs, μ = 0 (15 kHz)", ha="right",
            va="center", fontsize=FS_S + 0.5)
    ax.text(pa - 1, rows["g1"] + hg / 2, "CRBs, μ = 1 (30 kHz)", ha="right",
            va="center", fontsize=FS_S + 0.5)
    # Point A
    vline(ax, pa, 2.5, 47, color=C["accent"], ls="-", lw=1.6, z=5)
    ax.text(pa, 48, "Point A", ha="center", va="bottom", color=C["accent"],
            weight="bold")
    ax.annotate("Point A = centre of subcarrier 0\nof CRB 0 (every numerology)",
                xy=(pa + 0.6, rows["g0"] - 0.2), xytext=(pa + 6, 0.8),
                fontsize=FS_S, va="center",
                arrowprops=dict(arrowstyle="-|>", lw=0.9, color=INK))
    ax.text(pa + n1 * w1, rows["g1"] + hg + 0.4, "… CRB N", ha="right",
            va="bottom", fontsize=FS_S, color=GREY)

    def bar(y, c0, n, w, text, col, h=4.2):
        x = pa + c0 * w
        box(ax, x, y, n * w, h, text, fc=lighten(col, 0.45), ec=col, lw=1.5,
            fs=FS_S + 0.5, rounded=True)
        vline(ax, x, rows["g1"] + hg if w == w1 else rows["g0"] + hg, y)
        vline(ax, x + n * w, rows["g1"] + hg if w == w1 else rows["g0"] + hg, y)
        return x

    # SSB inside initial BWP
    y_ssb, y0, y1, y2 = 19.5, 26.5, 33.5, 40.5
    bar(y0, 6, 24, w1, "Initial BWP (BWP#0), μ = 1, 24 RBs", C["pdcch"])
    xs = pa + 8 * w1 + 0.6
    box(ax, xs, y_ssb, 20 * w1, 4.2, "SSB: 20 RBs (240 subcarriers)",
        fc=C["ssb"], ec=INK, fs=FS_S + 0.5)
    bar(y1, 2, 30, w1, "BWP#1, μ = 1 (30 kHz), 30 RBs", C["pusch"])
    xb2 = bar(y2, 10, 24, w0, "BWP#2, μ = 0\n(15 kHz), 24 RBs", C["sss"],
              h=5.0)
    dim(ax, pa, xb2, y2 + 2.5, "", fs=FS_S)
    ax.text(pa - 1, y2 + 2.5,
            r"$N^{\mathrm{start}}_{\mathrm{BWP}}$ (in CRBs of the BWP's μ)",
            ha="right", va="center", fontsize=FS_S)
    ax.text(97, 49.5,
            "Up to 4 BWPs configured per direction;\n"
            "one DL and one UL BWP active at a time",
            ha="right", va="top", fontsize=FS_S, color=GREY)
    save(fig, "bwp")


# --------------------------------------------------------------------------
# 5. OFDM transmit chain
# --------------------------------------------------------------------------
def ofdm_chain():
    fig, ax = canvas(10, 3.0)
    y, h, w = 12.0, 10.0, 15.0
    xs = [12.0, 30.5, 49.0, 67.5]
    labels = ["Transform\nprecoding\n(M-point DFT)", "Subcarrier\nmapping",
              "IFFT\n(N-point)", "CP\ninsertion"]
    notes = ["M = 12 × allocated RBs", "onto the allocated\nsubcarriers, zeros elsewhere",
             "N ≥ used subcarriers\n(e.g. 4096)", "copy last N_CP samples\nto the front"]
    for i, (x, t, n) in enumerate(zip(xs, labels, notes)):
        opt = i == 0
        box(ax, x, y, w, h, t, fc=LIGHT if opt else lighten(C["dl"], 0.75),
            ls="--" if opt else "-", lw=1.3, rounded=True, fs=FS)
        ax.text(x + w / 2, y - 1.0, n, ha="center", va="top", fontsize=FS_S - 0.5,
                color=GREY)
        if i < 3:
            arrow(ax, x + w, y + h / 2, xs[i + 1], y + h / 2)
    ax.text(1.0, y + h / 2, "modulation\nsymbols", ha="left", va="center",
            fontsize=FS_S + 0.5)
    arrow(ax, 9.3, y + h / 2, xs[0], y + h / 2)
    arrow(ax, xs[-1] + w, y + h / 2, 87.5, y + h / 2)
    ax.text(88, y + h / 2, "to RF\n(DAC,\nup-conversion)", ha="left",
            va="center", fontsize=FS_S + 0.5)
    ax.text(xs[0] + w / 2, y + h + 1.0, "DFT-s-OFDM", ha="center",
            va="bottom", fontsize=FS_S, color=GREY)
    ax.text((xs[1] + xs[3] + w) / 2, y + h + 1.0, "CP-OFDM (DL and UL)",
            ha="center", va="bottom", fontsize=FS_S, color=GREY)
    ax.text(1.0, 1.8, "* transform precoding only in UL (PUSCH), optional "
            "(enabled by transformPrecoder); without it the UL is CP-OFDM "
            "like the DL.", fontsize=FS_S, color=INK, va="center")
    save(fig, "ofdm_chain")


# --------------------------------------------------------------------------
# 6. SS/PBCH block structure
# --------------------------------------------------------------------------
def ssb_structure():
    fig, ax = canvas(10, 5.6)
    x0, cw = 16.0, 10.0
    y0, H = 5.0, 45.0
    sc = H / 240.0

    def Y(k):
        return y0 + k * sc

    def region(sym, k0, k1, kind, text=""):   # k1 inclusive
        fc = {"pss": C["pss"], "sss": C["sss"], "pbch": C["pbch"],
              "zero": "white"}[kind]
        box(ax, x0 + sym * cw, Y(k0), cw, (k1 - k0 + 1) * sc, text, fc=fc,
            ec=INK, lw=0.9, fs=FS_S + 0.5,
            tc="white" if kind in ("pss", "sss") else INK,
            hatch="////" if kind == "zero" else None)

    region(0, 0, 55, "zero")
    region(0, 56, 182, "pss", "PSS\n127 sc\n(56–182)")
    region(0, 183, 239, "zero")
    region(1, 0, 239, "pbch")
    region(2, 0, 47, "pbch")
    region(2, 48, 55, "zero")
    region(2, 56, 182, "sss", "SSS\n127 sc\n(56–182)")
    region(2, 183, 191, "zero")
    region(2, 192, 239, "pbch")
    region(3, 0, 239, "pbch")
    # PBCH DMRS, v = 0
    v = 0
    for sym, ranges in ((1, [(0, 239)]), (2, [(0, 47), (192, 239)]),
                        (3, [(0, 239)])):
        for a, b in ranges:
            for k in range(a + v, b + 1, 4):
                ax.add_patch(Rectangle((x0 + sym * cw, Y(k)), cw, sc,
                                       fc=C["dmrs"], ec="none", zorder=3))
    for sym in (1, 3):
        ax.text(x0 + (sym + 0.5) * cw, Y(120), "PBCH", ha="center",
                va="center", fontsize=FS_S + 1, weight="bold",
                bbox=dict(fc=C["pbch"], ec="none", pad=1.5), zorder=5)
    for k in (24, 216):
        ax.text(x0 + 2.5 * cw, Y(k), "PBCH", ha="center", va="center",
                fontsize=FS_S, weight="bold",
                bbox=dict(fc=C["pbch"], ec="none", pad=1.0), zorder=5)
    # axes
    for s in range(4):
        ax.text(x0 + (s + 0.5) * cw, y0 + H + 0.8, str(s), ha="center",
                va="bottom")
    ax.text(x0 + 2 * cw, y0 + H + 4.2, "OFDM symbol within the SSB",
            ha="center", va="bottom", fontsize=FS_S + 1)
    ticks = [(0, "0"), (48, "48"), (56, "56"), (183, "183"), (192, "192"),
             (240, "239")]
    for k, t in ticks:
        ax.plot([x0 - 0.8, x0], [Y(k)] * 2, color=INK, lw=0.8)
        dy = {48: -0.6, 56: 0.6, 183: -0.6, 192: 0.6}.get(k, 0)
        ax.text(x0 - 1.1, Y(k) + dy, t, ha="right", va="center",
                fontsize=FS_S)
    ax.text(x0 - 9, y0 + H / 2, "subcarrier k within the SSB", rotation=90,
            ha="center", va="center", fontsize=FS_S + 1)
    vdim(ax, y0, y0 + H, x0 + 4 * cw + 1.5,
         "240 subcarriers\n= 20 RBs", fs=FS_S + 0.5)
    # legend
    lx, ly = 70.0, 46.0
    items = [(C["pss"], None, "PSS: m-sequence, 127 subcarriers"),
             (C["sss"], None, "SSS: Gold sequence, 127 subcarriers"),
             (C["pbch"], None, "PBCH data (MIB + timing bits), QPSK"),
             (C["dmrs"], None, "PBCH DMRS: k = 0+v, 4+v, 8+v, …"),
             ("white", "////", "set to zero (unused)")]
    for i, (fc, hatch, t) in enumerate(items):
        yy = ly - i * 5.0
        box(ax, lx, yy, 3.0, 2.4, fc=fc, hatch=hatch, lw=0.8)
        ax.text(lx + 4.0, yy + 1.2, t, va="center", fontsize=FS_S + 0.5)
    ax.text(lx, ly - 25.5,
            r"$v = N_{\mathrm{ID}}^{\mathrm{cell}} \,\mathrm{mod}\, 4$ (drawn for v = 0)"
            "\nPBCH in symbol 2: subcarriers 0–47\nand 192–239 only."
            "\nSSB = 4 symbols × 240 subcarriers\n(TS 38.211 Table 7.4.3.1-1)",
            va="top", fontsize=FS_S + 0.5, color=INK, linespacing=1.5)
    save(fig, "ssb_structure")


# --------------------------------------------------------------------------
# 7. SSB beam sweeping
# --------------------------------------------------------------------------
def ssb_beams():
    fig, ax = canvas(11, 5.6)
    X0, X1 = 4.0, 74.0
    # periodicity strip
    yt, ht = 49.0, 3.0
    per = 20.0
    span = 60.0
    msx = (X1 - X0) / span
    ax.plot([X0, X1], [yt, yt], color=INK, lw=1)
    for t in range(0, 61, 5):
        ax.plot([X0 + t * msx] * 2, [yt - 0.5, yt], color=INK, lw=0.8)
        if t % 10 == 0:
            ax.text(X0 + t * msx, yt - 0.8, f"{t} ms", ha="center", va="top",
                    fontsize=FS_S - 0.5)
    for b in range(3):
        xb = X0 + b * per * msx
        for i in range(8):
            ax.add_patch(Rectangle((xb + i * 5 * msx / 8, yt),
                                   5 * msx / 8, ht, fc=BEAMS[i], ec="none"))
        box(ax, xb, yt, 5 * msx, ht, fc="none", lw=0.8)
    dim(ax, X0, X0 + per * msx, yt + ht + 1.0,
        "ssb-PeriodicityServingCell (e.g. 20 ms)")
    ax.text(X0 + 5 * msx + 1, yt + ht / 2, "SSB burst (one half-frame)",
            va="center", fontsize=FS_S, color=GREY)
    # half-frame, 140 symbols
    yh, hh = 30.0, 6.0
    sx = (X1 - X0) / 140
    zoom(ax, (X0, yt), (X0 + 5 * msx, yt), (X0, yh + hh), (X1, yh + hh))
    first = [2, 8, 16, 22, 30, 36, 44, 50]
    box(ax, X0, yh, X1 - X0, hh, fc="white", lw=1)
    for s in range(10):
        if s:
            vline(ax, X0 + 14 * s * sx, yh, yh + hh, color=INK, ls="-", lw=0.8)
        ax.text(X0 + (14 * s + 7) * sx, yh - 0.6, f"slot {s}", ha="center",
                va="top", fontsize=FS_S)
    for i, f in enumerate(first):
        box(ax, X0 + f * sx, yh, 4 * sx, hh, str(i), fc=BEAMS[i], ec=INK,
            lw=0.6, tc="white", fs=FS_S, weight="bold")
    ax.text(X0 + 0.5, yh + hh + 0.5, "half-frame = 5 ms = 10 slots at 30 kHz",
            ha="left", va="bottom", fontsize=FS_S, color=GREY)
    ax.text(X0 + 98 * sx, yh + hh / 2, "no SSB in slots 4–9", ha="center",
            va="center", fontsize=FS_S, color=GREY)
    # zoom into slot 0 and 1
    yz, hz = 10.0, 6.0
    zx1 = 46.0
    zsx = (zx1 - X0) / 28
    zoom(ax, (X0, yh), (X0 + 28 * sx, yh), (X0, yz + hz), (zx1, yz + hz))
    for k in range(28):
        idx = None
        for i, f in enumerate(first[:4]):
            if f <= k < f + 4:
                idx = i
        box(ax, X0 + k * zsx, yz, zsx, hz,
            fc=BEAMS[idx] if idx is not None else "white", lw=0.5)
        ax.text(X0 + (k + 0.5) * zsx, yz - 0.5, str(k % 14), ha="center",
                va="top", fontsize=7)
    vline(ax, X0 + 14 * zsx, yz - 0.3, yz + hz + 0.3, color=INK, ls="-", lw=1.5)
    for i in range(4):
        ax.text(X0 + (first[i] + 2) * zsx, yz + hz / 2, f"SSB {i}",
                ha="center", va="center", fontsize=FS_S - 0.5, color="white",
                weight="bold")
    ax.text(X0 + 7 * zsx, yz - 3.2, "slot 0", ha="center", fontsize=FS_S)
    ax.text(X0 + 21 * zsx, yz - 3.2, "slot 1", ha="center", fontsize=FS_S)
    ax.text(zx1 + 2, yz + hz / 2 + 1,
            "Case C (30 kHz), L_max = 8:\n"
            "first symbols {2, 8} + 14·n, n = 0…3\n"
            "→ two SSBs per slot in slots 0–3",
            va="center", fontsize=FS_S + 0.5)
    # beam fan
    gx, gy = 84.0, 28.0
    angs = np.linspace(52, -52, 8)
    for i, a in enumerate(angs):
        r = np.deg2rad(a)
        d = np.array([np.cos(r), np.sin(r)])
        c = np.array([gx, gy]) + 11.0 * d
        ax.add_patch(Ellipse(c, 21.0, 4.0, angle=a, fc=lighten(BEAMS[i], 0.25),
                             ec=BEAMS[i], lw=1, alpha=0.85, zorder=2))
        t = np.array([gx, gy]) + 23.6 * d
        ax.text(t[0], t[1], str(i), ha="center", va="center", fontsize=FS_S,
                weight="bold", color=BEAMS[i])
    ax.add_patch(Polygon([[gx - 1.6, gy - 7], [gx + 1.6, gy - 7], [gx, gy]],
                         fc=GREY, ec=INK, zorder=3))
    ax.add_patch(Rectangle((gx - 0.7, gy - 1), 1.4, 2.6, fc=INK, zorder=4))
    ax.text(gx, gy - 8, "gNB", ha="center", va="top", weight="bold")
    ax.text(gx + 10, 1.5, "SSB index i ↔ beam i", ha="center",
            fontsize=FS_S, color=GREY)
    ax.text(X0, 1.5, "The UE measures SS-RSRP per SSB index and answers on the "
            "PRACH occasion associated with its best SSB.", fontsize=FS_S,
            color=GREY)
    save(fig, "ssb_beams")


# --------------------------------------------------------------------------
# 8. CORESET#0 / SSB frequency layout
# --------------------------------------------------------------------------
def coreset0_layout():
    fig, ax = canvas(10, 5.6, y0=-6.0)
    pa, rbw = 8.0, 3.0
    ncrb = 30
    yg, hg = 7.0, 4.0
    for i in range(ncrb):
        box(ax, pa + i * rbw, yg, rbw, hg, str(i), fc="white", lw=0.6, fs=7)
    ax.text(pa + ncrb * rbw + 0.5, yg + hg / 2, "CRB", va="center",
            fontsize=FS_S)
    off_pa, kssb_sc, offset, ncs = 6, 6, 2, 24
    x_crb = pa + off_pa * rbw
    x_ssb = x_crb + kssb_sc * rbw / 12
    x_cs = pa + (off_pa - offset) * rbw
    # highlight CRB containing SSB start
    box(ax, x_crb, yg, rbw, hg, str(off_pa), fc=C["ssb"], lw=1.0, fs=7)
    # SSB
    ys, hs = 20.0, 5.0
    box(ax, x_ssb, ys, 20 * rbw, hs, "SS/PBCH block: 20 RBs (240 subcarriers)",
        fc=C["ssb"], fs=FS_S + 1)
    for i in range(1, 20):
        ax.plot([x_ssb + i * rbw] * 2, [ys, ys + 0.8], color=INK, lw=0.6)
    # CORESET#0
    yc, hc = 32.0, 5.0
    box(ax, x_cs, yc, ncs * rbw, hc,
        r"CORESET#0: $N_{\mathrm{RB}}^{\mathrm{CORESET}}$ RBs (here 24)",
        fc=C["pdcch_l"], ec=C["pdcch"], lw=1.5, fs=FS_S + 1)
    # guides
    vline(ax, pa, 3.5, 45, color=C["accent"], ls="-", lw=1.6, z=5)
    ax.text(pa, 45.5, "Point A", ha="center", va="bottom", color=C["accent"],
            weight="bold")
    vline(ax, x_crb, yg + hg, yc)
    vline(ax, x_ssb, ys, ys + hs + 2)
    vline(ax, x_cs, yg + hg, yc + hc + 3)
    vline(ax, x_cs + ncs * rbw, yc, yc + hc + 3)
    # dimensions
    dim(ax, pa, x_crb, 14.5, "offsetToPointA\n(15 kHz RBs in FR1)",
        fs=FS_S)
    ax.annotate(r"$k_{\mathrm{SSB}}$ (subcarriers)", xy=(x_crb + 0.75, 17.2),
                xytext=(x_crb + 8, 15.0), fontsize=FS_S + 0.5, va="center",
                arrowprops=dict(arrowstyle="-|>", lw=0.9, color=INK))
    dim(ax, x_crb, x_ssb, 17.2, "", fs=FS_S)
    dim(ax, x_cs, x_crb, 30.0, "Offset (RBs)", fs=FS_S, below=True,
        ha="left", tx=x_cs - 0.3)
    dim(ax, x_cs, x_cs + ncs * rbw, 39.5,
        r"$N_{\mathrm{RB}}^{\mathrm{CORESET}}$ RBs, 1–3 symbols at the start of "
        "the PDCCH monitoring occasion", fs=FS_S)
    ax.annotate(r"$N_{\mathrm{CRB}}^{\mathrm{SSB}}$: CRB overlapping the "
                "first SSB subcarrier", xy=(x_crb + rbw / 2, yg),
                xytext=(x_crb + 10, 3.2), fontsize=FS_S, va="center",
                arrowprops=dict(arrowstyle="-|>", lw=0.9, color=INK))
    ax.text(pa, -3.5,
            "Drawn with CRB grid, SSB and CORESET#0 all at 15 kHz.  FR1: "
            r"offsetToPointA and $k_{\mathrm{SSB}}$ (0…23) in 15 kHz units.  "
            "CORESET#0 size, symbols and Offset\nfrom controlResourceSetZero "
            "(MIB) → TS 38.213 Tables 13-1…13-10; Offset counted down from "
            r"$N_{\mathrm{CRB}}^{\mathrm{SSB}}$ in RBs of the CORESET#0 SCS.",
            fontsize=FS_S - 0.5, color=GREY, va="center")
    save(fig, "coreset0_layout")


# --------------------------------------------------------------------------
# 9. Random-access procedure
# --------------------------------------------------------------------------
def ra_procedure():
    fig, ax = canvas(10, 6.8)
    ue, gnb = 16.0, 86.0
    top = 63.0
    box(ax, ue - 6, top, 12, 4.5, "UE", fc=lighten(C["ul"], 0.5),
        weight="bold", rounded=True)
    box(ax, gnb - 6, top, 12, 4.5, "gNB", fc=lighten(C["dl"], 0.5),
        weight="bold", rounded=True)
    vline(ax, ue, 2, top, color=INK, ls="-", lw=1)
    vline(ax, gnb, 2, top, color=INK, ls="-", lw=1)

    def msg(y, frm, title, sub, col, dy=2.0, ls="-"):
        x0, x1 = (ue, gnb) if frm == "ue" else (gnb, ue)
        arrow(ax, x0, y, x1, y - dy, color=col, lw=1.8, ls=ls)
        xm = (ue + gnb) / 2
        ax.text(xm, y + 0.3, title, ha="center", va="bottom", weight="bold",
                fontsize=FS, color=INK)
        if sub:
            ax.text(xm, y - dy - 0.6, sub, ha="center", va="top",
                    fontsize=FS_S, color=INK, linespacing=1.3)

    msg(59.0, "gnb", "SSB burst + SIB1 (RACH-ConfigCommon)", "", GREY, ls="--",
        dy=1.5)
    ax.text(ue - 1, 55.0, "select best SSB\n(SS-RSRP) → preamble\n+ RACH occasion",
            ha="right", va="center", fontsize=FS_S, color=INK)
    msg(52.0, "ue", "Msg1: PRACH preamble",
        "RACH occasion associated with the selected SSB; "
        "RA-RNTI derived from its time/frequency position", C["ul"])
    msg(43.0, "gnb", "Msg2: Random Access Response (RAR)",
        "PDCCH: DCI 1_0 with CRC scrambled by RA-RNTI  +  PDSCH (MAC RAR):\n"
        "RAPID, Timing Advance command, UL grant, TC-RNTI", C["dl"])
    msg(32.0, "ue", "Msg3: PUSCH — RRCSetupRequest",
        "scheduled by the RAR UL grant, sent with the TA applied; "
        "carries the UE identity\n(retransmissions: DCI 0_0 scrambled by TC-RNTI)",
        C["pusch"])
    msg(21.0, "gnb", "Msg4: PDCCH (TC-RNTI) + PDSCH",
        "UE Contention Resolution Identity MAC CE + RRCSetup", C["dl"])
    msg(12.0, "ue", "HARQ-ACK on PUCCH",
        "contention resolved → TC-RNTI becomes the C-RNTI", C["ul"])
    # timers on UE side
    def bracket(y0, y1, x, text):
        ax.plot([x + 1, x, x, x + 1], [y0, y0, y1, y1], color=C["accent"],
                lw=1.3)
        ax.text(x - 0.8, (y0 + y1) / 2, text, ha="right", va="center",
                fontsize=FS_S, color=C["accent"])
    bracket(48.5, 40.5, ue - 2.5, "ra-Response-\nWindow")
    bracket(29.5, 18.5, ue - 2.5, "ra-Contention-\nResolutionTimer")
    ax.text((ue + gnb) / 2, 3.0, "4-step contention-based random access "
            "(TS 38.321 §5.1, TS 38.213 §8)", ha="center", fontsize=FS_S,
            color=GREY)
    save(fig, "ra_procedure")


# --------------------------------------------------------------------------
# 10. PRACH transmitter
# --------------------------------------------------------------------------
def prach_tx():
    fig, ax = canvas(10, 4.7, y0=6.5)
    h = 9.0
    y1, y2 = 40.0, 15.0
    w1 = 27.0
    xs1 = [3.0, 36.5, 70.0]
    b1 = [("Zadoff–Chu root sequence\n"
           r"$x_u(i)=e^{-j\pi u i(i+1)/L_{RA}}$"),
          ("Cyclic shift\n"
           r"$x_{u,v}(n)=x_u((n+C_v) \,\mathrm{mod}\, L_{RA})$"),
          ("DFT (L_RA points)\n"
           r"$y_{u,v}(k)=\sum_n x_{u,v}(n)\,e^{-j2\pi kn/L_{RA}}$")]
    n1 = ["u from prach-RootSequenceIndex\n(logical → physical root, "
          "TS 38.211\nTables 6.3.3.1-3/-4); L_RA = 839 or 139",
          r"$C_v = v\,N_{CS}$ (unrestricted set);"
          "\nv from preamble index 0…63,\n"
          r"$N_{CS}$ from zeroCorrelationZoneConfig",
          "sequence → PRACH subcarriers\n(long: 1.25 / 5 kHz, "
          "short: 15·2^μ kHz)"]
    for i, x in enumerate(xs1):
        box(ax, x, y1, w1, h, b1[i], fc=lighten(C["ul"], 0.6), rounded=True,
            fs=FS_S + 0.5)
        ax.text(x + w1 / 2, y1 - 0.8, n1[i], ha="center", va="top",
                fontsize=FS_S - 0.5, color=GREY, linespacing=1.3)
        if i < 2:
            arrow(ax, x + w1, y1 + h / 2, xs1[i + 1], y1 + h / 2)
    w2 = 19.0
    xs2 = [3.0, 27.0, 51.0, 75.0]
    b2 = ["Subcarrier\nmapping", "IDFT\n(OFDM)", "CP + sequence\nrepetition",
          "to RF"]
    n2 = ["msg1-FrequencyStart (offset\nfrom BWP start), msg1-FDM\n"
          "(1, 2, 4 or 8 ROs in freq.)",
          "one long OFDM symbol\nper sequence repetition",
          "preamble format (0–3,\nA1…C2) sets N_CP and\nnumber of repetitions",
          "power from\nramping procedure"]
    for i, x in enumerate(xs2):
        box(ax, x, y2, w2, h, b2[i],
            fc=LIGHT if i == 3 else lighten(C["ul"], 0.6), rounded=True,
            fs=FS_S + 1)
        ax.text(x + w2 / 2, y2 - 0.8, n2[i], ha="center", va="top",
                fontsize=FS_S - 0.5, color=GREY, linespacing=1.3)
        if i < 3:
            arrow(ax, x + w2, y2 + h / 2, xs2[i + 1], y2 + h / 2)
    polyarrow(ax, [(xs1[2] + w1 / 2 + 6, y1), (xs1[2] + w1 / 2 + 6, 28.0),
                   (xs2[0] + w2 / 2, 28.0), (xs2[0] + w2 / 2, y2 + h)])
    ax.text(3.0, 52.0, "64 preambles per RACH occasion: increasing cyclic shift "
            "of a root first, then the next logical root index",
            fontsize=FS_S, color=INK)
    save(fig, "prach_tx")


# --------------------------------------------------------------------------
# 11. PRACH receiver
# --------------------------------------------------------------------------
def prach_rx():
    fig = plt.figure(figsize=(10, 5.8))
    ax = fig.add_axes([0, 0.63, 1, 0.35])
    ax.set_xlim(0, 100)
    ax.set_ylim(7, 27.3)
    ax.axis("off")
    labels = ["Remove\nCP", "DFT", "Extract\nPRACH\nsubcarriers",
              "× conj(Y_u(k))\n(root u in\nfreq. domain)", "IDFT\n(L_RA)",
              "|·|²: power\ndelay profile\n(+ combine)", "Peak\ndetection"]
    w, g = 12.2, 2.2
    y, h = 9.5, 11.0
    for i, t in enumerate(labels):
        x = 1.0 + i * (w + g)
        box(ax, x, y, w, h, t, fc=LIGHT if i == 6 else lighten(C["dl"], 0.75),
            rounded=True, fs=FS_S)
        if i < 6:
            arrow(ax, x + w, y + h / 2, x + w + g, y + h / 2, ms=9)
    ax.text(50, y + h + 1.0, "gNB PRACH receiver — one correlator per "
            "configured root sequence u", ha="center", va="bottom",
            fontsize=FS, weight="bold")
    ax.text(50, y - 1.2, "multiplying by the conjugate root in the frequency "
            "domain = circular correlation with the root sequence; "
            "antennas / repetitions are combined non-coherently on |·|²",
            ha="center", va="top", fontsize=FS_S - 0.5, color=GREY)

    # numerical power delay profile (L_RA = 139, N_CS = 23)
    L, ncs, u = 139, 23, 25
    n = np.arange(L)
    xu = np.exp(-1j * np.pi * u * n * (n + 1) / L)
    rng = np.random.default_rng(3)
    ues = [(0, 4, 1.0), (2, 11, 0.6)]          # (preamble v, delay, amplitude)
    r = np.zeros(L, complex)
    for v, d, a in ues:
        r += a * np.roll(np.roll(xu, -v * ncs), d)
    r += 0.25 * (rng.standard_normal(L) + 1j * rng.standard_normal(L))
    c = np.fft.ifft(np.fft.fft(r) * np.conj(np.fft.fft(xu)))
    pdp = np.abs(c) ** 2
    pdp /= pdp.max()
    bx = fig.add_axes([0.07, 0.11, 0.9, 0.5])
    nwin = L // ncs
    for v in range(nwin):
        s = (-v * ncs) % L
        bx.axvspan(s - 0.5, s + ncs - 0.5,
                   color=lighten(BEAMS[v], 0.75), zorder=0)
        bx.text(s + ncs / 2 - 0.5, 1.12, f"preamble {v}", ha="center",
                va="bottom", fontsize=FS_S, color=BEAMS[v])
    bx.vlines(n, 0, pdp, color=INK, lw=1.1)
    thr = 0.35
    bx.axhline(thr, color=C["accent"], ls="--", lw=1)
    bx.text(25, thr + 0.02, "detection threshold", ha="left", va="bottom",
            fontsize=FS_S, color=C["accent"])
    for v, d, a in ues:
        p = (d - v * ncs) % L
        s = (-v * ncs) % L
        bx.annotate("", xy=(p, pdp[p] + 0.03), xytext=(s - 0.5, pdp[p] + 0.03),
                    arrowprops=dict(arrowstyle="<|-|>", lw=0.9, color=INK,
                                    mutation_scale=8))
        bx.text(p + 1.5, min(pdp[p] + 0.1, 0.8), f"preamble {v} detected\n"
                f"offset in window = {d} → TA", fontsize=FS_S, va="center")
    bx.set_xlim(-1, L)
    bx.set_ylim(0, 1.3)
    bx.set_yticks([0, 0.5, 1])
    bx.set_xlabel(r"correlation lag (IDFT output index, $L_{RA}$ = 139, "
                  r"$N_{CS}$ = 23)", fontsize=FS_S + 1)
    bx.set_ylabel("normalised power", fontsize=FS_S + 1)
    bx.tick_params(labelsize=FS_S)
    for s in ("top", "right"):
        bx.spines[s].set_visible(False)
    fig.text(0.07, 0.005, r"Window of preamble v starts at lag $(-C_v) \,\mathrm{mod}\, "
             r"L_{RA}$: window index → preamble ID, peak position inside the "
             "window → round-trip delay → TA command.",
             fontsize=FS_S, color=GREY)
    save(fig, "prach_rx")


# --------------------------------------------------------------------------
# 12. Timing advance
# --------------------------------------------------------------------------
def timing_advance():
    fig, ax = canvas(10, 7.6)
    # ---- (a) frame timing
    ax.text(1, 74, "(a) Uplink frame i is sent T_TA before downlink frame i "
            "as received by the UE", fontsize=FS, weight="bold", va="center")
    rows = [("gNB DL TX", 64.0, "dl", 35.0),
            ("UE DL RX", 55.5, "dl", 40.0),
            ("UE UL TX", 47.0, "ul", 26.0),
            ("gNB UL RX", 38.5, "ul", 31.0)]
    h, fw = 4.5, 50.0
    for name, y, k, s in rows:
        ax.text(17, y + h / 2, name, ha="right", va="center", fontsize=FS_S + 1)
        col = C["dl"] if k == "dl" else C["ul"]
        box(ax, 18, y, s - 18, h, fc=LIGHT, ec=GREY, lw=0.6)
        box(ax, s, y, fw, h, f"{'DL' if k == 'dl' else 'UL'} frame i",
            fc=lighten(col, 0.55), ec=INK, fs=FS_S + 0.5)
        box(ax, s + fw, y, 98 - s - fw, h, fc=LIGHT, ec=GREY, lw=0.6)
    vline(ax, 35, 36.5, 70, color=C["dl"])
    vline(ax, 40, 46, 61.5, color=C["dl"])
    dim(ax, 35, 40, 62.0, "", fs=FS_S)
    ax.text(41, 62.0, r"$T_p$ (propagation)", fontsize=FS_S, va="center")
    dim(ax, 26, 40, 45.4, "", fs=FS_S)
    ax.text(41, 45.4, r"$T_{TA} = (N_{TA} + N_{TA,offset})\,T_c$  "
            r"$\approx 2T_p + N_{TA,offset}T_c$", fontsize=FS_S + 0.5,
            va="center")
    dim(ax, 31, 35, 36.9, "", fs=FS_S)
    ax.text(36, 36.9, r"$N_{TA,offset}\,T_c$ (TX/RX switching margin, "
            r"e.g. 25600 $T_c$ ≈ 13 µs in FR1 TDD)", fontsize=FS_S,
            va="center")
    ax.text(98, 32.6, r"$T_c$ = 1/(480 kHz · 4096) ≈ 0.509 ns;  RAR TA "
            r"command $T_A$ = 0…3846 → $N_{TA} = T_A \cdot 16 \cdot 64 / 2^{\mu}$",
            ha="right", fontsize=FS_S, color=GREY, va="center")
    # ---- (b) CP and multi-UE alignment
    ax.text(1, 28.0, "(b) Several UEs received at the gNB in one FFT window",
            fontsize=FS, weight="bold", va="center")
    cp, tu = 3.0, 16.0
    T = cp + tu
    x0 = 22.0
    ues = [("UE 1", 0.0), ("UE 2", 1.2), ("UE 3", 2.4), ("UE 4", 4.8)]
    hb = 3.4
    ys = [19.5, 14.5, 9.5, 4.5]
    w0, w1 = x0 + T + cp, x0 + T + cp + tu
    for (name, d), y in zip(ues, ys):
        late = d > cp
        col = C["accent"] if late else C["ul"]
        ax.text(x0 - 3, y + hb / 2, name, ha="right", va="center",
                fontsize=FS_S + 1)
        for j, lab in enumerate(["k−1", "k", "k+1"]):
            xs = x0 + d + j * T
            box(ax, xs, y, cp, hb, fc=GREY, ec=INK, lw=0.6)
            box(ax, xs + cp, y, tu, hb, lab,
                fc=lighten(col, 0.35 if j == 1 else 0.7), ec=INK, lw=0.6,
                fs=FS_S)
        if late:
            ov = x0 + d + T - w0
            box(ax, w0, y - 0.4, ov, hb + 0.8, fc="none", ec=C["accent"],
                lw=1.8, z=6)
            ax.text(85.5, y + hb / 2, "delay > CP:\nISI from symbol k−1",
                    ha="left", va="center",
                    fontsize=FS_S, color=C["accent"])
        else:
            ax.text(85.5, y + hb / 2,
                    "aligned" if d == 0 else "delay < CP:\nphase ramp only",
                    ha="left", va="center", fontsize=FS_S, color=INK)
    box(ax, w0, 3.4, tu, 21.5, fc="none", ec=C["dl"], lw=1.6, ls="--", z=7)
    ax.text((w0 + w1) / 2, 25.3, "gNB FFT window, symbol k", ha="center",
            va="bottom", fontsize=FS_S, color=C["dl"])
    dim(ax, x0 + T, x0 + T + cp, 23.6, "CP", fs=FS_S)
    ax.text(1, 1.0, "Within the FFT window each in-time UE contributes one "
            "cyclically shifted copy of a single symbol → subcarriers stay "
            "orthogonal.", fontsize=FS_S, color=GREY, va="center")
    save(fig, "timing_advance")


# --------------------------------------------------------------------------
# 13. UL-SCH processing chain
# --------------------------------------------------------------------------
def ulsch_chain():
    fig, ax = canvas(10, 6.2)
    w, g, h = 14.0, 2.4, 9.0
    y1, y2 = 34.0, 11.0
    xs = [2.0 + i * (w + g) for i in range(6)]
    r1 = ["TB CRC\nattachment\n(24 bit; 16 if\nTBS ≤ 3824)",
          "LDPC base\ngraph selection,\nCB segmentation\n+ CB CRC (24 bit)",
          "LDPC\nencoding\n(BG1 / BG2)",
          "Rate matching\n(circular buffer,\nredundancy\nversion rv 0…3)",
          "Code block\nconcatenation",
          "Data & control\nmultiplexing"]
    for i, t in enumerate(r1):
        box(ax, xs[i], y1, w, h, t, fc=lighten(C["pusch"], 0.6), rounded=True,
            fs=FS_S - 0.5)
        if i < 5:
            arrow(ax, xs[i] + w, y1 + h / 2, xs[i + 1], y1 + h / 2, ms=9)
    # UCI inputs
    uci = ["HARQ-ACK", "CSI part 1", "CSI part 2"]
    ux = [50.0, 66.4, 82.8]
    for x, t in zip(ux, uci):
        box(ax, x, 50.0, w, 5.5, t + "\n(coded)", fc=lighten(C["dl"], 0.7),
            rounded=True, fs=FS_S - 0.5)
        ax.plot([x + w / 2, x + w / 2], [50.0, 47.0], color=INK, lw=1.1)
    ax.plot([ux[0] + w / 2, ux[2] + w / 2], [47.0, 47.0], color=INK, lw=1.1)
    arrow(ax, xs[5] + w / 2, 47.0, xs[5] + w / 2, y1 + h)
    ax.text(48.5, 52.75, "UCI, each part encoded and\nrate-matched separately "
            "(§6.3.2)", ha="right", va="center", fontsize=FS_S - 0.5)
    ax.text(xs[0] + w / 2, 52.75, "transport block\nfrom MAC", ha="center",
            va="center", fontsize=FS_S)
    arrow(ax, xs[0] + w / 2, 50.3, xs[0] + w / 2, y1 + h)
    ax.text(2.0, 30.5, "Channel coding — TS 38.212 §6.2 (UL-SCH)",
            fontsize=FS_S, color=GREY, va="center", style="italic")
    # row 2
    r2 = ["Scrambling", "Modulation\n(π/2-BPSK …\n256QAM)", "Layer\nmapping",
          "Transform\nprecoding\n(optional)", "Precoding",
          "Mapping to\nVRB → PRB\n(+ DMRS)"]
    for i, t in enumerate(r2):
        opt = i == 3
        box(ax, xs[i], y2, w, h, t,
            fc=LIGHT if opt else lighten(C["pusch"], 0.35),
            ls="--" if opt else "-", rounded=True, fs=FS_S - 0.5)
        if i < 5:
            arrow(ax, xs[i] + w, y2 + h / 2, xs[i + 1], y2 + h / 2, ms=9)
    polyarrow(ax, [(xs[5] + w / 2, y1), (xs[5] + w / 2, 27.0),
                   (xs[0] + w / 2, 27.0), (xs[0] + w / 2, y2 + h)])
    ax.text(2.0, 7.5, "Physical channel — TS 38.211 §6.3.1 (PUSCH)",
            fontsize=FS_S, color=GREY, va="center", style="italic")
    arrow(ax, xs[5] + w / 2, y2, xs[5] + w / 2, 6.0)
    ax.text(xs[5] + w / 2, 5.4, "OFDM signal\ngeneration", ha="center",
            va="top", fontsize=FS_S)
    save(fig, "ulsch_chain")


# --------------------------------------------------------------------------
# 14. PRACH power ramping
# --------------------------------------------------------------------------
def power_ramping():
    fig, bx = plt.subplots(figsize=(10, 4.8))
    fig.subplots_adjust(left=0.1, right=0.98, top=0.78, bottom=0.12)
    p0, step, n = -104, 2, 4
    win = 6.0
    for k in range(1, n + 1):
        t = (k - 1) * 10.0
        pw = p0 + (k - 1) * step
        bx.bar(t, pw - (-112), bottom=-112, width=1.2, align="edge",
               color=C["ul"], ec=INK, lw=0.8, zorder=3)
        bx.text(t + 0.6, pw + 0.3, f"{pw} dBm", ha="center", va="bottom",
                fontsize=FS_S)
        bx.axvspan(t + 1.8, t + 1.8 + win, ymin=0, ymax=0.12,
                   color=LIGHT, zorder=1)
        bx.text(t + 1.8 + win / 2, -111.3,
                "ra-Response-\nWindow" if k == 1 else "window",
                ha="center", va="bottom", fontsize=FS_S - 1)
        if k < n:
            bx.text(t + 1.8 + win / 2, -108.0, "no RAR", ha="center",
                    fontsize=FS_S, color=C["accent"])
        else:
            bx.annotate("RAR received\n(Msg2)", xy=(t + 4.8, -110.0),
                        xytext=(t + 4.8, -106.5), ha="center", fontsize=FS_S,
                        color=C["dl"], arrowprops=dict(arrowstyle="-|>",
                                                       color=C["dl"]))
    bx.axhline(p0, color=GREY, ls="--", lw=1, zorder=2)
    bx.text(1.5, p0 - 0.2, "preambleReceivedTargetPower", ha="left",
            va="top", fontsize=FS_S - 1, color=GREY)
    bx.annotate("", xy=(11.8, p0 + step), xytext=(11.8, p0),
                arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=1,
                                mutation_scale=8))
    bx.text(12.3, p0 + step / 2, "powerRampingStep", va="center",
            fontsize=FS_S)
    bx.set_xticks([(k - 1) * 10 + 0.6 for k in range(1, n + 1)])
    bx.set_xticklabels([f"attempt {k}" for k in range(1, n)] +
                       [f"attempt {n}\n(≤ preambleTransMax)"], fontsize=FS_S)
    bx.set_xlim(-2, 40)
    bx.set_ylim(-112, -96)
    bx.set_ylabel("target received power [dBm]", fontsize=FS_S + 1)
    bx.set_xlabel("time", fontsize=FS_S + 1)
    bx.tick_params(labelsize=FS_S)
    for s in ("top", "right"):
        bx.spines[s].set_visible(False)
    fig.text(0.1, 0.955,
             "PREAMBLE_RECEIVED_TARGET_POWER = preambleReceivedTargetPower + "
             "DELTA_PREAMBLE\n        + (PREAMBLE_POWER_RAMPING_COUNTER − 1) "
             "× PREAMBLE_POWER_RAMPING_STEP      (TS 38.321 §5.1.3)",
             fontsize=FS_S, va="top", family="DejaVu Sans Mono")
    fig.text(0.1, 0.845,
             r"$P_{PRACH} = \min(P_{CMAX},\ $PREAMBLE_RECEIVED_TARGET_POWER"
             r"$\ +\ PL)$ (TS 38.213 §7.4).  Example: −104 dBm, step 2 dB, "
             "DELTA_PREAMBLE = 0 dB (format 0).\nNo RAR after "
             "preambleTransMax attempts → random-access problem indicated "
             "to upper layers.",
             fontsize=FS_S - 0.5, va="top", color=GREY)
    save(fig, "power_ramping")


# --------------------------------------------------------------------------
# 15. TDD pattern
# --------------------------------------------------------------------------
def tdd_pattern():
    fig, ax = canvas(10, 4.8)
    X0, sw = 6.0, 8.8
    yt, ht = 33.0, 6.0
    pat = "DDDSU" * 2
    ndl, ng, nul = 10, 2, 2
    for i, s in enumerate(pat):
        x = X0 + i * sw
        if s == "D":
            box(ax, x, yt, sw, ht, "D", fc=lighten(C["dl"], 0.35), tc="white",
                weight="bold")
        elif s == "U":
            box(ax, x, yt, sw, ht, "U", fc=C["ul"], tc="white", weight="bold")
        else:
            u = sw / 14
            box(ax, x, yt, ndl * u, ht, fc=lighten(C["dl"], 0.35), lw=0.6)
            box(ax, x + ndl * u, yt, ng * u, ht, fc=C["guard"], lw=0.6)
            box(ax, x + (ndl + ng) * u, yt, nul * u, ht, fc=C["ul"], lw=0.6)
            box(ax, x, yt, sw, ht, "S", fc="none", lw=1.2, weight="bold")
        ax.text(x + sw / 2, yt - 0.5, "0.5 ms", ha="center", va="top",
                fontsize=FS_S - 1, color=GREY)
    dim(ax, X0, X0 + 5 * sw, yt + ht + 1.2,
        "dl-UL-TransmissionPeriodicity = 2.5 ms (ms2p5)", fs=FS_S + 0.5)
    ax.text(X0 + 7.5 * sw, yt + ht + 1.7, "pattern repeats",
            ha="center", va="bottom", fontsize=FS_S, color=GREY)
    dim(ax, X0, X0 + 3 * sw, yt - 4.0, "nrofDownlinkSlots = 3", below=True)
    dim(ax, X0 + 4 * sw, X0 + 5 * sw, yt - 4.0, "nrofUplinkSlots = 1",
        below=True, ha="left", tx=X0 + 4 * sw - 2)
    # zoom into S
    yz, hz = 11.0, 6.0
    Z0, Z1 = 6.0, 96.0
    zw = (Z1 - Z0) / 14
    xs = X0 + 3 * sw
    zoom(ax, (xs, yt - 2.4), (xs + sw, yt - 2.4), (Z0, yz + hz), (Z1, yz + hz))
    for k in range(14):
        if k < ndl:
            fc, tc = lighten(C["dl"], 0.35), "white"
        elif k < ndl + ng:
            fc, tc = C["guard"], INK
        else:
            fc, tc = C["ul"], "white"
        box(ax, Z0 + k * zw, yz, zw, hz, str(k), fc=fc, tc=tc, fs=FS_S)
    dim(ax, Z0, Z0 + ndl * zw, yz - 1.5, "nrofDownlinkSymbols = 10", below=True)
    dim(ax, Z0 + ndl * zw, Z0 + (ndl + ng) * zw, yz + hz + 1.5,
        "guard /\nflexible = 2", fs=FS_S)
    dim(ax, Z0 + (ndl + ng) * zw, Z1, yz - 1.5, "nrofUplinkSymbols = 2",
        below=True, ha="right", tx=Z1)
    ax.text(Z0, yz + hz + 1.0, "special (mixed) slot: 14 OFDM symbols",
            fontsize=FS_S + 0.5, va="bottom")
    ax.text(Z0, 46.0, "TDD-UL-DL-ConfigCommon, referenceSubcarrierSpacing = "
            "30 kHz:  D D D S U", fontsize=FS, va="center", weight="bold")
    ax.text(Z0, 2.0, "DL symbols start the slot after the DL slots, UL symbols "
            "end the slot before the UL slots; the gap absorbs DL→UL switching "
            "and round-trip delay.", fontsize=FS_S - 0.5, color=GREY,
            va="center")
    save(fig, "tdd_pattern")


# --------------------------------------------------------------------------
# 16. Link adaptation loop
# --------------------------------------------------------------------------
def amc_loop():
    fig, ax = canvas(10, 5.6)
    # groups
    box(ax, 1.5, 3, 31, 49, fc="none", ec=C["dl"], ls="--", lw=1.2, z=1)
    ax.text(3, 50.5, "gNB", color=C["dl"], weight="bold", va="top")
    box(ax, 67.5, 3, 31, 49, fc="none", ec=C["ul"], ls="--", lw=1.2, z=1)
    ax.text(69, 50.5, "UE", color=C["ul"], weight="bold", va="top")
    A = (4, 8, 26, 13)    # scheduler
    B = (4, 31, 26, 11)   # PHY TX
    CH = (37, 31, 26, 11)
    U = (70, 29, 26, 15)
    E = (70, 8, 26, 11)
    F = (37, 8, 26, 11)
    box(ax, *A, "MAC scheduler + AMC\nMCS, rank, precoder (PMI),\nRB allocation;"
        "\nouter loop: CQI offset\nfrom ACK/NACK", fc=lighten(C["dl"], 0.7),
        rounded=True, fs=FS_S)
    box(ax, *B, "PHY TX\nLDPC, QAM, layers,\nprecoding; + DMRS, CSI-RS",
        fc=lighten(C["dl"], 0.7), rounded=True, fs=FS_S)
    box(ax, *CH, "DL radio channel\nH(t, f) + noise\n+ interference",
        fc=LIGHT, rounded=True, fs=FS_S)
    box(ax, *U, "UE receiver\nchannel estimation (DMRS, CSI-RS)\n"
        "→ MIMO detection → LLRs\n→ LDPC decoding → CRC", fc=lighten(C["ul"], 0.6),
        rounded=True, fs=FS_S)
    box(ax, *E, "CSI computation\nCQI, RI, PMI (from CSI-RS)",
        fc=lighten(C["ul"], 0.6), rounded=True, fs=FS_S)
    box(ax, *F, "UL feedback (UCI)\non PUCCH or PUSCH", fc=LIGHT,
        rounded=True, fs=FS_S)
    arrow(ax, A[0] + A[2] / 2, A[1] + A[3], B[0] + B[2] / 2, B[1])
    arrow(ax, B[0] + B[2], 36.5, CH[0], 36.5)
    ax.text(33.5, 37.2, "PDSCH", ha="center", va="bottom", fontsize=FS_S - 1)
    arrow(ax, CH[0] + CH[2], 36.5, U[0], 36.5)
    arrow(ax, U[0] + U[2] / 2, U[1], E[0] + E[2] / 2, E[1] + E[3])
    ax.text(U[0] + U[2] / 2 + 1, 24, "CSI-RS\nestimates", fontsize=FS_S - 1,
            va="center")
    arrow(ax, E[0], 13.5, F[0] + F[2], 13.5)
    ax.text(65.2, 15.0, "CQI/RI/PMI", ha="center", va="bottom", fontsize=FS_S - 1)
    polyarrow(ax, [(U[0], 32.0), (66.0, 32.0), (66.0, 24.5), (56.0, 24.5),
                   (56.0, F[1] + F[3])], color=C["accent"])
    ax.text(61.0, 25.3, "HARQ ACK/NACK", fontsize=FS_S, color=C["accent"],
            va="bottom", ha="center")
    arrow(ax, F[0], 13.5, A[0] + A[2], 13.5)
    ax.text(33.5, 15.0, "UCI", ha="center", va="bottom", fontsize=FS_S - 1)
    ax.text(50, 54, "Link adaptation (AMC) loop", ha="center", weight="bold")
    save(fig, "amc_loop")


# --------------------------------------------------------------------------
# 17. PDCCH candidates
# --------------------------------------------------------------------------
def pdcch_candidates():
    fig, ax = canvas(10, 5.3)
    x0, rw = 14.0, 1.6
    nrb = 48
    yA, hA = 39.0, 3.2     # symbol 0 row (top)
    yB = yA - hA           # symbol 1 row
    for c in range(16):
        fc = C["pdcch_l"] if c % 2 == 0 else lighten(C["pdcch"], 0.55)
        box(ax, x0 + 3 * c * rw, yB, 3 * rw, 2 * hA, fc=fc, ec="none", z=1)
        ax.text(x0 + (3 * c + 1.5) * rw, yA + hA + 0.5, str(c), ha="center",
                va="bottom", fontsize=FS_S)
    for i in range(nrb + 1):
        ax.plot([x0 + i * rw] * 2, [yB, yA + hA], color=INK,
                lw=1.4 if i % 3 == 0 else 0.4, zorder=3)
    for yy in (yB, yA, yA + hA):
        ax.plot([x0, x0 + nrb * rw], [yy] * 2, color=INK,
                lw=1.4 if yy != yA else 0.4, zorder=3)
    ax.text(x0 - 0.8, yA + hA / 2, "symbol 0", ha="right", va="center",
            fontsize=FS_S)
    ax.text(x0 - 0.8, yB + hA / 2, "symbol 1", ha="right", va="center",
            fontsize=FS_S)
    ax.text(x0 - 0.8, yA + hA + 1.2, "CCE", ha="right", va="center",
            fontsize=FS_S, weight="bold")
    dim(ax, x0, x0 + nrb * rw, yA + hA + 4.5,
        "CORESET: 48 RBs × 2 symbols = 96 REGs = 16 CCEs", fs=FS_S + 1)
    ax.text(x0 + nrb * rw + 1, yB + hA,
            "REG =\n1 RB ×\n1 symbol", fontsize=FS_S - 1, va="center",
            color=GREY)
    ax.text(x0, yB - 1.5, "non-interleaved CCE-to-REG mapping, REGs numbered "
            "time-first → one CCE = 3 RBs × 2 symbols",
            fontsize=FS_S - 0.5, color=GREY, va="top")
    # candidates
    rows = [(4, 4, 25.5), (8, 2, 19.5), (16, 1, 13.5)]
    cw = 3 * rw
    for L, M, y in rows:
        ax.text(x0 - 0.8, y + 2, f"AL {L}\n({M} cand.)", ha="right",
                va="center", fontsize=FS_S)
        for m in range(M):
            c0 = L * m
            box(ax, x0 + c0 * cw + 0.15, y, L * cw - 0.3, 4.0,
                f"candidate {m}: CCE {c0}–{c0 + L - 1}",
                fc=lighten(C["pdcch"], 0.15 + 0.2 * (m % 2)), ec=INK,
                tc="white", fs=FS_S - 0.5, rounded=True)
    ax.text(x0 + nrb * rw, 11.2, "positions from the search-space hashing "
            "function (TS 38.213 §10.1), drawn for Y = 0",
            ha="right", va="top", fontsize=FS_S - 0.5, color=GREY)
    # REG detail
    rx, rsw = x0, 2.0
    for k in range(12):
        d = k in (1, 5, 9)
        box(ax, rx + k * rsw, 3.5, rsw, 2.6, fc=C["dmrs"] if d else C["pdcch_l"],
            lw=0.5)
    ax.text(rx + 12 * rsw + 1.2, 4.8, "1 REG = 12 RE: 9 data + 3 DMRS "
            "(subcarriers 1, 5, 9)", fontsize=FS_S, va="center")
    ax.text(x0 + nrb * rw, 4.8, "CCE = 6 REG = 72 RE\n(54 data + 18 DMRS)",
            ha="right", va="center", fontsize=FS, weight="bold")
    save(fig, "pdcch_candidates")


# --------------------------------------------------------------------------
# 18. From the resource grid to the IFFT input, and the cyclic prefix
# --------------------------------------------------------------------------
def ofdm_ifft_mapping():
    fig, ax = canvas(10.5, 5.4)
    neg, pos, zero = C["pdsch"], C["pdcch"], LIGHT
    x0, W = 8, 92                           # common horizontal extent

    # (1) resource grid of one symbol, K = N_grid * 12 subcarriers
    y1 = 44
    ax.text(x0, y1 + 6.5, "Resource grid of symbol $l$: $K = N_{grid}^{size}\\,N_{sc}^{RB}$ subcarriers, "
            "$a_{k,l}$ for $k = 0 \\dots K-1$", fontsize=FS, va="bottom")
    gx, gw = x0 + 18, 56
    box(ax, gx, y1, gw / 2, 4, "$k < K/2$: below the carrier centre", fc=neg, fs=FS_S)
    box(ax, gx + gw / 2, y1, gw / 2, 4, "$k \\geq K/2$: above the carrier centre", fc=pos, tc="white", fs=FS_S)
    ax.text(gx - 1, y1 + 2, "frequency\n$(k - K/2)\\,\\Delta f$", ha="right", va="center", fontsize=FS_S)
    vline(ax, gx + gw / 2, y1 - 1.5, y1 + 5.5, color=C["accent"], ls="-", lw=1.4)
    ax.text(gx + gw / 2 + 1, y1 + 5.2, "DC (carrier centre, $f_0$)", ha="left", va="center",
            fontsize=FS_S, color=C["accent"])

    # (2) IFFT input bins m = 0 .. N-1
    y2 = 25
    ax.text(x0, y2 + 6.5, "IFFT input, $N$ bins ($N > K$, e.g. $N = 4096$):  bin $m = (k - K/2) \\mathrm{mod}\\ N$",
            fontsize=FS, va="bottom")
    bw = W - 10
    bx = x0 + 6
    seg = bw * 0.36
    box(ax, bx, y2, seg, 4, "bins $0 \\dots K/2-1$", fc=pos, tc="white", fs=FS_S)
    box(ax, bx + seg, y2, bw - 2 * seg, 4, "zeros: guard band / oversampling", fc=zero, fs=FS_S)
    box(ax, bx + bw - seg, y2, seg, 4, "bins $N-K/2 \\dots N-1$", fc=neg, fs=FS_S)
    ax.text(bx, y2 - 1, "0", ha="center", va="top", fontsize=FS_S)
    ax.text(bx + bw, y2 - 1, "$N-1$", ha="center", va="top", fontsize=FS_S)
    # crossing arrows: upper half -> low bins, lower half -> high bins
    arrow(ax, gx + gw * 0.75, y1, bx + seg / 2, y2 + 4.2, color=pos)
    arrow(ax, gx + gw * 0.25, y1, bx + bw - seg / 2, y2 + 4.2, color=neg)
    ax.text(x0 + W - 1, (y1 + y2 + 4) / 2 + 1, "negative frequencies wrap\nto the top of the IFFT\n(\"fftshift\")",
            ha="right", va="center", fontsize=FS_S, color=GREY)

    # (3) time samples of the symbol: CP + N samples
    y3 = 6
    ax.text(x0, y3 + 6.5, "IFFT output at $f_s = N\\,\\Delta f$:  $N_{CP}$ + $N$ samples", fontsize=FS, va="bottom")
    cpw, nw = 9, bw - 9
    box(ax, bx, y3, cpw, 4, "CP", fc=lighten(C["ssb"], 0.3), fs=FS_S)
    box(ax, bx + cpw, y3, nw - cpw, 4, "$s[n]$,  $n = 0 \\dots N-1$", fc="white", fs=FS_S)
    box(ax, bx + nw, y3, cpw, 4, "", fc=lighten(C["ssb"], 0.3))
    ax.text(bx + nw + cpw / 2, y3 + 2, "tail", ha="center", va="center", fontsize=FS_S)
    ax.annotate("", xy=(bx + cpw / 2, y3 + 4.2), xytext=(bx + nw + cpw / 2, y3 + 4.2), zorder=4,
                arrowprops=dict(arrowstyle="-|>", color=C["ssb"], lw=1.3, mutation_scale=12,
                                connectionstyle="arc3,rad=0.25", shrinkA=0, shrinkB=0))
    ax.text(bx + bw / 2, y3 - 1, "copy of the last $N_{CP}$ samples = the 3GPP formula evaluated for "
            "$-N_{CP} \\leq n < 0$ (periodicity of $e^{j2\\pi mn/N}$)",
            ha="center", va="top", fontsize=FS_S, color=GREY)
    save(fig, "ofdm_ifft_mapping")


# --------------------------------------------------------------------------
def main():
    global PNG_DIR
    ap = argparse.ArgumentParser()
    ap.add_argument("--png", help="also write PNG previews to this directory")
    args = ap.parse_args()
    if args.png:
        PNG_DIR = args.png
        os.makedirs(PNG_DIR, exist_ok=True)
    for f in (frame_structure, resource_grid, channel_bandwidth, bwp,
              ofdm_chain, ssb_structure, ssb_beams, coreset0_layout,
              ra_procedure, prach_tx, prach_rx, timing_advance, ulsch_chain,
              power_ramping, tdd_pattern, amc_loop, pdcch_candidates,
              ofdm_ifft_mapping):
        f()
        print("wrote", f.__name__ + ".svg")


if __name__ == "__main__":
    main()
