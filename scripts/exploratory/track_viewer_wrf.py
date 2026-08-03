"""
Script: Visualizador do Track do Ciclone Biguá (rastreado no WRF)
Objetivo: Plotar a trajetória do ciclone (posição bruta e corrigida,
a partir da vorticidade em 850 hPa) sobre o domínio WRF
Autor: Danilo Couto de Souza
Data: 2026-08-03

Track gerado diretamente da simulação WRF (data/bigua_track_track_WRF.csv),
com posição bruta (lat/lon) e corrigida (lat_corrigida/lon_corrigida) do
centro do ciclone, rastreado via mínimo de vorticidade em 850 hPa.
"""

import xarray as xr
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

DATA_FILE = Path("data/WRF_d02_bigua_LEC.nc")
TRACK_FILE = Path("data/bigua_track_track_WRF.csv")
OUTPUT_DIR = Path("figures/exploratory")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("VISUALIZADOR DE TRACK — CICLONE BIGUÁ (domínio WRF)")
print("=" * 70)

print("\n[1] Carregando arquivo WRF...")
if not DATA_FILE.exists():
    print(f"    ✗ Erro: Arquivo não encontrado: {DATA_FILE}")
    exit(1)
ds = xr.open_dataset(DATA_FILE)
print("    ✓ Arquivo carregado!")

print("\n[2] Carregando track do ciclone (WRF)...")
if not TRACK_FILE.exists():
    print(f"    ✗ Erro: Arquivo não encontrado: {TRACK_FILE}")
    exit(1)
track = pd.read_csv(TRACK_FILE)
print(f"    ✓ Track carregado! Colunas: {list(track.columns)}")
print(f"    Número de pontos: {len(track)}")

lat_raw, lon_raw = track["lat"].values, track["lon"].values
lat_corr, lon_corr = track["lat_corrigida"].values, track["lon_corrigida"].values
print(f"    Lat range (bruto): [{lat_raw.min():.2f}, {lat_raw.max():.2f}]")
print(f"    Lon range (bruto): [{lon_raw.min():.2f}, {lon_raw.max():.2f}]")

print("\n[3] Extraindo domínio WRF...")
lat_wrf = ds.coords["lat"].values
lon_wrf = ds.coords["lon"].values
print(f"    WRF Lat range: [{lat_wrf.min():.2f}, {lat_wrf.max():.2f}]")
print(f"    WRF Lon range: [{lon_wrf.min():.2f}, {lon_wrf.max():.2f}]")

print("\n[4] Gerando mapa...")
fig = plt.figure(figsize=(12, 10))
ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
ax.set_extent([lon_wrf.min(), lon_wrf.max(), lat_wrf.min(), lat_wrf.max()], crs=ccrs.PlateCarree())
ax.coastlines(resolution="10m", linewidth=0.7)
ax.add_feature(cfeature.BORDERS, linewidth=0.5)
ax.add_feature(cfeature.LAND, facecolor="lightgray", alpha=0.3)
ax.add_feature(cfeature.OCEAN, facecolor="lightblue", alpha=0.3)
ax.gridlines(draw_labels=True, linewidth=0.3, alpha=0.5)

# Posição bruta (referência)
ax.plot(lon_raw, lat_raw, "--", color="gray", linewidth=1.5, label="Posição bruta",
        transform=ccrs.PlateCarree(), zorder=4)
ax.scatter(lon_raw, lat_raw, c="gray", s=25, marker="o", transform=ccrs.PlateCarree(), zorder=4, alpha=0.7)

# Posição corrigida (principal)
ax.plot(lon_corr, lat_corr, "r-", linewidth=2.5, label="Posição corrigida",
        transform=ccrs.PlateCarree(), zorder=5)
ax.scatter(lon_corr, lat_corr, c="red", s=50, marker="o", transform=ccrs.PlateCarree(),
           zorder=6, edgecolors="darkred", linewidth=1)

ax.scatter(lon_corr[0], lat_corr[0], c="green", s=200, marker="s", label="Início",
           transform=ccrs.PlateCarree(), zorder=7, edgecolors="darkgreen", linewidth=2)
ax.scatter(lon_corr[-1], lat_corr[-1], c="blue", s=200, marker="^", label="Fim",
           transform=ccrs.PlateCarree(), zorder=7, edgecolors="darkblue", linewidth=2)

n_points = len(track)
skip = max(1, n_points // 10)
for i in range(0, n_points, skip):
    ax.text(lon_corr[i], lat_corr[i], str(i), fontsize=8, transform=ccrs.PlateCarree(), zorder=8, ha="center")

ax.set_title(f"Track do Ciclone Biguá (vort. 850 hPa)\nDomínio WRF — {n_points} pontos",
             fontsize=14, fontweight="bold", pad=20)
ax.legend(loc="upper left", fontsize=10, framealpha=0.9)
plt.tight_layout()

output_file = OUTPUT_DIR / "wrf_track_overview.png"
plt.savefig(output_file, dpi=150, bbox_inches="tight")
print(f"    ✓ Salvo: {output_file}")

print("\n" + "=" * 70)
print("RESUMO")
print("=" * 70)
print(f"Período: {track['time'].iloc[0]} a {track['time'].iloc[-1]}")
print(f"Trajetória: {n_points} pontos de tracking (mínimo de vorticidade 850 hPa)")
print(f"Domínio WRF: {lat_wrf.min():.2f}–{lat_wrf.max():.2f}°, {lon_wrf.min():.2f}–{lon_wrf.max():.2f}°")
print(f"✓ Mapa salvo: {output_file}")

ds.close()
print("\n✓ Script concluído!")
