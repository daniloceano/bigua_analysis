"""
Script: Inspeção Detalhada da Estrutura do Arquivo WRF
Objetivo: Investigar a estrutura do NetCDF do WRF (corrigido, com
georreferência real) e gerar o namelist do LEC
Autor: Danilo Couto de Souza
Data: 2026-08-03 (atualizado após recuperação da georreferência real)

Este script inspeciona data/WRF_d02_bigua_LEC.nc — o arquivo corrigido
gerado por scripts/analysis_01_preprocessing/prepare_wrf_for_lec.py, que
contém apenas as variáveis necessárias para o LEC (t, ght, omega, u, v)
com coordenadas lat/lon reais (recuperadas separadamente, ver
data/metadata/wrf_d02_latlon_download.json — o arquivo bruto
data/WRF_d02_bigua.nc perdeu a georreferência durante processamento com CDO).
"""

import sys
import json
from pathlib import Path

import xarray as xr
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "utils"))
from namelist_writer import write_lec_namelist

MODEL_NAME = "WRF_bigua"

DATA_FILE = Path("data/WRF_d02_bigua_LEC.nc")
METADATA_FILE = Path(f"data/metadata/{MODEL_NAME}_structure.json")
METADATA_FILE.parent.mkdir(parents=True, exist_ok=True)

print("=" * 80)
print(f"INSPEÇÃO DETALHADA — ESTRUTURA DO ARQUIVO {MODEL_NAME}")
print("=" * 80)

if not DATA_FILE.exists():
    print(f"\n✗ ERRO: Arquivo não encontrado: {DATA_FILE}")
    print("  Execute primeiro: python scripts/analysis_01_preprocessing/prepare_wrf_for_lec.py")
    exit(1)

print(f"\n[1] Carregando arquivo WRF (corrigido)...")
print(f"    Arquivo: {DATA_FILE}")
print(f"    Tamanho: {DATA_FILE.stat().st_size / 1e9:.2f} GB")

ds = xr.open_dataset(DATA_FILE)
print("    ✓ Arquivo carregado com sucesso!")

metadata = {"model": MODEL_NAME, "source_file": str(DATA_FILE)}

print(f"\n[2] DIMENSÕES")
print("-" * 80)
for dim_name, dim_size in ds.dims.items():
    print(f"  {dim_name:20s}: {dim_size}")
metadata["dims"] = dict(ds.dims)

print(f"\n[3] COORDENADAS")
print("-" * 80)
for coord_name in sorted(ds.coords):
    coord = ds.coords[coord_name]
    print(f"  {coord_name:20s}: shape={coord.shape}, dtype={coord.dtype}")
    if coord.dtype != object and coord.size:
        print(f"      range=[{float(coord.min().values):.4f}, {float(coord.max().values):.4f}]")

print(f"\n[4] VARIÁVEIS")
print("-" * 80)
vars_info = {}
for var_name in sorted(ds.data_vars):
    var = ds[var_name]
    stats = {}
    try:
        stats = {
            "min": float(var.min().values),
            "max": float(var.max().values),
            "mean": float(var.mean().values),
        }
    except Exception:
        pass
    print(f"  {var_name:12s}: shape={var.shape}  {stats}")
    vars_info[var_name] = {"shape": list(var.shape), **stats}
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
levels = ds.coords["levels"].values
print(f"  {len(levels)} níveis (hPa): {[int(l) for l in levels]}")
metadata["levels_hpa"] = [float(l) for l in levels]

print(f"\n[7] GEORREFERÊNCIA (lat/lon)")
print("-" * 80)
lat, lon = ds.coords["lat"].values, ds.coords["lon"].values
print(f"  Lat: [{lat.min():.4f}, {lat.max():.4f}]°  |  Lon: [{lon.min():.4f}, {lon.max():.4f}]°")
print("  ✓ Coordenadas geográficas reais aplicadas (ver data/metadata/wrf_d02_latlon_download.json)")
metadata["has_real_geolocation"] = True
metadata["lat_range"] = [float(lat.min()), float(lat.max())]
metadata["lon_range"] = [float(lon.min()), float(lon.max())]

# --- Geração do namelist para o LEC ---
print(f"\n[8] GERANDO NAMELIST PARA O LORENZCYCLETOOLKIT")
print("-" * 80)

mapping = {
    "temperature_var": "t", "temperature_units": "K",
    "geopotential_var": "ght", "geopotential_units": "m",
    "omega_var": "omega", "omega_units": "Pa/s",
    "u_var": "u", "u_units": "m/s",
    "v_var": "v", "v_units": "m/s",
    "lon_var": "lon",
    "lat_var": "lat",
    "time_var": "time",
    "level_var": "levels",
}

try:
    namelist_path = write_lec_namelist(MODEL_NAME, mapping, geopotential_kind="geopotential_height")
    print(f"  ✓ Namelist salvo em: {namelist_path}")
    print(f"  ✓ Longitude='lon' e Latitude='lat' já em graus reais — box_limits do LEC")
    print(f"    pode ser especificado normalmente em graus (ex. buffer de ±15° em torno do track).")
except (KeyError, ValueError, OSError) as e:
    print(f"  ✗ Não foi possível gerar o namelist: {e}")
    namelist_path = None

metadata["namelist_generated"] = str(namelist_path) if namelist_path else None

with open(METADATA_FILE, "w") as f:
    json.dump(metadata, f, indent=2, default=str)
print(f"\n✓ Metadados salvos em: {METADATA_FILE}")

ds.close()
print("\n✓ Inspeção concluída!")
