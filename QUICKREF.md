# Quick Reference — Ciclone Biguá

**Última atualização**: 2026-08-03

---

## 🚀 Início Rápido

### Pré-requisitos
```bash
conda activate bigua  # ou criar: conda env create -f environment.yml
python scripts/exploratory/test_imports.py
```

### Execução
```bash
# Automática (WRF + ERA5 em sequência)
bash scripts/exploratory/quickstart.sh
```

Ver `scripts/exploratory/README.md` para execução manual passo-a-passo.

---

## 📂 Estrutura de Arquivos

```
bigua_analysis/
├── README.md                        # Visão geral do projeto
├── SCIENTIFIC_NOTES.md              # Registro científico
├── QUICKREF.md                      # Este arquivo
├── CHANGES_2026-08-03.md            # Histórico da correção ERA5 vs WRF
├── environment.yml
│
├── data/
│   ├── WRF_d02_bigua_LEC.nc         # WRF corrigido: t/ght/omega/u/v + lat/lon reais (5.3 GB)
│   ├── WRF_d02_bigua.nc             # WRF bruto: 10 variáveis, sem georreferência (18.2 GB)
│   ├── ERA5_d02_bigua_LCT.nc        # Reanalysis ERA5 (condição de contorno)
│   ├── bigua_track_track_ERA.csv    # Trajetória do ciclone (sep=";")
│   ├── README.md
│   └── metadata/
│       ├── WRF_bigua_structure.json
│       ├── ERA5_bigua_structure.json
│       ├── wrf_d02_lat.json / wrf_d02_lon.json    # Coordenadas reais recuperadas
│       └── wrf_d02_latlon_download.json           # Proveniência
│
├── scripts/
│   ├── exploratory/
│   │   ├── README.md                    # Guia completo (LEIA ISTO!)
│   │   ├── quickstart.sh                # Executa tudo (WRF + ERA5)
│   │   ├── test_imports.py
│   │   ├── inspect_structure_wrf.py     # Estrutura WRF + gera namelist LEC
│   │   ├── inspect_structure_era5.py    # Estrutura ERA5 + gera namelist LEC
│   │   ├── explore_data_wrf.py
│   │   ├── explore_data_era5.py
│   │   ├── plot_basic_fields_wrf.py     # Mapas WRF (projeção cartográfica)
│   │   ├── plot_basic_fields_era5.py    # Mapas ERA5 (projeção cartográfica)
│   │   └── track_viewer_era5.py         # Track sobre domínio ERA5
│   ├── analysis_01_preprocessing/
│   │   └── prepare_wrf_for_lec.py       # Gera WRF_d02_bigua_LEC.nc (reduz vars + georreferencia)
│   ├── main/
│   └── utils/
│       ├── utils_lec.py
│       └── namelist_writer.py           # Gera namelist no formato do LEC
│
├── figures/exploratory/
│   ├── wrf_basic_fields_{1000,850,500,250}hPa.png
│   ├── era5_basic_fields_{1000,850,500,250}hPa.png
│   └── era5_track_overview.png
│
└── results/
```

---

## Georreferência do WRF (resolvido em 2026-08-03)

O arquivo bruto `WRF_d02_bigua.nc` havia perdido lat/lon durante processamento com CDO, ficando só com índices de grade. As coordenadas reais (786 lat × 879 lon) foram recuperadas e aplicadas via `prepare_wrf_for_lec.py`, gerando `WRF_d02_bigua_LEC.nc` — domínio lat [-39.47°, -18.87°], lon [-61.20°, -34.58°], praticamente o mesmo do ERA5, em resolução muito maior.

Todos os scripts exploratórios e o `namelist_WRF_bigua` já usam o arquivo corrigido, com lat/lon reais em graus.

---

## 🔗 Namelists para o LorenzCycleToolkit

Gerados automaticamente pelos scripts `inspect_structure_*.py`:

- `../LorenzCycleToolkit/inputs/namelist_WRF_bigua`
- `../LorenzCycleToolkit/inputs/namelist_ERA5_bigua`

Para usar, copie o desejado para `namelist` (nome lido por padrão pelo toolkit):
```bash
cp ../LorenzCycleToolkit/inputs/namelist_ERA5_bigua ../LorenzCycleToolkit/inputs/namelist
```

---

## 📚 Documentação

- **README.md** — Visão geral, objetivos científicos, datasets
- **SCIENTIFIC_NOTES.md** — Equações, metodologia, hipóteses, resultados
- **data/README.md** — Descrição de dados
- **scripts/exploratory/README.md** — Guia detalhado de cada script
- **CHANGES_2026-08-03.md** — Correção ERA5 vs WRF

---

## 📋 Checklist — Próximas Ações

- [x] Download do arquivo WRF
- [x] Inspeção de estrutura (WRF + ERA5) e geração de namelists
- [x] Mapas exploratórios (WRF + ERA5)
- [x] Resolver georreferência real do WRF
- [x] Gerar arquivo WRF "limpo" (apenas u, v, t, omega, ght) com lat/lon corretos
- [ ] Rodar LorenzCycleToolkit com namelist_ERA5_bigua e/ou namelist_WRF_bigua
- [ ] Implementar pré-processamento (domínio centrado no ciclone, ±15° do track)
- [ ] Decomposição zonal-eddy e termos do LEC
