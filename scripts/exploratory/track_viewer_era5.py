"""
Script: Visualizador do Track do Ciclone Biguá
Objetivo: Plotar a trajetória do ciclone sobre o domínio ERA5
Autor: Danilo Couto de Souza
Data: 2026-08-03

Nota: Usa o domínio ERA5 (data/ERA5_d02_bigua_LCT.nc) como referência
geográfica porque o arquivo WRF (data/WRF_d02_bigua.nc) não possui
coordenadas lat/lon reais — ver inspect_structure_wrf.py.
"""

import xarray as xr
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

DATA_FILE = Path("data/ERA5_d02_bigua_LCT.nc")
TRACK_FILE = Path("data/bigua_track_track_ERA.csv")
OUTPUT_DIR = Path("figures/exploratory")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("VISUALIZADOR DE TRACK — CICLONE BIGUÁ (domínio ERA5)")
print("=" * 70)

print("\n[1] Carregando arquivo ERA5...")
if not DATA_FILE.exists():
    print(f"    ✗ Erro: Arquivo não encontrado: {DATA_FILE}")
    exit(1)
ds = xr.open_dataset(DATA_FILE)
print("    ✓ Arquivo carregado!")

print("\n[2] Carregando track do ciclone...")
if not TRACK_FILE.exists():
    print(f"    ✗ Erro: Arquivo não encontrado: {TRACK_FILE}")
    exit(1)
track = pd.read_csv(TRACK_FILE, sep=";")
print(f"    ✓ Track carregado! Colunas: {list(track.columns)}")
print(f"    Número de pontos: {len(track)}")

track_lat = track["Lat"].values
track_lon = track["Lon"].values
print(f"    Lat range: [{track_lat.min():.2f}, {track_lat.max():.2f}]")
print(f"    Lon range: [{track_lon.min():.2f}, {track_lon.max():.2f}]")

print("\n[3] Extraindo domínio ERA5...")
lat_era5 = ds.coords["lat"].values
lon_era5 = ds.coords["lon"].values
print(f"    ERA5 Lat range: [{lat_era5.min():.2f}, {lat_era5.max():.2f}]")
print(f"    ERA5 Lon range: [{lon_era5.min():.2f}, {lon_era5.max():.2f}]")

print("\n[4] Gerando mapa...")
fig = plt.figure(figsize=(12, 10))
ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
ax.set_extent([lon_era5.min(), lon_era5.max(), lat_era5.min(), lat_era5.max()], crs=ccrs.PlateCarree())
ax.coastlines(resolution="10m", linewidth=0.7)
ax.add_feature(cfeature.BORDERS, linewidth=0.5)
ax.add_feature(cfeature.LAND, facecolor="lightgray", alpha=0.3)
ax.add_feature(cfeature.OCEAN, facecolor="lightblue", alpha=0.3)
ax.gridlines(draw_labels=True, linewidth=0.3, alpha=0.5)

ax.plot(track_lon, track_lat, "r-", linewidth=2.5, label="Track do ciclone", transform=ccrs.PlateCarree(), zorder=5)
ax.scatter(track_lon, track_lat, c="red", s=50, marker="o", transform=ccrs.PlateCarree(),
           zorder=6, edgecolors="darkred", linewidth=1)
ax.scatter(track_lon[0], track_lat[0], c="green", s=200, marker="s", label="Início",
           transform=ccrs.PlateCarree(), zorder=7, edgecolors="darkgreen", linewidth=2)
ax.scatter(track_lon[-1], track_lat[-1], c="blue", s=200, marker="^", label="Fim",
           transform=ccrs.PlateCarree(), zorder=7, edgecolors="darkblue", linewidth=2)

n_points = len(track_lon)
skip = max(1, n_points // 10)
for i in range(0, n_points, skip):
    ax.text(track_lon[i], track_lat[i], str(i), fontsize=8, transform=ccrs.PlateCarree(), zorder=8, ha="center")

ax.set_title(f"Track do Ciclone Biguá\nDomínio ERA5 — {n_points} pontos", fontsize=14, fontweight="bold", pad=20)
ax.legend(loc="upper left", fontsize=10, framealpha=0.9)
plt.tight_layout()

output_file = OUTPUT_DIR / "era5_track_overview.png"
plt.savefig(output_file, dpi=150, bbox_inches="tight")
print(f"    ✓ Salvo: {output_file}")

print("\n" + "=" * 70)
print("RESUMO")
print("=" * 70)
print(f"Período: {track['time'].iloc[0]} a {track['time'].iloc[-1]}")
print(f"Trajetória: {n_points} pontos de tracking")
print(f"Domínio ERA5: {lat_era5.min():.2f}–{lat_era5.max():.2f}°, {lon_era5.min():.2f}–{lon_era5.max():.2f}°")
print(f"✓ Mapa salvo: {output_file}")

ds.close()
print("\n✓ Script concluído!")
