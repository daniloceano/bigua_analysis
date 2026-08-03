"""
Script: Preparação do Arquivo WRF para o LorenzCycleToolkit
Objetivo: A partir do arquivo WRF bruto (data/WRF_d02_bigua.nc), gerar um
arquivo corrigido contendo:
  1. Apenas as variáveis necessárias para o LEC (t, ght, omega, u, v)
  2. Coordenadas lat/lon REAIS (graus), substituindo os índices de grade
     south_north/east_west originais
  3. Coordenada de tempo como datetime64 real (CF-compliant), substituindo
     as strings de tempo do arquivo bruto

Autor: Danilo Couto de Souza
Data: 2026-08-03 (corrigido em seguida: tempo como string quebrava o LEC)

Histórico:
O arquivo WRF_d02_bigua.nc perdeu a georreferência durante o processamento
com CDO (mergetime), ficando apenas com índices de grade (south_north 0-785,
east_west 0-878). Os arrays de latitude e longitude reais do domínio d02
foram recuperados separadamente (ver data/metadata/wrf_d02_latlon_download.json)
e são aplicados aqui.

Além disso, a coordenada `time` do arquivo bruto é armazenada como STRING
(`string time(time)` no netCDF), não como tempo codificado via CF-convention
(unidades + calendário). O LorenzCycleToolkit assume `time` como datetime64
e falha ao tentar subtrair dois valores de tempo
(numpy._core._exceptions._UFuncNoLoopError: subtract em dtype('<U19')).
Por isso, aqui convertemos `time` para datetime64 real antes de salvar —
o xarray então grava a codificação CF numérica correta no netCDF de saída.

Por fim, os primeiros time steps da simulação (2024-12-13 00h–09h) são
spin-up do modelo e não têm ponto de track correspondente — são descartados
aqui, cortando o dado para começar no mesmo instante do início do track
(data/bigua_track_track_WRF.csv).
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr

INPUT_FILE = Path("data/WRF_d02_bigua.nc")
LAT_FILE = Path("data/metadata/wrf_d02_lat.json")
LON_FILE = Path("data/metadata/wrf_d02_lon.json")
TRACK_FILE = Path("data/bigua_track_track_WRF.csv")
OUTPUT_FILE = Path("data/WRF_d02_bigua_LEC.nc")

VARS_NEEDED = ["t", "ght", "omega", "u", "v"]

print("=" * 70)
print("PREPARAÇÃO DO ARQUIVO WRF PARA O LORENZCYCLETOOLKIT (com georreferência)")
print("=" * 70)

for f in (INPUT_FILE, LAT_FILE, LON_FILE):
    if not f.exists():
        print(f"\n✗ ERRO: Arquivo não encontrado: {f}")
        exit(1)

print(f"\n[1] Carregando: {INPUT_FILE} ({INPUT_FILE.stat().st_size / 1e9:.2f} GB)")
ds = xr.open_dataset(INPUT_FILE)

print(f"\n[2] Carregando coordenadas reais de {LAT_FILE.name} / {LON_FILE.name}")
lat_values = np.array(json.loads(LAT_FILE.read_text()))
lon_values = np.array(json.loads(LON_FILE.read_text()))
print(f"    Lat: {len(lat_values)} valores, [{lat_values.min():.4f}, {lat_values.max():.4f}]°")
print(f"    Lon: {len(lon_values)} valores, [{lon_values.min():.4f}, {lon_values.max():.4f}]°")

n_south_north = ds.dims["south_north"]
n_east_west = ds.dims["east_west"]
if len(lat_values) != n_south_north or len(lon_values) != n_east_west:
    print(f"\n✗ ERRO: Dimensões incompatíveis — south_north={n_south_north} "
          f"(lat tem {len(lat_values)}), east_west={n_east_west} (lon tem {len(lon_values)})")
    exit(1)
print("    ✓ Dimensões conferem com south_north/east_west do arquivo WRF")

missing = [v for v in VARS_NEEDED if v not in ds.data_vars]
if missing:
    print(f"\n✗ Variáveis ausentes no arquivo de entrada: {missing}")
    exit(1)

print(f"\n[3] Selecionando variáveis: {VARS_NEEDED}")
print(f"    Variáveis descartadas: {[v for v in ds.data_vars if v not in VARS_NEEDED]}")
ds_reduced = ds[VARS_NEEDED]

print(f"\n[4] Aplicando georreferência real (south_north/east_west → lat/lon)")
ds_reduced = ds_reduced.assign_coords(south_north=lat_values, east_west=lon_values)
ds_reduced = ds_reduced.rename({"south_north": "lat", "east_west": "lon"})
ds_reduced["lat"].attrs = {"standard_name": "latitude", "long_name": "latitude", "units": "degrees_north", "axis": "Y"}
ds_reduced["lon"].attrs = {"standard_name": "longitude", "long_name": "longitude", "units": "degrees_east", "axis": "X"}

print(f"\n[4b] Convertendo 'time' de string para datetime64 (era: {ds_reduced.coords['time'].dtype})")
time_values = pd.to_datetime(ds_reduced.coords["time"].values)
ds_reduced = ds_reduced.assign_coords(time=time_values)
print(f"     Novo dtype: {ds_reduced.coords['time'].dtype}")

print(f"\n[4c] Removendo spin-up inicial (sem ponto de track correspondente)")
if not TRACK_FILE.exists():
    print(f"    ✗ ERRO: Arquivo não encontrado: {TRACK_FILE}")
    exit(1)
track_start = pd.to_datetime(pd.read_csv(TRACK_FILE)["time"]).min()
n_before = ds_reduced.dims["time"]
ds_reduced = ds_reduced.sel(time=slice(track_start, None))
n_after = ds_reduced.dims["time"]
print(f"    Início do track: {track_start}")
print(f"    Time steps: {n_before} → {n_after} ({n_before - n_after} removidos)")

print(f"\n[5] Coordenadas finais:")
for coord_name in ds_reduced.coords:
    coord = ds_reduced.coords[coord_name]
    print(f"    {coord_name}: {coord.shape}", end="")
    if coord.dtype != object:
        print(f"  range=[{float(coord.min()):.4f}, {float(coord.max()):.4f}]")
    else:
        print()

encoding = {var: {"zlib": True, "complevel": 4} for var in VARS_NEEDED}

print(f"\n[6] Salvando arquivo corrigido em: {OUTPUT_FILE}")
ds_reduced.to_netcdf(OUTPUT_FILE, encoding=encoding)

ds.close()
ds_reduced.close()

print(f"\n✓ Arquivo salvo: {OUTPUT_FILE} ({OUTPUT_FILE.stat().st_size / 1e9:.2f} GB)")
print(f"  Redução: {INPUT_FILE.stat().st_size / 1e9:.2f} GB → {OUTPUT_FILE.stat().st_size / 1e9:.2f} GB")
print("\n✓ Script concluído!")
print("\nPróximo passo: python scripts/exploratory/inspect_structure_wrf.py")
print("               (regenera namelist_WRF_bigua usando lat/lon reais)")
