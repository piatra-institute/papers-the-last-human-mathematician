"""Figures for 1976-2036: From the Last Human Computer to the Last Human Mathematician."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

INK, GRID, AMBER, GREEN, BLUE, GRAY, RED = ("#1a1a1a", "#d9d9d9", "#b45309", "#15803d", "#2563eb", "#78716c", "#b3202c")


def _style(ax):
    ax.grid(True, color=GRID, lw=0.5)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.tick_params(labelsize=8)


def _title(ax, t):
    ax.set_title(t, fontsize=9.5, loc="left")


def _arr(x):
    return np.array([np.nan if v is None else v for v in x], dtype=float)


def plot_computer(r, path):
    c = r["computer"]
    y = np.array(c["years"])
    fig, axes = plt.subplots(1, 2, figsize=(11.6, 3.9))
    ax = axes[0]
    ax.semilogy(y, _arr(c["fc"]), color=INK, lw=1.4)
    sh = c["share"]["high"]
    for b, ls, lab in ((sh["baseline"], "--", "wartime peak of the human sense"),
                       (c["share"]["low"]["baseline"], ":", "pre-war level")):
        ax.axhline(2 * b, color=GRAY, lw=0.9, ls=ls, label=f"twice the {lab}")
    ax.axvline(1946, color=BLUE, lw=0.8)
    ax.axvline(1976, color=RED, lw=0.8)
    ax.text(1947, 3e-7, "1946", color=BLUE, fontsize=7.5)
    ax.text(1977, 3e-7, "1976", color=RED, fontsize=7.5)
    ax.set_xlim(1900, 2022)
    ax.set_xlabel("year", fontsize=9)
    ax.set_ylabel("relative frequency of computer(s)", fontsize=9)
    ax.legend(fontsize=7.5, frameon=False, loc="upper left")
    _title(ax, "a. frequency of the noun in English books")
    _style(ax)
    ax = axes[1]
    ax.plot(y, 100 * _arr(c["m"]), color=AMBER, lw=1.6, label="machine marked (electronic, digital, automatic)")
    ax2 = ax.twinx()
    ax2.plot(y, 100 * _arr(c["h"]), color=GREEN, lw=1.4, label="human marked (human computer, net of HCI)")
    ax.axvline(1976, color=RED, lw=0.8)
    ax.set_xlim(1940, 2022)
    ax.set_ylim(0, 26)
    ax2.set_ylim(0, 0.16)
    ax.set_xlabel("year", fontsize=9)
    ax.set_ylabel("machine-marked share of uses (%)", fontsize=9, color=AMBER)
    ax2.set_ylabel("human-marked share of uses (%)", fontsize=9, color=GREEN)
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, fontsize=7.5, frameon=False, loc="upper right")
    _title(ax, "b. qualified uses as a share of all uses")
    _style(ax)
    ax2.tick_params(labelsize=8)
    ax2.spines["top"].set_visible(False)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def plot_typewriter(r, path):
    t = r["typewriter"]
    y = np.array(t["years"])
    fig, ax = plt.subplots(1, 1, figsize=(6.2, 3.6))
    ax.plot(y, 100 * _arr(t["person_rate"]), color=GREEN, lw=1.6, label="person marked (typewriter girl, lady typewriter)")
    ax2 = ax.twinx()
    ax2.plot(y, _arr(t["typist_ratio"]), color=INK, lw=1.4, label="typist(s) per typewriter(s)")
    ax.set_xlim(1880, 1950)
    ax.set_xlabel("year", fontsize=9)
    ax.set_ylabel("person-marked share of uses (%)", fontsize=9, color=GREEN)
    ax2.set_ylabel("ratio of frequencies", fontsize=9)
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, fontsize=7.5, frameon=False, loc="upper left")
    _title(ax, "typewriter and typist in English books, 1880 to 1950")
    _style(ax)
    ax2.spines["top"].set_visible(False)
    ax2.tick_params(labelsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def plot_mathematician(r, path):
    mb, ms = r["mathematician_books"], r["mathematician_scholarly"]
    fig, axes = plt.subplots(1, 2, figsize=(11.6, 3.9))
    ax = axes[0]
    y = np.array(mb["years"])
    ax.plot(y, 100 * _arr(mb["h"]), color=GREEN, lw=1.5, label="human mathematician(s)")
    ax.plot(y, 100 * _arr(mb["m"]), color=AMBER, lw=1.3, label="machine-qualified forms")
    ax.set_xlim(1940, 2022)
    ax.set_xlabel("year", fontsize=9)
    ax.set_ylabel("share of uses of mathematician(s) (%)", fontsize=9)
    ax.legend(fontsize=7.5, frameon=False, loc="upper left")
    _title(ax, "a. English books, to 2022")
    _style(ax)
    ax = axes[1]
    yrs = ms["years"]
    base = ms["mathematician"]
    raw = [100 * ms["human"][str(k)] / base[str(k)] for k in yrs]
    cl = [100 * ms["clean"][str(k)]["phrase"] / base[str(k)] for k in yrs]
    mac = [100 * ms["machine"][str(k)] / base[str(k)] for k in yrs]
    ax.plot(yrs, raw, "o-", color=GREEN, mfc="none", lw=1.0, ms=4, label="human mathematician, all records")
    ax.plot(yrs, cl, "o-", color=GREEN, lw=1.6, ms=4, label="human mathematician, deduplicated and verified")
    ax.plot(yrs, mac, "s-", color=AMBER, lw=1.3, ms=4, label="AI, automated, artificial, machine or robot mathematician")
    ax.set_xlabel("publication year (2026 to 8 October)", fontsize=9)
    ax.set_ylabel("share of works using mathematician (%)", fontsize=9)
    ax.legend(fontsize=7.5, frameon=False, loc="upper left")
    _title(ax, "b. titles and abstracts of scholarly works, 2016 to 2026")
    _style(ax)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def make_all(r, out):
    import json
    r = json.loads(json.dumps(r, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o)))
    out = Path(out)
    plot_computer(r, out / "computer.png")
    plot_typewriter(r, out / "typewriter.png")
    plot_mathematician(r, out / "mathematician.png")
