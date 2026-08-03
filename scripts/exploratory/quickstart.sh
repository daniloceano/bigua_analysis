#!/bin/bash
# Quickstart: Executa sequência recomendada de scripts exploratórios
# para ambos os datasets — WRF (simulação) e ERA5 (condição de contorno).
# Uso: bash scripts/exploratory/quickstart.sh

set -e

echo "=========================================="
echo "QUICKSTART — Ciclone Biguá (WRF + ERA5)"
echo "=========================================="

if [ ! -f "data/ERA5_d02_bigua_LCT.nc" ]; then
    echo ""
    echo "✗ ERRO: Arquivo não encontrado: data/ERA5_d02_bigua_LCT.nc"
    exit 1
fi

if [ ! -f "data/WRF_d02_bigua_LEC.nc" ]; then
    if [ ! -f "data/WRF_d02_bigua.nc" ]; then
        echo ""
        echo "✗ ERRO: Nenhum arquivo WRF encontrado (nem bruto, nem corrigido)"
        exit 1
    fi
    echo ""
    echo "────────────────────────────────────────"
    echo "[WRF] Pré-processamento (gera WRF_d02_bigua_LEC.nc)"
    echo "────────────────────────────────────────"
    python scripts/analysis_01_preprocessing/prepare_wrf_for_lec.py
fi
echo ""
echo "✓ Arquivos WRF e ERA5 detectados"

echo ""
echo "────────────────────────────────────────"
echo "[WRF] Inspeção de estrutura + namelist LEC"
echo "────────────────────────────────────────"
python scripts/exploratory/inspect_structure_wrf.py

echo ""
echo "────────────────────────────────────────"
echo "[WRF] Exploração completa"
echo "────────────────────────────────────────"
python scripts/exploratory/explore_data_wrf.py

echo ""
echo "────────────────────────────────────────"
echo "[WRF] Mapas básicos"
echo "────────────────────────────────────────"
python scripts/exploratory/plot_basic_fields_wrf.py

echo ""
echo "────────────────────────────────────────"
echo "[WRF] Visualização do track do ciclone"
echo "────────────────────────────────────────"
python scripts/exploratory/track_viewer_wrf.py

echo ""
echo "────────────────────────────────────────"
echo "[WRF] Preparação do track para o LEC"
echo "────────────────────────────────────────"
python scripts/analysis_01_preprocessing/prepare_track_for_lec.py

echo ""
echo "────────────────────────────────────────"
echo "[ERA5] Inspeção de estrutura + namelist LEC"
echo "────────────────────────────────────────"
python scripts/exploratory/inspect_structure_era5.py

echo ""
echo "────────────────────────────────────────"
echo "[ERA5] Exploração completa"
echo "────────────────────────────────────────"
python scripts/exploratory/explore_data_era5.py

echo ""
echo "────────────────────────────────────────"
echo "[ERA5] Mapas básicos"
echo "────────────────────────────────────────"
python scripts/exploratory/plot_basic_fields_era5.py

echo ""
echo "────────────────────────────────────────"
echo "[ERA5] Visualização do track do ciclone"
echo "────────────────────────────────────────"
python scripts/exploratory/track_viewer_era5.py

echo ""
echo "=========================================="
echo "✓ QUICKSTART CONCLUÍDO!"
echo "=========================================="
echo ""
echo "Figuras:   figures/exploratory/{wrf,era5}_basic_fields_*.png, {wrf,era5}_track_overview.png"
echo "Metadados: data/metadata/{WRF,ERA5}_bigua_structure.json"
echo "Namelists: ../LorenzCycleToolkit/inputs/namelist_{WRF,ERA5}_bigua"
echo "Track LEC: data/bigua_track_WRF_LEC.csv"
