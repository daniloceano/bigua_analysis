"""
Script: Exploração dos Dados ERA5 (condição de contorno da simulação WRF)
Objetivo: Inspecionar variáveis, dimensões, níveis, período e track do ciclone
Autor: Danilo Couto de Souza
Data: 2026-08-03

Nota: data/ERA5_d02_bigua_LCT.nc é reanalysis ERA5, não saída do WRF
(ver CHANGES_2026-08-03.md). Mantido como referência e como fonte de
condição de contorno / comparação com a simulação WRF de alta resolução.
"""

import xarray as xr
import pandas as pd
from pathlib import Path

DATA_FILE = Path("data/ERA5_d02_bigua_LCT.nc")
TRACK_FILE = Path("data/bigua_track_track_ERA.csv")

print("=" * 70)
print("EXPLORAÇÃO — CICLONE BIGUÁ (ERA5)")
print("=" * 70)

print("\n[1] Carregando arquivo ERA5...")
print(f"    Arquivo: {DATA_FILE}")
try:
    ds = xr.open_dataset(DATA_FILE)
    print("    ✓ Arquivo carregado com sucesso!")
except FileNotFoundError:
    print(f"    ✗ Erro: Arquivo {DATA_FILE} não encontrado!")
    exit(1)

print("\n[2] INFORMAÇÕES GERAIS")
print("-" * 70)
print(f"Tamanho em memória: {ds.nbytes / 1e9:.2f} GB")
print(f"Número de variáveis: {len(ds.data_vars)}")

print("\n[3] DIMENSÕES")
print("-" * 70)
for dim_name, dim_size in ds.dims.items():
    print(f"  {dim_name:20s}: {dim_size}")

print("\n[4] COORDENADAS")
print("-" * 70)
for coord_name in ds.coords:
    coord = ds.coords[coord_name]
    print(f"  {coord_name:20s}: shape={coord.shape}, dtype={coord.dtype}")
    if coord.size < 50 and coord.dtype != object:
        print(f"      valores: {coord.values}")

print("\n[5] VARIÁVEIS DISPONÍVEIS")
print("-" * 70)
for var_name in ds.data_vars:
    var = ds[var_name]
    print(f"  {var_name:10s}: shape={var.shape}, dtype={var.dtype}")
    if "long_name" in var.attrs:
        print(f"      {var.attrs['long_name']}  ({var.attrs.get('units', 'N/A')})")

print("\n[6] ATRIBUTOS GLOBAIS")
print("-" * 70)
for attr_name, attr_value in ds.attrs.items():
    print(f"  {attr_name}: {str(attr_value)[:150]}")

print("\n[7] NÍVEIS VERTICAIS")
print("-" * 70)
plev = ds.coords["plev"].values
print(f"  Coordenada: plev ({len(plev)} níveis, {ds.coords['plev'].attrs.get('units', 'Pa')})")
print(f"  Valores: {plev}")

print("\n[8] PERÍODO TEMPORAL")
print("-" * 70)
time_values = pd.to_datetime(ds.coords["time"].values)
print(f"  Início: {time_values[0]}")
print(f"  Fim:    {time_values[-1]}")
print(f"  Número de time steps: {len(time_values)}")
if len(time_values) > 1:
    print(f"  Resolução temporal: {time_values[1] - time_values[0]}")

print("\n[9] GEORREFERÊNCIA")
print("-" * 70)
lat, lon = ds.coords["lat"].values, ds.coords["lon"].values
print(f"  Lat: [{lat.min():.2f}, {lat.max():.2f}]°  |  Lon: [{lon.min():.2f}, {lon.max():.2f}]°")

print("\n[10] TRACK DO CICLONE")
print("-" * 70)
if TRACK_FILE.exists():
    try:
        track = pd.read_csv(TRACK_FILE, sep=";")
        print(f"  ✓ Track carregado: {TRACK_FILE}")
        print(f"  Colunas: {list(track.columns)}")
        print(f"  Número de pontos: {len(track)}")
        print(f"\n  Primeiras linhas:\n{track.head()}")
    except Exception as e:
        print(f"  ✗ Erro ao carregar track: {e}")
else:
    print(f"  ✗ Arquivo {TRACK_FILE} não encontrado.")

ds.close()
print("\n✓ Exploração concluída!")
print("\nPróximo passo: python scripts/exploratory/inspect_structure_era5.py (gera namelist do LEC)")
