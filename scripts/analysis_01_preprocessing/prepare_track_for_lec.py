"""
Script: Preparação do Track do Ciclone (WRF) para o LorenzCycleToolkit
Objetivo: Extrair apenas a posição corrigida (lat_corrigida, lon_corrigida)
do track bruto rastreado no WRF e salvar no formato exigido pelo LEC.
Autor: Danilo Couto de Souza
Data: 2026-08-03

Formato exigido pelo LorenzCycleToolkit (src/utils/validation.py):
- Delimitador ';'
- Colunas obrigatórias: time, Lat, Lon
- Formato de data: YYYY-MM-DD-HHMM (ex. 2005-08-08-0000)

O track trunca no último instante disponível em data/WRF_d02_bigua_LEC.nc
(o LEC rejeita track que se estenda além do fim dos dados).
"""

from pathlib import Path

import pandas as pd
import xarray as xr

INPUT_FILE = Path("data/bigua_track_track_WRF.csv")
WRF_FILE = Path("data/WRF_d02_bigua_LEC.nc")
OUTPUT_FILE = Path("data/bigua_track_WRF_LEC.csv")

print("=" * 70)
print("PREPARAÇÃO DO TRACK WRF PARA O LORENZCYCLETOOLKIT")
print("=" * 70)

if not INPUT_FILE.exists():
    print(f"\n✗ ERRO: Arquivo não encontrado: {INPUT_FILE}")
    exit(1)
if not WRF_FILE.exists():
    print(f"\n✗ ERRO: Arquivo não encontrado: {WRF_FILE}")
    print("  Execute primeiro: python scripts/analysis_01_preprocessing/prepare_wrf_for_lec.py")
    exit(1)

print(f"\n[1] Carregando: {INPUT_FILE}")
track = pd.read_csv(INPUT_FILE)
print(f"    Colunas: {list(track.columns)}")
print(f"    Número de pontos: {len(track)}")

required = ["time", "lat_corrigida", "lon_corrigida"]
missing = [c for c in required if c not in track.columns]
if missing:
    print(f"\n✗ ERRO: Colunas ausentes: {missing}")
    exit(1)

print(f"\n[2] Selecionando apenas campos corrigidos: lat_corrigida, lon_corrigida")
track_lec = track[["time", "lat_corrigida", "lon_corrigida"]].copy()
track_lec.columns = ["time", "Lat", "Lon"]
track_lec["time"] = pd.to_datetime(track_lec["time"])

print(f"\n[3] Truncando track no fim dos dados WRF ({WRF_FILE.name})")
with xr.open_dataset(WRF_FILE) as ds:
    data_end = pd.Timestamp(ds.coords["time"].max().values)
n_before = len(track_lec)
track_lec = track_lec[track_lec["time"] <= data_end]
n_after = len(track_lec)
print(f"    Fim dos dados: {data_end}")
print(f"    Pontos do track: {n_before} → {n_after} ({n_before - n_after} removidos)")

print(f"\n[4] Convertendo formato de data para YYYY-MM-DD-HHMM")
track_lec["time"] = track_lec["time"].dt.strftime("%Y-%m-%d-%H%M")

print(f"\n[5] Salvando: {OUTPUT_FILE}")
track_lec.to_csv(OUTPUT_FILE, sep=";", index=False)

print(f"\n  Últimas linhas:")
print(track_lec.tail().to_string(index=False))

print(f"\n✓ Arquivo salvo: {OUTPUT_FILE} ({len(track_lec)} pontos)")
print("\n✓ Script concluído!")
print("\nPróximo passo: copiar para o LEC, ex.:")
print(f"  cp {OUTPUT_FILE} ../LorenzCycleToolkit/inputs/track_WRF_bigua")
