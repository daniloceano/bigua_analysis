# Análise do Ciclone Biguá — Atlântico Sul

**Objetivo**: Análise da estrutura dinâmica e do ciclo energético de Lorenz do ciclone extratropical Biguá no Atlântico Sul usando simulações WRF de alta resolução.

---

## Contexto Científico

O ciclone Biguá foi um sistema extratropical significativo no Atlântico Sul. Este projeto visa:
- Caracterizar a estrutura tridimensional do ciclone (temperatura, vento, geopotencial)
- Diagnosticar o Ciclo de Energia de Lorenz (LEC) durante o ciclo de vida do sistema
- Quantificar conversões energéticas (APE → KE, zonal ↔ eddy)

---

## Dados

- **Simulação WRF**: `data/ERA5_d02_bigua_LCT.nc`
  - Domínio: d02 (alta resolução)
  - Variáveis: u, v, T, Z, omega (verificar com script exploratório)
  - Níveis de pressão: 1000, 925, 850, 700, 500, 400, 300, 250, 200, 150, 100 hPa (verificar)
  
- **Track do ciclone**: `data/bigua_track_track.csv`
  - Lat/lon do centro do ciclone ao longo do tempo

---

## Estrutura de Pastas

```
bigua_analysis/
├── README.md                        # Este arquivo
├── SCIENTIFIC_NOTES.md             # Registro científico (métodos, equações, resultados)
├── environment.yml                  # Ambiente conda
├── data/
│   ├── ERA5_d02_bigua_LCT.nc       # Simulação WRF
│   ├── bigua_track_track.csv       # Track do ciclone
│   └── metadata/                    # Logs de proveniência
├── scripts/
│   ├── exploratory/                 # Análises exploratórias, diagnósticos
│   ├── main/                        # Scripts finais para figuras do paper
│   ├── utils/                       # Funções reutilizáveis (LEC, I/O, plots)
│   ├── analysis_01_preprocessing/   # Pré-processamento dos dados WRF
│   ├── analysis_02_lec_computation/ # Cálculo dos termos do LEC
│   └── analysis_03_visualization/   # Mapas e séries temporais
├── figures/
│   ├── exploratory/                 # Plots exploratórios
│   └── paper/                       # Figuras finais para manuscrito
├── results/
│   ├── processed/                   # Datasets intermediários (termos LEC)
│   └── final/                       # Tabelas, métricas finais
└── docs/
    └── README.pdf                   # Versão exportada da documentação
```

---

## Workflow de Análise

### Fase 1 — Exploração Inicial
1. `scripts/exploratory/explore_wrf_data.py` — Inspecionar variáveis, dimensões, níveis
2. `scripts/exploratory/plot_basic_fields.py` — Mapas de T, vento, Z em níveis selecionados

### Fase 2 — Pré-processamento
1. Extrair domínio centrado no ciclone (±15° lat/lon do centro)
2. Interpolar para níveis de pressão padrão (se necessário)
3. Computar componentes zonais e eddy (T_bar, T_prime, u_bar, u_prime, etc.)

### Fase 3 — Ciclo de Energia de Lorenz
1. Calcular termos de energia: $P_Z$, $P_E$, $K_Z$, $K_E$
2. Calcular conversões: $C(P_Z, P_E)$, $C(P_E, K_E)$, $C(K_E, K_Z)$, $C(P_Z, K_Z)$
3. Calcular geração e dissipação
4. Integração vertical (ponderada por Δp)
5. Série temporal dos termos LEC ao longo do ciclo de vida

### Fase 4 — Visualização
1. Mapas de estrutura vertical (seção transversal)
2. Evolução temporal dos termos LEC
3. Diagramas de conversão energética

---

## Ambiente

Criar ambiente conda:
```bash
conda env create -f environment.yml
conda activate bigua
```

## Como Executar

1. **Exploração inicial**:
   ```bash
   python scripts/exploratory/explore_wrf_data.py
   ```

2. **Mapas básicos**:
   ```bash
   python scripts/exploratory/plot_basic_fields.py
   ```

3. **Análise completa** (em desenvolvimento):
   ```bash
   python scripts/analysis_01_preprocessing/preprocess_wrf.py
   python scripts/analysis_02_lec_computation/compute_lec_terms.py
   python scripts/analysis_03_visualization/plot_lec_timeseries.py
   ```

---

## Referências

- Lorenz, E. N. (1955). Available potential energy and the maintenance of the general circulation. *Tellus*, 7(2), 157-167.
- Li, L., Ingersoll, A. P., Jiang, X., Feldman, D., & Yung, Y. L. (2007). Lorenz energy cycle of the global atmosphere based on reanalysis datasets. *Geophys. Res. Lett.*, 34, L16813.
- Muench, H. S. (1965). On the dynamics of the wintertime stratosphere circulation. *J. Atmos. Sci.*, 22(4), 349-360.

---

## Contato

**Autor**: Danilo Couto de Souza  
**Instituição**: IAG-USP  
**Linha de Pesquisa**: Dinâmica e energética de ciclones extratropicais no Atlântico Sul
