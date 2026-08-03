# Data Directory — Ciclone Biguá

## Arquivos

### 1. ERA5_d02_bigua_LCT.nc
- **Tipo**: Saída de simulação WRF (Weather Research and Forecasting Model)
- **Domínio**: d02 (alta resolução, aninhado)
- **Condições de contorno**: ERA5 Reanalysis
- **Conteúdo**: Campos atmosféricos 3D do ciclone Biguá
- **Variáveis esperadas**: 
  - Componentes do vento (U, V, W ou OMEGA)
  - Temperatura (T ou TK)
  - Geopotencial (Z ou GHT)
  - Pressão (níveis ou coordenada vertical)
- **Período**: [verificar com script exploratório]
- **Tamanho**: [verificar]

### 2. bigua_track_track.csv
- **Tipo**: Track do ciclone (trajetória)
- **Conteúdo**: Posição do centro do ciclone (lat, lon) ao longo do tempo
- **Método de tracking**: [a ser documentado]
- **Uso**: Referência para análise centrada no ciclone, extração de domínio móvel

---

## Metadata

O subdiretório `metadata/` contém logs de proveniência e metadados:
- Informações sobre a simulação WRF (namelist, configurações)
- Registros de download/transferência de dados
- Documentação sobre o método de tracking

**Nota**: Sempre documente a origem dos dados para garantir reprodutibilidade!

---

## Como Inspecionar os Dados

Execute o script exploratório:
```bash
python scripts/exploratory/explore_wrf_data.py
```

Isso gerará um relatório completo sobre:
- Dimensões e coordenadas
- Variáveis disponíveis
- Níveis verticais
- Período temporal
- Estrutura do track
