"""
Script: Mapas Básicos dos Campos ERA5 do Ciclone Biguá
Objetivo: Gerar mapas de temperatura, vento e geopotencial em níveis selecionados
Níveis: 1000, 850, 500, 250 hPa
Autor: Danilo Couto de Souza
Data: 2026-08-03

Nota: data/ERA5_d02_bigua_LCT.nc é reanalysis ERA5 (condição de contorno do
WRF), não a saída do modelo WRF. Possui lat/lon reais, permitindo uso de
projeção cartográfica.
"""

import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from pathlib import Path

DATA_FILE = Path("data/ERA5_d02_bigua_LCT.nc")
OUTPUT_DIR = Path("figures/exploratory")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

LEVELS_TO_PLOT = [1000, 850, 500, 250]
TIME_INDEX = "middle"

print("=" * 70)
print("MAPAS BÁSICOS — CICLONE BIGUÁ (ERA5)")
print("=" * 70)

print("\n[1] Carregando dados ERA5...")
try:
    ds = xr.open_dataset(DATA_FILE)
    print("    ✓ Arquivo carregado com sucesso!")
except FileNotFoundError:
    print(f"    ✗ Erro: Arquivo {DATA_FILE} não encontrado!")
    exit(1)

lats = ds.coords["lat"].values
lons = ds.coords["lon"].values
print(f"    Lat: {lats.min():.2f} a {lats.max():.2f}")
print(f"    Lon: {lons.min():.2f} a {lons.max():.2f}")

if TIME_INDEX == "middle":
    TIME_INDEX = len(ds.coords["time"]) // 2
time_value = ds.coords["time"].values[TIME_INDEX]
print(f"\n[2] Time step selecionado: índice {TIME_INDEX} ({time_value})")

ds_time = ds.isel(time=TIME_INDEX)

print(f"\n[3] Gerando mapas para níveis: {LEVELS_TO_PLOT} hPa...")

for level_hpa in LEVELS_TO_PLOT:
    print(f"\n  → Nível {level_hpa} hPa")
    level_pa = level_hpa * 100

    try:
        ds_level = ds_time.sel(plev=level_pa, method="nearest")
    except Exception as e:
        print(f"    ✗ Erro ao selecionar nível {level_hpa} hPa: {e}")
        continue

    T = ds_level["t"].values
    U = ds_level["u"].values
    V = ds_level["v"].values
    Z = ds_level["z"].values / 9.81
    wind_speed = np.sqrt(U**2 + V**2)

    fig = plt.figure(figsize=(15, 5))

    ax1 = fig.add_subplot(1, 3, 1, projection=ccrs.PlateCarree())
    ax1.set_extent([lons.min(), lons.max(), lats.min(), lats.max()], crs=ccrs.PlateCarree())
    ax1.coastlines(resolution="10m", linewidth=0.5)
    ax1.add_feature(cfeature.BORDERS, linewidth=0.3)
    ax1.gridlines(draw_labels=True, linewidth=0.3, alpha=0.5)
    T_c = T - 273.15
    cf1 = ax1.contourf(lons, lats, T_c, levels=15, cmap="RdYlBu_r", transform=ccrs.PlateCarree())
    plt.colorbar(cf1, ax=ax1, orientation="horizontal", pad=0.05, label="Temperatura (°C)")
    ax1.set_title(f"Temperatura — {level_hpa} hPa")

    ax2 = fig.add_subplot(1, 3, 2, projection=ccrs.PlateCarree())
    ax2.set_extent([lons.min(), lons.max(), lats.min(), lats.max()], crs=ccrs.PlateCarree())
    ax2.coastlines(resolution="10m", linewidth=0.5)
    ax2.add_feature(cfeature.BORDERS, linewidth=0.3)
    ax2.gridlines(draw_labels=True, linewidth=0.3, alpha=0.5)
    cf2 = ax2.contourf(lons, lats, wind_speed, levels=15, cmap="YlOrRd", transform=ccrs.PlateCarree())
    plt.colorbar(cf2, ax=ax2, orientation="horizontal", pad=0.05, label="Velocidade do Vento (m/s)")
    skip = max(1, len(lons) // 15)
    ax2.quiver(lons[::skip], lats[::skip], U[::skip, ::skip], V[::skip, ::skip],
               transform=ccrs.PlateCarree(), scale=200, width=0.003)
    ax2.set_title(f"Vento — {level_hpa} hPa")

    ax3 = fig.add_subplot(1, 3, 3, projection=ccrs.PlateCarree())
    ax3.set_extent([lons.min(), lons.max(), lats.min(), lats.max()], crs=ccrs.PlateCarree())
    ax3.coastlines(resolution="10m", linewidth=0.5)
    ax3.add_feature(cfeature.BORDERS, linewidth=0.3)
    ax3.gridlines(draw_labels=True, linewidth=0.3, alpha=0.5)
    cs = ax3.contour(lons, lats, Z, levels=15, colors="black", linewidths=1, transform=ccrs.PlateCarree())
    ax3.clabel(cs, inline=True, fontsize=8, fmt="%d")
    cf3 = ax3.contourf(lons, lats, Z, levels=15, cmap="terrain", alpha=0.3, transform=ccrs.PlateCarree())
    plt.colorbar(cf3, ax=ax3, orientation="horizontal", pad=0.05, label="Altura Geopotencial (m)")
    ax3.set_title(f"Geopotencial — {level_hpa} hPa")

    fig.suptitle(f"Ciclone Biguá ERA5 — {level_hpa} hPa — Time: {time_value}",
                 fontsize=14, fontweight="bold", y=1.02)
    plt.tight_layout()

    output_file = OUTPUT_DIR / f"era5_basic_fields_{level_hpa}hPa.png"
    plt.savefig(output_file, dpi=150, bbox_inches="tight")
    print(f"    ✓ Salvo: {output_file}")
    plt.close()

print("\n" + "=" * 70)
print("RESUMO")
print("=" * 70)
print(f"✓ Mapas salvos em: {OUTPUT_DIR}/ (prefixo era5_)")
print(f"✓ Time step: {TIME_INDEX} ({time_value})")

ds.close()
print("\n✓ Script concluído!")
