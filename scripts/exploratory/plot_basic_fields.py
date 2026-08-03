"""
Script: Mapas Básicos dos Campos do Ciclone Biguá
Objetivo: Gerar mapas simples de temperatura, vento e geopotencial em níveis selecionados
Níveis: 1000, 850, 500, 250 hPa
Data: 2026-07-22
Autor: Danilo Couto de Souza
"""

import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from pathlib import Path

# --- Configurações ---
DATA_FILE = Path("data/ERA5_d02_bigua_LCT.nc")
OUTPUT_DIR = Path("figures/exploratory")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Níveis de pressão para plotar (hPa)
LEVELS_TO_PLOT = [1000, 850, 500, 250]

# Time step para plotar (índice ou 'middle' para meio da série)
TIME_INDEX = 'middle'  # Ajustar conforme necessário

print("=" * 70)
print("MAPAS BÁSICOS — CICLONE BIGUÁ")
print("=" * 70)

# --- 1. Carregar dados ---
print("\n[1] Carregando dados WRF...")
try:
    ds = xr.open_dataset(DATA_FILE)
    print("    ✓ Arquivo carregado com sucesso!")
except FileNotFoundError:
    print(f"    ✗ Erro: Arquivo {DATA_FILE} não encontrado!")
    exit(1)

# --- 2. Identificar nomes das variáveis ---
print("\n[2] Identificando variáveis...")
print("    ATENÇÃO: Ajuste os nomes das variáveis conforme seu arquivo WRF!")
print("    Variáveis disponíveis:", list(ds.data_vars))

# Tente identificar automaticamente (ajuste conforme necessário)
# Mapeamento comum de variáveis WRF:
var_map = {
    'temperature': 't',        # Identificado: t
    'u_wind': 'u',             # Identificado: u  
    'v_wind': 'v',             # Identificado: v
    'geopotential': 'z',       # Identificado: z
    'pressure': 'plev'         # Identificado: plev
}

print(f"    Mapeamento identificado (direto do dataset):")
for key, val in var_map.items():
    print(f"      ✓ {key:15s}: {val}")

# --- 3. Extrair coordenadas ---
print("\n[3] Extraindo coordenadas...")
lat_name = 'lat'
lon_name = 'lon'
time_name = 'time'

lats = ds.coords[lat_name].values
lons = ds.coords[lon_name].values
print(f"    Lat: {lats.min():.2f} a {lats.max():.2f}")
print(f"    Lon: {lons.min():.2f} a {lons.max():.2f}")

# --- 4. Selecionar time step ---
if TIME_INDEX == 'middle':
    TIME_INDEX = len(ds[time_name]) // 2
    
print(f"\n[4] Selecionando time step (índice {TIME_INDEX})...")
ds_time = ds.isel({time_name: TIME_INDEX})
time_value = ds[time_name].values[TIME_INDEX]
print(f"    Time selecionado: {time_value}")

# --- 5. Gerar mapas para cada nível ---
print(f"\n[5] Gerando mapas para níveis: {LEVELS_TO_PLOT} hPa...")

for level_hpa in LEVELS_TO_PLOT:
    print(f"\n  → Nível {level_hpa} hPa")
    
    # Converter para Pa (pressões no arquivo estão em Pa)
    level_pa = level_hpa * 100
    
    try:
        # Selecionar o nível mais próximo
        ds_level = ds_time.sel({var_map['pressure']: level_pa}, method='nearest')
    except Exception as e:
        print(f"    ✗ Erro ao selecionar nível {level_hpa} hPa: {e}")
        continue
    
    # Extrair variáveis
    T = ds_level[var_map['temperature']].values
    U = ds_level[var_map['u_wind']].values
    V = ds_level[var_map['v_wind']].values
    
    # Calcular magnitude do vento
    wind_speed = np.sqrt(U**2 + V**2)
    
    # Criar figura
    fig = plt.figure(figsize=(15, 5))
    
    # --- Subplot 1: Temperatura ---
    ax1 = fig.add_subplot(1, 3, 1, projection=ccrs.PlateCarree())
    ax1.set_extent([lons.min(), lons.max(), lats.min(), lats.max()], crs=ccrs.PlateCarree())
    ax1.coastlines(resolution='10m', linewidth=0.5)
    ax1.add_feature(cfeature.BORDERS, linewidth=0.3)
    ax1.gridlines(draw_labels=True, linewidth=0.3, alpha=0.5)
    
    # Converter de K para °C se necessário
    if T.mean() > 200:  # Provavelmente em Kelvin
        T_plot = T - 273.15
        unit_T = "°C"
    else:
        T_plot = T
        unit_T = "K"
    
    cf1 = ax1.contourf(lons, lats, T_plot, levels=15, cmap='RdYlBu_r', transform=ccrs.PlateCarree())
    plt.colorbar(cf1, ax=ax1, orientation='horizontal', pad=0.05, label=f'Temperatura ({unit_T})')
    ax1.set_title(f'Temperatura — {level_hpa} hPa')
    
    # --- Subplot 2: Velocidade do vento ---
    ax2 = fig.add_subplot(1, 3, 2, projection=ccrs.PlateCarree())
    ax2.set_extent([lons.min(), lons.max(), lats.min(), lats.max()], crs=ccrs.PlateCarree())
    ax2.coastlines(resolution='10m', linewidth=0.5)
    ax2.add_feature(cfeature.BORDERS, linewidth=0.3)
    ax2.gridlines(draw_labels=True, linewidth=0.3, alpha=0.5)
    
    cf2 = ax2.contourf(lons, lats, wind_speed, levels=15, cmap='YlOrRd', transform=ccrs.PlateCarree())
    plt.colorbar(cf2, ax=ax2, orientation='horizontal', pad=0.05, label='Velocidade do Vento (m/s)')
    
    # Adicionar vetores de vento (subsample para clareza)
    skip = max(1, len(lons) // 15)  # Subsample
    ax2.quiver(lons[::skip], lats[::skip], 
               U[::skip, ::skip], V[::skip, ::skip],
               transform=ccrs.PlateCarree(), scale=200, width=0.003)
    ax2.set_title(f'Vento — {level_hpa} hPa')
    
    # --- Subplot 3: Geopotencial ---
    ax3 = fig.add_subplot(1, 3, 3, projection=ccrs.PlateCarree())
    ax3.set_extent([lons.min(), lons.max(), lats.min(), lats.max()], crs=ccrs.PlateCarree())
    ax3.coastlines(resolution='10m', linewidth=0.5)
    ax3.add_feature(cfeature.BORDERS, linewidth=0.3)
    ax3.gridlines(draw_labels=True, linewidth=0.3, alpha=0.5)
    
    Z = ds_level[var_map['geopotential']].values
    # Geopotencial já está em m²/s², converter para metros geopotenciais
    Z_plot = Z / 9.81  # m²/s² → m
    
    # Contornos de geopotencial
    cf3 = ax3.contour(lons, lats, Z_plot, levels=15, colors='black', linewidths=1, transform=ccrs.PlateCarree())
    ax3.clabel(cf3, inline=True, fontsize=8, fmt='%d')
    
    # Preencher com cores também
    cf3_fill = ax3.contourf(lons, lats, Z_plot, levels=15, cmap='terrain', alpha=0.3, transform=ccrs.PlateCarree())
    plt.colorbar(cf3_fill, ax=ax3, orientation='horizontal', pad=0.05, label='Altura Geopotencial (m)')
    ax3.set_title(f'Geopotencial — {level_hpa} hPa')
    
    # Título geral
    fig.suptitle(f'Ciclone Biguá — {level_hpa} hPa — Time: {time_value}', 
                 fontsize=14, fontweight='bold', y=1.02)
    
    plt.tight_layout()
    
    # Salvar figura
    output_file = OUTPUT_DIR / f"basic_fields_{level_hpa}hPa.png"
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"    ✓ Salvo: {output_file}")
    plt.close()

# --- 6. Resumo ---
print("\n" + "=" * 70)
print("RESUMO")
print("=" * 70)
print(f"✓ Mapas salvos em: {OUTPUT_DIR}/")
print(f"✓ Níveis plotados: {LEVELS_TO_PLOT} hPa")
print(f"✓ Time step: {TIME_INDEX} ({time_value})")
print("\nPróximos passos:")
print("  - Ajustar TIME_INDEX para explorar outros time steps")
print("  - Ajustar LEVELS_TO_PLOT para outros níveis")
print("  - Implementar análise do ciclo de vida (loop temporal)")
print("  - Implementar análise do Ciclo de Energia de Lorenz")

ds.close()
print("\n✓ Script concluído!")
