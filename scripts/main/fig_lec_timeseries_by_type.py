"""
Figuras: Séries temporais dos termos do Ciclo de Energia de Lorenz — ERA5 vs WRF
Uma figura multipainel por tipo de termo (estilo Scientific Reports):
  - fig_01: Energia (Ae, Az, Kz, Ke)
  - fig_02: Conversão (Cz, Ca, Ck, Ce)
  - fig_03: Fronteira (BAz, BAe, BKz, BKe)
  - fig_04: Geração (Ge, Gz)
Cada subplot = um termo. ERA5 em preto, WRF em vermelho.
Output: figures/paper/fig_01_lec_energy_era5_vs_wrf.png
        figures/paper/fig_02_lec_conversion_era5_vs_wrf.png
        figures/paper/fig_03_lec_boundary_era5_vs_wrf.png
        figures/paper/fig_04_lec_generation_era5_vs_wrf.png
Depends:
  results/ERA5_d02_bigua_LCT_track/ERA5_d02_bigua_LCT_track_results.csv
  results/WRF_d02_bigua_LEC_track/WRF_d02_bigua_LEC_track_results.csv
"""

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
from pathlib import Path

# --- Config ---
FIGURES_DIR = Path("figures/paper")
FIGURES_DIR.mkdir(parents=True, exist_ok=True)
DPI = 300

ERA5_CSV = Path("results/ERA5_d02_bigua_LCT_track/ERA5_d02_bigua_LCT_track_results.csv")
WRF_CSV = Path("results/WRF_d02_bigua_LEC_track/WRF_d02_bigua_LEC_track_results.csv")

TERM_LABELS = {
    "Az": r"$A_Z$ (J m$^{-2}$)", "Ae": r"$A_E$ (J m$^{-2}$)",
    "Kz": r"$K_Z$ (J m$^{-2}$)", "Ke": r"$K_E$ (J m$^{-2}$)",
    "Cz": r"$C_Z$ (W m$^{-2}$)", "Ca": r"$C_A$ (W m$^{-2}$)",
    "Ck": r"$C_K$ (W m$^{-2}$)", "Ce": r"$C_E$ (W m$^{-2}$)",
    "BAz": r"$B_{A_Z}$ (W m$^{-2}$)", "BAe": r"$B_{A_E}$ (W m$^{-2}$)",
    "BKz": r"$B_{K_Z}$ (W m$^{-2}$)", "BKe": r"$B_{K_E}$ (W m$^{-2}$)",
    "Ge": r"$G_E$ (W m$^{-2}$)", "Gz": r"$G_Z$ (W m$^{-2}$)",
}

FIGURES = [
    {"output": "fig_01_lec_energy_era5_vs_wrf.png", "terms": ["Ae", "Az", "Kz", "Ke"],
     "shape": (2, 2), "sci": True},
    {"output": "fig_02_lec_conversion_era5_vs_wrf.png", "terms": ["Cz", "Ca", "Ck", "Ce"],
     "shape": (2, 2), "sci": False},
    {"output": "fig_03_lec_boundary_era5_vs_wrf.png", "terms": ["BAz", "BAe", "BKz", "BKe"],
     "shape": (2, 2), "sci": False},
    {"output": "fig_04_lec_generation_era5_vs_wrf.png", "terms": ["Ge", "Gz"],
     "shape": (1, 2), "sci": False},
]

ERA5_COLOR = "black"
WRF_COLOR = "red"

# Scientific Reports style
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 8,
    "axes.labelsize": 9,
    "axes.titlesize": 9,
    "xtick.labelsize": 7,
    "ytick.labelsize": 7,
    "legend.fontsize": 8,
    "axes.linewidth": 0.8,
})

# --- Load ---
era5 = pd.read_csv(ERA5_CSV, index_col=0, parse_dates=True)
wrf = pd.read_csv(WRF_CSV, index_col=0, parse_dates=True)


def make_figure(output, terms, shape, sci):
    nrows, ncols = shape
    fig, axes = plt.subplots(nrows, ncols, figsize=(7.2, 3.3 * nrows), sharex=True, squeeze=False)
    axes_flat = axes.flat

    for ax, term in zip(axes_flat, terms):
        ax.plot(era5.index, era5[term], color=ERA5_COLOR, linewidth=1.2, label="ERA5")
        ax.plot(wrf.index, wrf[term], color=WRF_COLOR, linewidth=1.2, label="WRF")
        ax.axhline(0, color="gray", linewidth=0.5, linestyle="--", zorder=0)
        ax.set_ylabel(TERM_LABELS[term])
        ax.tick_params(direction="in", top=True, right=True)
        for spine in ax.spines.values():
            spine.set_linewidth(0.8)
        if sci:
            formatter = mticker.ScalarFormatter(useMathText=True)
            formatter.set_scientific(True)
            formatter.set_powerlimits((0, 0))
            ax.yaxis.set_major_formatter(formatter)

    axes_flat[0].legend(loc="upper right", frameon=False)

    for ax in axes[-1, :]:
        ax.set_xlabel("Time")
    fig.autofmt_xdate(rotation=30, ha="right")

    plt.tight_layout()
    output_file = FIGURES_DIR / output
    plt.savefig(output_file, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {output_file}")


for figure_config in FIGURES:
    make_figure(**figure_config)
