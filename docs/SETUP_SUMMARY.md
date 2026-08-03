# Resumo da Estruturação — Repositório Ciclone Biguá

**Data**: 2026-07-22  
**Repositório**: `/Users/danilocoutodesouza/Documents/Programs_and_scripts/bigua_analysis`

---

## ✅ O Que Foi Realizado

### 1. Estrutura de Pastas Criada
```
bigua_analysis/
├── README.md                        # Documentação completa do projeto
├── SCIENTIFIC_NOTES.md             # Registro científico (métodos, equações, resultados)
├── environment.yml                  # Ambiente conda com dependências
├── .gitignore                       # Exclusões para git
├── data/
│   ├── README.md                    # Documentação dos dados
│   ├── ERA5_d02_bigua_LCT.nc       # Simulação WRF (1.26 GB)
│   ├── bigua_track_track.csv       # Track do ciclone
│   └── metadata/                    # Para logs de proveniência
├── scripts/
│   ├── exploratory/                 # ✓ Scripts exploratórios
│   │   ├── explore_wrf_data.py     # ✓ Inspeção do NetCDF
│   │   └── plot_basic_fields.py    # ✓ Mapas básicos
│   ├── main/                        # Para scripts finais de figuras
│   └── utils/
│       └── utils_lec.py            # ✓ Funções do Ciclo de Energia de Lorenz
├── figures/
│   ├── exploratory/                 # ✓ 4 mapas gerados
│   └── paper/                       # Para figuras finais
├── results/
│   ├── processed/                   # Para datasets intermediários
│   └── final/                       # Para resultados finais
└── docs/                            # Para PDFs e documentação exportada
```

### 2. Análise Exploratória Executada

**Script**: `explore_wrf_data.py` — ✅ Executado com sucesso

**Informações Extraídas:**
- ✓ 216 time steps horários (2024-12-11 a 2024-12-19)
- ✓ 24 níveis de pressão (100 a 1000 hPa)
- ✓ Domínio espacial: 19-39.25°S, 61-34.75°W
- ✓ Variáveis: z, t, u, v, w, q, r — **todas necessárias para LEC presentes!**
- ✓ Track do ciclone: 25 pontos identificados

### 3. Mapas Básicos Gerados

**Script**: `plot_basic_fields.py` — ✅ Executado com sucesso

**Figuras Criadas** (em `figures/exploratory/`):
1. ✓ `basic_fields_1000hPa.png` — Temperatura, vento, geopotencial em 1000 hPa
2. ✓ `basic_fields_850hPa.png` — Temperatura, vento, geopotencial em 850 hPa
3. ✓ `basic_fields_500hPa.png` — Temperatura, vento, geopotencial em 500 hPa
4. ✓ `basic_fields_250hPa.png` — Temperatura, vento, geopotencial em 250 hPa

**Time step plotado**: 2024-12-15 12:00 (meio da simulação)

### 4. Documentação Criada

- ✅ `README.md` — Contexto científico, estrutura de pastas, workflow de análise, referências
- ✅ `SCIENTIFIC_NOTES.md` — Perguntas de pesquisa, framework teórico do LEC, equações, datasets, métodos, resultados iniciais
- ✅ `data/README.md` — Descrição dos arquivos de dados
- ✅ `environment.yml` — Ambiente conda (`bigua`) com xarray, cartopy, metpy, wrf-python
- ✅ `.gitignore` — Configurado para excluir dados brutos, resultados, figuras

### 5. Código de Utilidades Preparado

**Arquivo**: `scripts/utils/utils_lec.py`

**Funções Implementadas:**
- ✓ `compute_zonal_mean()` — Média zonal
- ✓ `compute_eddy_component()` — Componente eddy (T', u', v')
- ✓ `compute_kinetic_energy_zonal()` — $K_Z$
- ✓ `compute_kinetic_energy_eddy()` — $K_E$
- ✓ `compute_potential_temperature()` — $\theta$
- ✓ `compute_static_stability()` — $\sigma$
- ✓ `compute_APE_eddy()` — $P_E$
- ✓ `compute_conversion_PE_KE()` — $C(P_E, K_E)$ (conversão baroclínica)
- ✓ `compute_conversion_KE_KZ()` — $C(K_E, K_Z)$ (conversão barotrópica)
- ✓ `integrate_vertically()` — Integração vertical ponderada por pressão
- ✓ `print_lec_summary()` — Resumo dos termos LEC

---

## 📊 Próximos Passos Sugeridos

### Fase 1 — Análise Visual (Curto Prazo)
1. Ajustar `plot_basic_fields.py` para gerar animação temporal (loop sobre time steps)
2. Parse correto do CSV do track (separador `;`)
3. Plotar trajetória do ciclone sobreposta aos mapas

### Fase 2 — Pré-processamento para LEC
1. Extrair domínio centrado no ciclone (±10-15° do centro ao longo da trajetória)
2. Implementar decomposição zonal-eddy para todas as variáveis
3. Calcular temperatura potencial e estabilidade estática

### Fase 3 — Cálculo do Ciclo de Energia de Lorenz
1. Implementar script `scripts/analysis_02_lec_computation/compute_lec_terms.py`
2. Calcular termos de energia: $K_Z$, $K_E$, $P_Z$, $P_E$ para cada time step
3. Calcular conversões: $C(P_E, K_E)$ e $C(K_E, K_Z)$
4. Integrar verticalmente (100-1000 hPa)
5. Salvar série temporal em `results/processed/lec_timeseries_bigua.nc`

### Fase 4 — Visualização Final
1. Plotar evolução temporal dos termos LEC
2. Plotar diagrama de caixas do ciclo energético (estilo Lorenz box)
3. Comparar fase de intensificação vs. maturação vs. dissipação
4. Gerar figuras finais para paper em `figures/paper/`

---

## 🔧 Como Usar o Repositório

### 1. Criar Ambiente
```bash
cd /Users/danilocoutodesouza/Documents/Programs_and_scripts/bigua_analysis
conda env create -f environment.yml
conda activate bigua
```

### 2. Explorar os Dados
```bash
# Inspecionar estrutura do NetCDF
python scripts/exploratory/explore_wrf_data.py

# Gerar mapas básicos (níveis padrão)
python scripts/exploratory/plot_basic_fields.py
```

### 3. Ajustar Configurações
- Editar `TIME_INDEX` em `plot_basic_fields.py` para outros time steps
- Editar `LEVELS_TO_PLOT` para outros níveis de pressão
- Variáveis estão mapeadas automaticamente (t, u, v, z)

### 4. Próximas Análises
Use as funções em `scripts/utils/utils_lec.py` para implementar o cálculo completo do LEC.

---

## 📚 Referências no SCIENTIFIC_NOTES.md

- Lorenz (1955) — Teoria original do LEC
- Li et al. (2007) — Aplicação com dados de reanálise
- Reboita et al. (2019) — Climatologia de ciclones no Atlântico Sul
- Gramcianinov et al. (2019) — Análise de tracks de ciclones

---

## ✅ Status Final

| Item | Status |
|------|--------|
| Estrutura de pastas | ✅ Completa |
| Documentação (README + SCIENTIFIC_NOTES) | ✅ Completa |
| Ambiente conda | ✅ Criado |
| Scripts exploratórios | ✅ Funcionando |
| Mapas básicos gerados | ✅ 4 níveis (1000, 850, 500, 250 hPa) |
| Funções LEC implementadas | ✅ Todas preparadas |
| Análise LEC completa | ⏳ Próxima fase |

---

**Repositório pronto para análise do Ciclo de Energia de Lorenz do ciclone Biguá!** 🌀
