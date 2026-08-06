"""
Script: Preparação dos Tracks (ERA5 e WRF) para o Cyclophaser
Objetivo: Extrair, de cada track bruto, apenas as colunas time e
min_max_zeta_850, salvando versões reduzidas com sufixo _cyclophaser.
Autor: Danilo Couto de Souza
Data: 2026-08-06

- ERA5: coluna min_max_zeta_850 já existe, apenas seleciona time e a coluna.
- WRF: coluna vort850 é renomeada para min_max_zeta_850.
Formato de saída: delimitador ';', colunas time;min_max_zeta_850.
"""

from pathlib import Path

import pandas as pd

ERA_INPUT = Path("data/bigua_track_track_ERA.csv")
ERA_OUTPUT = Path("data/bigua_track_track_ERA_cyclophaser.csv")

WRF_INPUT = Path("data/bigua_track_track_WRF.csv")
WRF_OUTPUT = Path("data/bigua_track_track_WRF_cyclophaser.csv")

print("=" * 70)
print("PREPARAÇÃO DOS TRACKS PARA O CYCLOPHASER")
print("=" * 70)

print(f"\n[1] ERA5: carregando {ERA_INPUT}")
era = pd.read_csv(ERA_INPUT, sep=";")
era_out = era[["time", "min_max_zeta_850"]].copy()
era_out.to_csv(ERA_OUTPUT, sep=";", index=False)
print(f"    Salvo: {ERA_OUTPUT} ({len(era_out)} pontos)")

print(f"\n[2] WRF: carregando {WRF_INPUT}")
wrf = pd.read_csv(WRF_INPUT)
wrf_out = wrf[["time", "vort850"]].rename(columns={"vort850": "min_max_zeta_850"})
wrf_out.to_csv(WRF_OUTPUT, sep=";", index=False)
print(f"    Salvo: {WRF_OUTPUT} ({len(wrf_out)} pontos)")

print("\n✓ Script concluído!")
