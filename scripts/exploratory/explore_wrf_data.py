"""
Script: Exploração Inicial dos Dados WRF do Ciclone Biguá
Objetivo: Inspecionar estrutura do arquivo NetCDF (variáveis, dimensões, níveis, período)
Data: 2026-07-22
Autor: Danilo Couto de Souza
"""

import xarray as xr
import pandas as pd
from pathlib import Path

# --- Paths ---
DATA_FILE = Path("data/ERA5_d02_bigua_LCT.nc")
TRACK_FILE = Path("data/bigua_track_track.csv")

print("=" * 70)
print("EXPLORAÇÃO INICIAL — CICLONE BIGUÁ")
print("=" * 70)

# --- 1. Carregar arquivo WRF ---
print("\n[1] Carregando arquivo WRF...")
print(f"    Arquivo: {DATA_FILE}")

try:
    ds = xr.open_dataset(DATA_FILE)
    print("    ✓ Arquivo carregado com sucesso!\n")
except FileNotFoundError:
    print(f"    ✗ Erro: Arquivo {DATA_FILE} não encontrado!")
    exit(1)

# --- 2. Informações básicas do dataset ---
print("\n[2] INFORMAÇÕES GERAIS DO DATASET")
print("-" * 70)
print(f"Tamanho total em memória: {ds.nbytes / 1e9:.2f} GB")
print(f"Número de variáveis: {len(ds.data_vars)}")

# --- 3. Dimensões ---
print("\n[3] DIMENSÕES")
print("-" * 70)
for dim_name, dim_size in ds.dims.items():
    print(f"  {dim_name:20s}: {dim_size}")

# --- 4. Coordenadas ---
print("\n[4] COORDENADAS")
print("-" * 70)
for coord_name in ds.coords:
    coord = ds.coords[coord_name]
    print(f"  {coord_name:20s}: shape={coord.shape}, dtype={coord.dtype}")
    if coord.size < 50:  # Mostrar valores se for pequeno
        print(f"      valores: {coord.values}")
    else:
        # Verificar se é numérico antes de formatar
        try:
            print(f"      min={coord.min().values:.2f}, max={coord.max().values:.2f}")
        except (ValueError, TypeError):
            print(f"      min={coord.min().values}, max={coord.max().values}")

# --- 5. Variáveis disponíveis ---
print("\n[5] VARIÁVEIS DISPONÍVEIS")
print("-" * 70)
for var_name in ds.data_vars:
    var = ds[var_name]
    print(f"  {var_name:20s}: shape={var.shape}, dtype={var.dtype}")
    if "long_name" in var.attrs:
        print(f"      {var.attrs['long_name']}")
    if "units" in var.attrs:
        print(f"      unidades: {var.attrs['units']}")
    print()

# --- 6. Atributos globais ---
print("\n[6] ATRIBUTOS GLOBAIS")
print("-" * 70)
for attr_name, attr_value in ds.attrs.items():
    print(f"  {attr_name}: {attr_value}")

# --- 7. Verificar níveis de pressão (se existir coordenada 'pressure' ou 'level') ---
print("\n[7] NÍVEIS VERTICAIS")
print("-" * 70)
if "pressure" in ds.coords or "lev" in ds.coords or "level" in ds.coords:
    level_name = None
    if "pressure" in ds.coords:
        level_name = "pressure"
    elif "lev" in ds.coords:
        level_name = "lev"
    elif "level" in ds.coords:
        level_name = "level"
    
    if level_name:
        levels = ds.coords[level_name].values
        print(f"  Coordenada: {level_name}")
        print(f"  Número de níveis: {len(levels)}")
        print(f"  Níveis (hPa ou índice): {levels}")
else:
    print("  Nenhuma coordenada vertical explícita identificada.")
    print("  Verificar se há variável 'P' ou 'pressure' no dataset.")

# --- 8. Período temporal ---
print("\n[8] PERÍODO TEMPORAL")
print("-" * 70)
if "time" in ds.coords or "Time" in ds.coords:
    time_coord = ds.coords.get("time", ds.coords.get("Time"))
    time_values = pd.to_datetime(time_coord.values)
    print(f"  Início: {time_values[0]}")
    print(f"  Fim:    {time_values[-1]}")
    print(f"  Número de time steps: {len(time_values)}")
    if len(time_values) > 1:
        dt = time_values[1] - time_values[0]
        print(f"  Resolução temporal: {dt}")
else:
    print("  Nenhuma coordenada temporal identificada.")

# --- 9. Carregar track do ciclone ---
print("\n[9] TRACK DO CICLONE")
print("-" * 70)
if TRACK_FILE.exists():
    try:
        track = pd.read_csv(TRACK_FILE)
        print(f"  ✓ Track carregado: {TRACK_FILE}")
        print(f"  Colunas: {list(track.columns)}")
        print(f"  Número de pontos: {len(track)}")
        print(f"\n  Primeiras linhas:")
        print(track.head())
    except Exception as e:
        print(f"  ✗ Erro ao carregar track: {e}")
else:
    print(f"  ✗ Arquivo {TRACK_FILE} não encontrado.")

# --- 10. Resumo e recomendações ---
print("\n" + "=" * 70)
print("RESUMO E PRÓXIMOS PASSOS")
print("=" * 70)
print("""
1. Verificar quais variáveis correspondem a:
   - Componentes do vento: U, V, W ou OMEGA
   - Temperatura: T, TK, ou theta
   - Geopotencial: Z, GHT, ou PH
   
2. Confirmar níveis de pressão disponíveis (idealmente 1000, 850, 500, 250 hPa)

3. Se necessário, usar wrf-python para extrair variáveis diagnósticas:
   - from wrf import getvar, interplevel
   
4. Executar script de plots básicos:
   python scripts/exploratory/plot_basic_fields.py
""")

# --- Fechar dataset ---
ds.close()
print("\n✓ Exploração concluída!")
