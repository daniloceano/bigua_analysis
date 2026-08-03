# SCIENTIFIC_NOTES.md — Ciclone Biguá

**Projeto**: Análise do Ciclo de Energia de Lorenz do Ciclone Biguá  
**Última atualização**: 2026-07-22

---

## Research Questions

1. Qual é a estrutura tridimensional (T, vento, geopotencial) do ciclone Biguá durante seu ciclo de vida?
2. Quais são as magnitudes dos termos do Ciclo de Energia de Lorenz ($P_Z$, $P_E$, $K_Z$, $K_E$) durante a intensificação e maturação do sistema?
3. Qual é a conversão dominante responsável pela intensificação: $C(P_E, K_E)$ (conversão baroclínica) ou $C(K_Z, K_E)$ (conversão barotrópica)?
4. Como as conversões energéticas evoluem ao longo do ciclo de vida do ciclone?

---

## Physical / Statistical Framework

### Ciclo de Energia de Lorenz (Lorenz, 1955)

O Ciclo de Energia de Lorenz (LEC) descreve as transformações entre energia potencial disponível (APE) e energia cinética (KE) em seus componentes zonais e eddy:

**Termos de energia:**
- $P_Z$: APE zonal (associada à estrutura térmica média zonal)
- $P_E$: APE eddy (associada a anomalias térmicas)
- $K_Z$: KE zonal (vento médio zonal)
- $K_E$: KE eddy (perturbações do vento)

**Conversões:**
- $C(P_Z, P_E)$: conversão de APE zonal → APE eddy (instabilidade baroclínica zonal)
- $C(P_E, K_E)$: conversão de APE eddy → KE eddy (conversão baroclínica)
- $C(K_E, K_Z)$: conversão de KE eddy → KE zonal (conversão barotrópica)
- $C(P_Z, K_Z)$: conversão de APE zonal → KE zonal (circulação direta de Hadley)

**Equações principais:**

$$C(P_E, K_E) = -\frac{R}{p} \int [\omega' T'] \, dp$$

$$C(K_Z, K_E) = -\int [\overline{u'v'} \frac{\partial \overline{u}}{\partial y} + \overline{v'v'} \frac{\partial \overline{v}}{\partial y}] \, dp$$

onde:
- $\overline{(\cdot)}$ = média zonal
- $(\cdot)'$ = desvio da média zonal (componente eddy)
- $R = 287.05$ J/(kg K) = constante dos gases para ar seco
- $\omega$ = velocidade vertical em coordenadas de pressão (Pa/s)
- $p$ = pressão (Pa)

---

## Datasets and Variables

### Simulação WRF
- **Arquivo bruto**: `data/WRF_d02_bigua.nc` (18.2 GB, 10 variáveis, sem lat/lon real)
- **Arquivo corrigido (uso recomendado)**: `data/WRF_d02_bigua_LEC.nc` (~5.3 GB, apenas t/ght/omega/u/v, lat/lon reais)
- **Domínio**: d02 (alta resolução, aninhado do ERA5)
- **Condições de contorno**: ERA5 reanalysis
- **Período**: 2024-12-13 a 2024-12-16, resolução 3h (25 time steps)
- **Variáveis** (no arquivo corrigido):
  - `u`, `v`: componentes do vento (m/s)
  - `t`: temperatura (K)
  - `ght`: altura geopotencial (m) — convertida para geopotencial (m²/s²) internamente pelo LEC via `Geopotential Height`
  - `omega`: velocidade vertical (Pa/s)
- **Níveis de pressão**: 24 níveis, 100–1000 hPa
- **Resolução espacial**: 786 × 879 pontos; lat [-39.47°, -18.87°], lon [-61.20°, -34.58°]
- **Georreferência**: recuperada em 2026-08-03 a partir de arrays lat/lon fornecidos separadamente (o arquivo bruto havia perdido essa informação durante processamento com CDO) — ver `data/metadata/wrf_d02_latlon_download.json`

### Track do Ciclone
- **Arquivo**: `data/bigua_track_track_ERA.csv` (separador `;`)
- **Conteúdo**: Posição (Lat, Lon) do centro do ciclone ao longo do tempo, mais length, width, vorticidade/altura/vento em 850 hPa
- **Método de tracking**: detector automático de vórtices (rodado sobre ERA5)

---

## Methodology

### 1. Pré-processamento
1. Carregar dados WRF (`xarray.open_dataset`)
2. Verificar variáveis, dimensões, níveis de pressão
3. Se necessário, converter temperatura potencial → temperatura (K)
4. Se necessário, converter altura geopotencial → geopotencial ($Z = g \times \text{GHT}$, $g = 9.81$ m/s²)
5. Extrair domínio espacial centrado no ciclone (e.g., ±15° lat/lon do centro ao longo da trajetória)

### 2. Decomposição Zonal-Eddy
Para cada variável $\phi$ (u, v, T, omega):
$$\phi = \overline{\phi} + \phi'$$
onde:
- $\overline{\phi}$ = média ao longo da longitude
- $\phi'$ = anomalia em relação à média zonal

### 3. Cálculo dos Termos de Energia
**Energia cinética zonal (J/kg):**
$$K_Z = \frac{1}{2}(\overline{u}^2 + \overline{v}^2)$$

**Energia cinética eddy (J/kg):**
$$K_E = \frac{1}{2}\overline{(u'^2 + v'^2)}$$

**Energia potencial disponível (requer cálculo da estabilidade estática $\sigma$):**
$$P_E = \frac{R}{2\sigma p} \overline{T'^2}$$

**Estabilidade estática:**
$$\sigma = -\frac{R T}{p} \frac{\partial \ln \theta}{\partial p}$$
onde $\theta$ = temperatura potencial.

### 4. Integração Vertical
Integrar cada termo de energia verticalmente ponderado pela pressão:
$$E_{\text{total}} = \frac{1}{g} \int_{p_{\text{top}}}^{p_{\text{sfc}}} E(p) \, dp$$

Usar integração discreta com $\Delta p$ entre níveis adjacentes.

### 5. Série Temporal
Computar todos os termos LEC para cada time step ao longo do ciclo de vida do ciclone.

---

## Assumptions

1. **Aproximação quasi-geostrófica**: válida para ciclones extratropicais de escala sinótica
2. **Domínio centrado no ciclone**: assume que o domínio $\pm 15°$ captura a circulação eddy associada ao sistema
3. **Decomposição zonal-eddy**: válida se o ciclone estiver suficientemente isolado
4. **Estabilidade estática constante** (primeira aproximação): pode ser refinada usando cálculo completo de $\sigma(p)$
5. **Níveis de pressão**: assumir níveis padrão ou níveis modelo do WRF

---

## Results and Interpretation

### 2026-08-03 — Correção: Identificação Correta do Dataset

**[NOTA IMPORTANTE]** Houve uma confusão inicial no pipeline:
- O arquivo `data/ERA5_d02_bigua_LCT.nc` foi **incorretamente** identificado como simulação WRF
- Na verdade, era dados de reanalysis ERA5
- O arquivo WRF correto é `data/WRF_d02_bigua.nc` (agora sendo baixado)

Esta nota documenta que os scripts exploratórios foram revisados para apontar para o arquivo WRF correto.

---

### 2026-07-22 — Análise Exploratória Inicial

**Estrutura do Dataset WRF:**
- **Dimensões**: 
  - Temporal: 216 time steps (2024-12-11 00:00 a 2024-12-19 23:00, horário)
  - Vertical: 24 níveis de pressão (100 a 1000 hPa)
  - Espacial: 82 lat × 106 lon
  - Domínio: 19°S a 39.25°S, 61°W a 34.75°W (Atlântico Sul ocidental)

- **Níveis de pressão disponíveis (Pa)**: 
  10000, 15000, 20000, 25000, 30000, 35000, 40000, 45000, 50000, 55000, 60000, 65000, 70000, 75000, 77500, 80000, 82500, 85000, 87500, 90000, 92500, 95000, 97500, 100000
  
- **Variáveis disponíveis**:
  - `z`: Geopotencial (m²/s²) ✓
  - `t`: Temperatura (K) ✓
  - `u`: Componente zonal do vento (m/s) ✓
  - `v`: Componente meridional do vento (m/s) ✓
  - `w`: Velocidade vertical (Pa/s) ✓ **[essencial para C(PE,KE)]**
  - `q`: Umidade específica (kg/kg)
  - `r`: Umidade relativa (%)

**Track do Ciclone:**
- 25 pontos de track identificados
- Período: 2024-12-13 12Z a 2024-12-14 00Z (fase madura do sistema)
- Variáveis do track: lat, lon, length, width, min/max vorticity 850 hPa, min height 850 hPa, max wind 850 hPa

**Mapas Exploratórios Gerados:**
Gerados mapas de temperatura, vento (magnitude + vetores) e geopotencial para os níveis:
- 1000 hPa (baixos níveis — estrutura de superfície)
- 850 hPa (baixa troposfera — núcleo do ciclone)
- 500 hPa (média troposfera — ondas baroclínicas)
- 250 hPa (alta troposfera — corrente de jato)

Time step selecionado: 2024-12-15 12:00 (meio do período de simulação)

**Observações Preliminares:**
- Dataset contém **todas as variáveis necessárias** para o cálculo do Ciclo de Energia de Lorenz
- Presença de `w` (velocidade vertical) é crítica para calcular $C(P_E, K_E) = -(R/p) \langle \omega' T' \rangle$
- Resolução temporal (horária) é adequada para análise da evolução energética
- 24 níveis verticais permitem integração vertical detalhada

**Próximas Ações:**
1. Parse correto do arquivo CSV do track (separador `;`)
2. Extração de domínio centrado no ciclone ao longo da trajetória
3. Implementação da decomposição zonal-eddy
4. Cálculo dos termos de energia $K_Z$, $K_E$, $P_Z$, $P_E$
5. Cálculo das conversões baroclínica e barotrópica

---

## Caveats and Limitations

1. **Resolução do WRF**: A alta resolução do d02 pode capturar processos de mesoescala não resolvidos pelo LEC clássico
2. **Efeitos de fronteira**: O domínio limitado pode introduzir artefatos nos fluxos de fronteira $B_{PE}$, $B_{KE}$
3. **Dissipação**: Termos de dissipação $D_Z$ e $D_E$ são difíceis de quantificar diretamente — geralmente calculados como resíduo
4. **Umidade**: O LEC clássico não considera explicitamente efeitos de calor latente (poderia ser estendido)

---

## Next Steps

### Fase 1 — Exploração de Dados WRF (Em Andamento)
- [ ] **AGUARDANDO**: Fazer download do arquivo WRF (`data/WRF_d02_bigua.nc`)
  - Problema: arquivo Google Drive precisa estar com permissão "Qualquer pessoa com o link"
  - Solução: compartilhar arquivo corretamente
- [ ] Executar `scripts/exploratory/inspect_wrf_structure.py` (detecção automática de variáveis)
- [ ] Executar `scripts/exploratory/explore_wrf_data.py` (verificação completa)
- [ ] Executar `scripts/exploratory/plot_basic_fields.py` (gerar mapas 1000, 850, 500, 250 hPa)

### Fase 2 — Pré-processamento
- [ ] Extrair domínio centrado no ciclone (±15° lat/lon do track)
- [ ] Implementar decomposição zonal-eddy
- [ ] Validar que todas as variáveis necessárias estão disponíveis

### Fase 3 — Ciclo de Energia de Lorenz
- [ ] Implementar cálculo dos termos $K_Z$, $K_E$, $P_Z$, $P_E$
- [ ] Implementar cálculo das conversões $C(P_E, K_E)$, $C(K_Z, K_E)$
- [ ] Gerar séries temporais dos termos LEC

### Fase 4 — Visualização e Análise
- [ ] Gerar séries temporais dos termos LEC ao longo do ciclo de vida
- [ ] Comparar com estudos prévios de ciclones no Atlântico Sul (Reboita et al., Gramcianinov et al.)

---

## References

1. Lorenz, E. N. (1955). Available potential energy and the maintenance of the general circulation. *Tellus*, 7(2), 157-167. DOI: 10.1111/j.2153-3490.1955.tb01148.x

2. Oort, A. H. (1964). On the energetics of the mean and eddy circulations in the lower stratosphere. *Tellus*, 16(3), 309-327.

3. Li, L., Ingersoll, A. P., Jiang, X., Feldman, D., & Yung, Y. L. (2007). Lorenz energy cycle of the global atmosphere based on reanalysis datasets. *Geophys. Res. Lett.*, 34, L16813. DOI: 10.1029/2007GL029985

4. Muench, H. S. (1965). On the dynamics of the wintertime stratosphere circulation. *J. Atmos. Sci.*, 22(4), 349-360.

5. Reboita, M. S., et al. (2019). South Atlantic extratropical cyclones climatology. *Int. J. Climatol.*, 39, 1–17.

6. Gramcianinov, C. B., et al. (2019). Analysis of Atlantic extratropical storm tracks characteristics in 41 years of ERA5 and CFSR/CFSv2 databases. *Ocean Eng.*, 194, 106592.
