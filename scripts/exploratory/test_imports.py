"""
Script: Teste de Dependências
Objetivo: Verificar se todos os pacotes necessários estão disponíveis
Data: 2026-08-03
Autor: Danilo Couto de Souza
"""

import sys

print("=" * 70)
print("TESTE DE DEPENDÊNCIAS")
print("=" * 70)

packages = {
    'xarray': 'Manipulação de dados NetCDF',
    'pandas': 'Análise de dados e DataFrames',
    'numpy': 'Computação numérica',
    'matplotlib': 'Plots 2D',
    'cartopy': 'Projeções cartográficas',
    'scipy': 'Funções científicas',
    'cdsapi': 'Download de dados ERA5',
}

print("\nVerificando pacotes necessários:\n")

missing = []
for package, description in packages.items():
    try:
        __import__(package)
        print(f"  ✓ {package:15s} — {description}")
    except ImportError:
        print(f"  ✗ {package:15s} — FALTA INSTALAR")
        missing.append(package)

print("\n" + "=" * 70)

if not missing:
    print("✓ TODAS AS DEPENDÊNCIAS DISPONÍVEIS!")
    print("  Scripts exploratórios devem executar corretamente.")
else:
    print(f"✗ FALTAM {len(missing)} PACOTE(S):")
    for pkg in missing:
        print(f"  - {pkg}")
    print("\n  Para instalar:")
    print(f"  conda install {' '.join(missing)}")
    print(f"  ou")
    print(f"  pip install {' '.join(missing)}")

print("=" * 70)
