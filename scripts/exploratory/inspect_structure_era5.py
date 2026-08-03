"""
Script: Inspeção Detalhada da Estrutura do Arquivo ERA5
Objetivo: Investigar a estrutura do NetCDF do ERA5 e gerar o namelist do LEC
Autor: Danilo Couto de Souza
Data: 2026-08-03

Nota: Este arquivo (data/ERA5_d02_bigua_LCT.nc) é reanalysis ERA5 usado como
condição de contorno para a simulação WRF do ciclone Biguá — NÃO é a saída
do modelo WRF (ver CHANGES_2026-08-03.md para o histórico dessa correção).
Ao contrário do WRF, o ERA5 possui coordenadas geográficas reais (lat/lon
em graus), o que permite rodar o LEC com box_limits especificados em graus.
"""

import json
from pathlib import Path
import sys

import xarray as xr
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "utils"))
from namelist_writer import write_lec_namelist

MODEL_NAME = "ERA5_bigua"

DATA_FILE = Path("data/ERA5_d02_bigua_LCT.nc")
METADATA_FILE = Path(f"data/metadata/{MODEL_NAME}_structure.json")
METADATA_FILE.parent.mkdir(parents=True, exist_ok=True)

print("=" * 80)
print(f"INSPEÇÃO DETALHADA — ESTRUTURA DO ARQUIVO {MODEL_NAME}")
print("=" * 80)

if not DATA_FILE.exists():
    print(f"\n✗ ERRO: Arquivo não encontrado: {DATA_FILE}")
    exit(1)

print(f"\n[1] Carregando arquivo ERA5...")
print(f"    Arquivo: {DATA_FILE}")
print(f"    Tamanho: {DATA_FILE.stat().st_size / 1e9:.2f} GB")

ds = xr.open_dataset(DATA_FILE)
print("    ✓ Arquivo carregado com sucesso!")

metadata = {"model": MODEL_NAME}

print(f"\n[2] DIMENSÕES")
print("-" * 80)
for dim_name, dim_size in ds.dims.items():
    print(f"  {dim_name:20s}: {dim_size}")
metadata["dims"] = dict(ds.dims)

print(f"\n[3] COORDENADAS")
print("-" * 80)
for coord_name in sorted(ds.coords):
    coord = ds.coords[coord_name]
    print(f"  {coord_name:20s}: shape={coord.shape}, dtype={coord.dtype}, units={coord.attrs.get('units', 'N/A')}")
    if coord.dtype != object and coord.size:
        print(f"      range=[{float(coord.min().values):.4f}, {float(coord.max().values):.4f}]")

print(f"\n[4] VARIÁVEIS")
print("-" * 80)
vars_info = {}
for var_name in sorted(ds.data_vars):
    var = ds[var_name]
    print(f"  {var_name:8s}: shape={var.shape}  standard_name={var.attrs.get('standard_name', 'N/A'):25s}  units={var.attrs.get('units', 'N/A')}")
    vars_info[var_name] = {
        "shape": list(var.shape),
        "standard_name": var.attrs.get("standard_name", ""),
        "units": var.attrs.get("units", ""),
    }
metadata["variables"] = vars_info

print(f"\n[5] PERÍODO TEMPORAL")
print("-" * 80)
time_values = pd.to_datetime(ds.coords["time"].values)
print(f"  Início: {time_values[0]}  |  Fim: {time_values[-1]}  |  N steps: {len(time_values)}")
metadata["temporal"] = {
    "start": str(time_values[0]), "end": str(time_values[-1]), "n_steps": len(time_values),
}

print(f"\n[6] NÍVEIS VERTICAIS")
print("-" * 80)
plev = ds.coords["plev"].values
print(f"  {len(plev)} níveis ({ds.coords['plev'].attrs.get('units', 'Pa')}): {plev}")
metadata["levels_pa"] = [float(l) for l in plev]

print(f"\n[7] GEORREFERÊNCIA (lat/lon)")
print("-" * 80)
lat, lon = ds.coords["lat"].values, ds.coords["lon"].values
print(f"  Lat: [{lat.min():.2f}, {lat.max():.2f}]°  |  Lon: [{lon.min():.2f}, {lon.max():.2f}]°")
print("  ✓ Coordenadas geográficas reais disponíveis — box_limits do LEC pode usar graus.")
metadata["has_real_geolocation"] = True
metadata["lat_range"] = [float(lat.min()), float(lat.max())]
metadata["lon_range"] = [float(lon.min()), float(lon.max())]

# --- Geração do namelist para o LEC ---
print(f"\n[8] GERANDO NAMELIST PARA O LORENZCYCLETOOLKIT")
print("-" * 80)

mapping = {
    "temperature_var": "t", "temperature_units": "K",
    "geopotential_var": "z", "geopotential_units": "m**2/s**2",
    "omega_var": "w", "omega_units": "Pa/s",
    "u_var": "u", "u_units": "m/s",
    "v_var": "v", "v_units": "m/s",
    "lon_var": "lon",
    "lat_var": "lat",
    "time_var": "time",
    "level_var": "plev",
}

try:
    namelist_path = write_lec_namelist(MODEL_NAME, mapping, geopotential_kind="geopotential")
    print(f"  ✓ Namelist salvo em: {namelist_path}")
except (KeyError, ValueError, OSError) as e:
    print(f"  ✗ Não foi possível gerar o namelist: {e}")
    namelist_path = None

metadata["namelist_generated"] = str(namelist_path) if namelist_path else None

with open(METADATA_FILE, "w") as f:
    json.dump(metadata, f, indent=2, default=str)
print(f"\n✓ Metadados salvos em: {METADATA_FILE}")

ds.close()
print("\n✓ Inspeção concluída!")
