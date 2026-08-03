# Data Directory — Ciclone Biguá

## Histórico: ERA5 vs WRF e Georreferência (2026-08-03)

Duas correções foram feitas neste projeto (ver `CHANGES_2026-08-03.md` na raiz):

1. **Confusão ERA5 vs WRF**: `ERA5_d02_bigua_LCT.nc` é reanalysis ERA5 (condição de contorno), não a simulação WRF. O arquivo WRF correto é `WRF_d02_bigua.nc`.
2. **Georreferência ausente no WRF**: o arquivo `WRF_d02_bigua.nc` perdeu lat/lon durante processamento com CDO (`mergetime`), ficando apenas com índices de grade (`south_north`, `east_west`). As coordenadas reais foram recuperadas separadamente e aplicadas, gerando o arquivo corrigido `WRF_d02_bigua_LEC.nc`.

---

## Arquivos

### 1. WRF_d02_bigua_LEC.nc (uso recomendado para o LEC)
- **Tipo**: Simulação WRF, domínio d02, apenas variáveis necessárias para o LorenzCycleToolkit
- **Gerado por**: `scripts/analysis_01_preprocessing/prepare_wrf_for_lec.py`
- **Variáveis**: `t` (K), `ght` (altura geopotencial, m), `omega` (Pa/s), `u`, `v` (m/s)
- **Coordenadas**: `time` (25 steps, 3h), `levels` (24 níveis, 100–1000 hPa), `lat` (786 pontos, -39.47° a -18.87°), `lon` (879 pontos, -61.20° a -34.58°) — **coordenadas geográficas reais**
- **Tamanho**: ~5.3 GB (reduzido de 18.2 GB do arquivo bruto)

### 2. WRF_d02_bigua.nc (arquivo bruto, sem georreferência)
- **Tipo**: Simulação WRF, domínio d02, saída completa (10 variáveis: u, v, t, rh, ght, s, td, q, omega, vorticity)
- **Condições de contorno**: ERA5 Reanalysis
- **Período**: 2024-12-13 a 2024-12-16 (resolução 3h, 25 time steps)
- **Níveis verticais**: 24 níveis de pressão (100–1000 hPa)
- **Tamanho**: ~18.2 GB
- **⚠️ Limitação**: `south_north`/`east_west` são índices de grade (0–785/0–878), não lat/lon. Mantido como fonte bruta; use `WRF_d02_bigua_LEC.nc` para análises físicas.

### 3. bigua_track_track_ERA.csv
- **Tipo**: Track do ciclone (trajetória), separador `;`
- **Colunas**: `time`, `Lat`, `Lon`, `length`, `width`, `min_max_zeta_850`, `min_hgt_850`, `max_wind_850`
- **Número de pontos**: 25
- **Período**: 2024-12-13 12Z a 2024-12-14 12Z (fase madura)
- **Uso**: Referência para análise centrada no ciclone, extração de domínio móvel

### 3b. bigua_track_track_WRF.csv
- **Tipo**: Track do ciclone rastreado diretamente no WRF (mínimo de vorticidade em 850 hPa), separador `,`
- **Colunas**: `time`, `lat`, `lon`, `vort850` (posição bruta), `lat_corrigida`, `lon_corrigida`, `vort850_corrigido` (posição corrigida)
- **Número de pontos**: 25
- **Período**: 2024-12-13 12Z a 2024-12-16 12Z (todo o período simulado)
- **Uso**: Track de maior resolução/qualidade (posição corrigida) para centrar o domínio de análise do LEC

### 3c. bigua_track_WRF_LEC.csv
- **Tipo**: Track processado no formato exigido pelo LorenzCycleToolkit
- **Gerado por**: `scripts/analysis_01_preprocessing/prepare_track_for_lec.py`
- **Colunas**: `time;Lat;Lon` (separador `;`, data `YYYY-MM-DD-HHMM`), usando apenas a posição **corrigida** de `bigua_track_track_WRF.csv`
- **Uso**: Copiar para `../LorenzCycleToolkit/inputs/track_WRF_bigua` para rodar o LEC

### 4. ERA5_d02_bigua_LCT.nc
- **Tipo**: Reanalysis ERA5 — condição de contorno da simulação WRF (não é a simulação em si)
- **Variáveis**: `t`, `z`, `w`, `u`, `v`, `q`, `r` (nomes ERA5 padrão, com `standard_name`/`units` nos atributos)
- **Coordenadas geográficas reais**: lat [-39.25°, -19.00°], lon [-61.00°, -34.75°]
- **Período**: 2024-12-11 a 2024-12-19 (resolução horária, 216 time steps)
- **Uso**: Comparação/validação com o WRF, e como dataset alternativo para o LEC (georreferenciado desde a origem)

---

## Metadata

O subdiretório `metadata/` contém:
- `WRF_bigua_structure.json`, `ERA5_bigua_structure.json` — estrutura completa de cada dataset (gerados por `inspect_structure_{wrf,era5}.py`)
- `wrf_d02_lat.json`, `wrf_d02_lon.json` — arrays de coordenadas reais do domínio WRF d02 (recuperados separadamente)
- `wrf_d02_latlon_download.json` — proveniência do download das coordenadas

---

## Como Inspecionar os Dados

```bash
# WRF (gera namelist_WRF_bigua)
python scripts/exploratory/inspect_structure_wrf.py
python scripts/exploratory/explore_data_wrf.py
python scripts/exploratory/plot_basic_fields_wrf.py

# ERA5 (gera namelist_ERA5_bigua)
python scripts/exploratory/inspect_structure_era5.py
python scripts/exploratory/explore_data_era5.py
python scripts/exploratory/plot_basic_fields_era5.py
python scripts/exploratory/track_viewer_era5.py

# Ou tudo de uma vez:
bash scripts/exploratory/quickstart.sh
```

Ver `scripts/exploratory/README.md` para detalhes de cada script.

## Namelists para o LorenzCycleToolkit

Gerados em `../LorenzCycleToolkit/inputs/namelist_{WRF,ERA5}_bigua`, ambos com lat/lon reais em graus (box_limits do LEC pode ser especificado normalmente).
