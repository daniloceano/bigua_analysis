# Scripts Exploratórios — Ciclone Biguá

Scripts de exploração para **dois datasets distintos**:

| Dataset | Arquivo | Papel |
|---|---|---|
| **WRF** | `data/WRF_d02_bigua_LEC.nc` | Simulação de alta resolução (domínio d02), corrigida — dado principal para o LEC |
| **ERA5** | `data/ERA5_d02_bigua_LCT.nc` | Reanalysis usada como condição de contorno do WRF — referência/comparação |

Cada script tem sufixo `_wrf` ou `_era5` indicando a qual dataset se refere. Veja `CHANGES_2026-08-03.md` na raiz do projeto para o histórico completo das correções (confusão ERA5/WRF e recuperação da georreferência).

---

## Sequência Recomendada

### Automática
```bash
bash scripts/exploratory/quickstart.sh
```

### Manual — WRF
```bash
python scripts/analysis_01_preprocessing/prepare_wrf_for_lec.py  # Gera WRF_d02_bigua_LEC.nc (1x apenas)
python scripts/exploratory/inspect_structure_wrf.py              # Estrutura + gera namelist LEC
python scripts/exploratory/explore_data_wrf.py                    # Exploração completa
python scripts/exploratory/plot_basic_fields_wrf.py               # Mapas (projeção cartográfica)
```

### Manual — ERA5
```bash
python scripts/exploratory/inspect_structure_era5.py   # Estrutura + gera namelist LEC
python scripts/exploratory/explore_data_era5.py        # Exploração completa
python scripts/exploratory/plot_basic_fields_era5.py   # Mapas (projeção cartográfica)
python scripts/exploratory/track_viewer_era5.py        # Track sobre domínio ERA5
```

---

## Georreferência do WRF — Histórico

O arquivo bruto `WRF_d02_bigua.nc` perdeu lat/lon durante processamento com CDO (`mergetime`), ficando apenas com índices de grade (`south_north` 0–785, `east_west` 0–878). As coordenadas reais do domínio d02 foram recuperadas separadamente (arrays de 786 e 879 pontos, ver `data/metadata/wrf_d02_latlon_download.json`) e aplicadas por `scripts/analysis_01_preprocessing/prepare_wrf_for_lec.py`, que gera o arquivo corrigido `data/WRF_d02_bigua_LEC.nc`:

- Domínio: lat [-39.47°, -18.87°], lon [-61.20°, -34.58°] — praticamente o mesmo domínio do ERA5, em resolução muito maior (786×879 vs 82×106)
- Apenas as 5 variáveis necessárias para o LEC: `t`, `ght`, `omega`, `u`, `v`

**Todos os scripts exploratórios de WRF já usam o arquivo corrigido** (`WRF_d02_bigua_LEC.nc`), não o bruto.

---

## Track para o LorenzCycleToolkit

`scripts/analysis_01_preprocessing/prepare_track_for_lec.py` converte
`data/bigua_track_track_WRF.csv` (posição bruta + corrigida) para o formato
exigido pelo LEC (`time;Lat;Lon`, data `YYYY-MM-DD-HHMM`), usando apenas a
posição **corrigida**. Gera `data/bigua_track_WRF_LEC.csv`:
```bash
python scripts/analysis_01_preprocessing/prepare_track_for_lec.py
cp data/bigua_track_WRF_LEC.csv ../LorenzCycleToolkit/inputs/track_WRF_bigua
```

## Namelists Gerados para o LorenzCycleToolkit

Os scripts `inspect_structure_*.py` geram automaticamente o namelist no formato esperado pelo LEC (`scripts/utils/namelist_writer.py`), ambos com lat/lon reais em graus:

- `../LorenzCycleToolkit/inputs/namelist_WRF_bigua`
- `../LorenzCycleToolkit/inputs/namelist_ERA5_bigua`

Para rodar o LEC com um desses, copie o arquivo desejado para `inputs/namelist` (nome que o toolkit lê por padrão):
```bash
cp ../LorenzCycleToolkit/inputs/namelist_ERA5_bigua ../LorenzCycleToolkit/inputs/namelist
```

O `box_limits` do LEC pode ser especificado normalmente em graus para ambos os datasets (ex. buffer de ±15° em torno do track do ciclone).

---

## Descrição dos Scripts

### `inspect_structure_wrf.py` / `inspect_structure_era5.py`
Inspeção detalhada: dimensões, coordenadas, variáveis, período, níveis verticais. Gera:
- Metadados JSON em `data/metadata/{WRF,ERA5}_bigua_structure.json`
- Namelist do LEC em `../LorenzCycleToolkit/inputs/namelist_{WRF,ERA5}_bigua`

### `explore_data_wrf.py` / `explore_data_era5.py`
Exploração textual completa (relatório no console), incluindo leitura do track do ciclone.

### `plot_basic_fields_wrf.py` / `plot_basic_fields_era5.py`
Mapas de temperatura, vento e geopotencial/altura geopotencial em 1000, 850, 500, 250 hPa, com projeção `ccrs.PlateCarree()`, costa, fronteiras e vetores de vento.

Saída: `figures/exploratory/{wrf,era5}_basic_fields_<nível>hPa.png`

### `track_viewer_era5.py`
Plota a trajetória do ciclone (`data/bigua_track_track_ERA.csv`) sobre o domínio ERA5.
Saída: `figures/exploratory/era5_track_overview.png`

### `track_viewer_wrf.py`
Plota a trajetória do ciclone rastreada no WRF (`data/bigua_track_track_WRF.csv`),
mostrando posição bruta e corrigida (mínimo de vorticidade 850 hPa), sobre o domínio WRF.
Saída: `figures/exploratory/wrf_track_overview.png`

### `test_imports.py`
Verifica se as dependências (xarray, cartopy, etc.) estão instaladas.

---

## Troubleshooting

| Problema | Solução |
|---|---|
| "Arquivo não encontrado: WRF_d02_bigua_LEC.nc" | Rode primeiro `python scripts/analysis_01_preprocessing/prepare_wrf_for_lec.py` |
| Erro ao ler track (`;` vs `,`) | O CSV usa `;` como separador — os scripts já usam `pd.read_csv(..., sep=";")` |
| Namelist não gerado | Ver mensagem de erro — `write_lec_namelist` valida chaves obrigatórias no mapping |
