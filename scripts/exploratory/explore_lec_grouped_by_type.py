"""
Exploratório: Séries temporais dos termos do LEC agrupados por tipo — ERA5 vs WRF
Painel 2x2 por tipo de termo:
  - Energia: Ae, Ke
  - Conversão: Ck, Ca, Ce
  - Fronteira: BAe, BKe
  - Geração: Ge, Gz
Cor = termo; linha/marcador = dataset (ERA5: contínua + círculo; WRF: tracejada + quadrado)
Output: figures/exploratory/explore_lec_grouped_by_type.png
Depends:
  results/ERA5_d02_bigua_LCT_track/ERA5_d02_bigua_LCT_track_results.csv
  results/WRF_d02_bigua_LEC_track/WRF_d02_bigua_LEC_track_results.csv
"""

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
from matplotlib.lines import Line2D
from pathlib import Path

# --- Config ---
FIGURES_DIR = Path("figures/exploratory")
FIGURES_DIR.mkdir(parents=True, exist_ok=True)
DPI = 150

ERA5_CSV = Path("results/ERA5_d02_bigua_LCT_track/ERA5_d02_bigua_LCT_track_results.csv")
WRF_CSV = Path("results/WRF_d02_bigua_LEC_track/WRF_d02_bigua_LEC_track_results.csv")

TERM_LABELS = {
    "Ae": r"$A_E$", "Ke": r"$K_E$",
    "Ck": r"$C_K$", "Ca": r"$C_A$", "Ce": r"$C_E$",
    "BAe": r"$B_{A_E}$", "BKe": r"$B_{K_E}$",
    "Ge": r"$G_E$", "Gz": r"$G_Z$",
}

PANELS = [
    {"title": "Energy", "terms": ["Ae", "Ke"], "ylabel": r"Energy (J m$^{-2}$)", "sci": True},
    {"title": "Conversion", "terms": ["Ck", "Ca", "Ce"], "ylabel": r"Conversion (W m$^{-2}$)", "sci": False},
    {"title": "Boundary flux", "terms": ["BAe", "BKe"], "ylabel": r"Boundary flux (W m$^{-2}$)", "sci": False},
    {"title": "Generation", "terms": ["Ge", "Gz"], "ylabel": r"Generation (W m$^{-2}$)", "sci": False},
]

TERM_COLORS = {term: color for term, color in zip(TERM_LABELS, plt.cm.tab10.colors)}

ERA5_STYLE = dict(linestyle="-", marker="o")
WRF_STYLE = dict(linestyle="--", marker="s")
MARKER_KW = dict(markersize=3.5, markerfacecolor="none", linewidth=1.1)

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 8,
    "axes.labelsize": 9,
    "axes.titlesize": 9,
    "xtick.labelsize": 7,
    "ytick.labelsize": 7,
    "legend.fontsize": 7,
    "axes.linewidth": 0.8,
})

# --- Load ---
era5 = pd.read_csv(ERA5_CSV, index_col=0, parse_dates=True)
wrf = pd.read_csv(WRF_CSV, index_col=0, parse_dates=True)

# --- Plot ---
fig, axes = plt.subplots(2, 2, figsize=(8.0, 6.5), sharex=True)

for ax, panel in zip(axes.flat, PANELS):
    for term in panel["terms"]:
        color = TERM_COLORS[term]
        ax.plot(era5.index, era5[term], color=color, label=TERM_LABELS[term], **ERA5_STYLE, **MARKER_KW)
        ax.plot(wrf.index, wrf[term], color=color, label="_nolegend_", **WRF_STYLE, **MARKER_KW)
    ax.axhline(0, color="gray", linewidth=0.5, linestyle=":", zorder=0)
    ax.set_title(panel["title"])
    ax.set_ylabel(panel["ylabel"])
    ax.tick_params(direction="in", top=True, right=True)
    for spine in ax.spines.values():
        spine.set_linewidth(0.8)
    if panel["sci"]:
        formatter = mticker.ScalarFormatter(useMathText=True)
        formatter.set_scientific(True)
        formatter.set_powerlimits((0, 0))
        ax.yaxis.set_major_formatter(formatter)
    ax.legend(loc="best", frameon=False, ncol=1)

for ax in axes[-1, :]:
    ax.set_xlabel("Time")
    fig.autofmt_xdate(rotation=30, ha="right")

# Global legend distinguishing datasets by line style/marker
dataset_handles = [
    Line2D([0], [0], color="black", label="ERA5", **ERA5_STYLE, **MARKER_KW),
    Line2D([0], [0], color="black", label="WRF", **WRF_STYLE, **MARKER_KW),
]
fig.legend(handles=dataset_handles, loc="upper center", ncol=2, frameon=False,
           bbox_to_anchor=(0.5, 1.03))

plt.tight_layout()

OUTPUT_FILE = FIGURES_DIR / "explore_lec_grouped_by_type.png"
plt.savefig(OUTPUT_FILE, dpi=DPI, bbox_inches="tight")
plt.close()
print(f"Saved: {OUTPUT_FILE}")
