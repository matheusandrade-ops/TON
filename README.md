# Análise e conversão de rasters

| Script | Objetivo |
| --- | --- |
| [main-2.1.py](main-2.1.py) | Inspecionar e comparar metadados dos TIFFs de um ZIP. |
| [main-2.2.py](main-2.2.py) | Converter formatos e aplicar compressão. |
| [main-3.1.py](main-3.1.py) | Comparar estatísticas por banda com Rasterio e NumPy. |
| [main-3.2.py](main-3.2.py) | Binarizar bandas por limiar. |


## main-2.1.py — Inspeção de metadados

Extrai o ZIP temporariamente e compara CRS, GSD, limites, bandas, tipos e nodata.
Os caminhos são configurados em `ZIP_PATH` e `REPORTS_DIR` no script.

### Como executar

Coloque `Orthos.zip` na raiz do projeto e execute:

```bash
uv run --python 3.12 main-2.1.py
```

### Relatórios gerados

- `reports/raster_metadata.json`: metadados dos rasters.
- `reports/differences.md`: comparação dos metadados.

## main-2.2.py — Conversão e compressão

Converte um raster usando GDAL. O formato é escolhido pela extensão da saída
ou pelo argumento `--format`.

### Como executar

```text
uv run main-2.2.py <entrada> <saida> [--format DRIVER] [-co NOME=VALOR]
```

- `entrada`: raster de origem.
- `saida`: arquivo de destino; a extensão define o formato.
- `--format`: define o driver explicitamente, como `GTiff`, `PNG`, `JPEG` ou `COG`.
- `-co`: opção do formato, como `COMPRESS=LZW` (TIFF), `ZLEVEL=9` (PNG) ou `QUALITY=90` (JPEG). Pode ser repetida.


### Redução de tamanho

Comparação com `Orthos/Orthomosaico.tif`: **101,21 MB** (101.210.212 bytes).
Após o original, as linhas comparam GeoTIFF e COG para cada compressão: NONE, LZW e DEFLATE.

| Formato | Opção de compressão | Compressão efetiva | Tamanho | Economia | Redução |
| --- | --- | --- | --- | --- | --- |
| Original | — | Nenhuma | 101,21 MB | 0,00 MB | 0,00% |
| GeoTIFF | `-co COMPRESS=NONE` | Nenhuma | 73,35 MB | 27,86 MB | 27,52% |
| COG | `-co COMPRESS=NONE` | Nenhuma | 125,83 MB | -24,62 MB | -24,33% |
| GeoTIFF | `-co COMPRESS=LZW` | LZW | 41,80 MB | 59,41 MB | 58,70% |
| COG | `-co COMPRESS=LZW` | LZW | 52,21 MB | 49,00 MB | 48,41% |
| GeoTIFF | `-co COMPRESS=DEFLATE` | DEFLATE | 31,65 MB | 69,56 MB | 68,72% |
| COG | `-co COMPRESS=DEFLATE` | DEFLATE | 37,30 MB | 63,91 MB | 63,15% |

## main-3.1.py — Estatísticas por banda

O `main-3.1.py` compara Rasterio/GDAL e NumPy e imprime a diferença absoluta
entre os resultados por banda.

### Métricas e relevância

| Métrica | Relevância |
| --- | --- |
| Mínimo e máximo | Identificar a faixa dos valores válidos e possíveis extremos anormais. |
| Média | Resumir o nível médio de intensidade, elevação ou índice, conforme o raster. |
| Desvio padrão | Medir a dispersão dos valores; não representa precisão ou erro do levantamento. |

### Como interpretar as diferenças

- **Precisão numérica:** algoritmos e ordem das operações podem gerar pequenas diferenças de ponto flutuante. A impressão arredonda os valores, mas a diferença é calculada antes desse arredondamento. Diferenças da ordem de `10⁻¹¹`, observadas nos testes, são compatíveis com precisão numérica; diferenças maiores exigem conferir as máscaras e os pixels considerados.
- **Nodata:** MDS e GLI declaram `-10000` como inválido. Incluí-lo distorceria principalmente mínimo, média e desvio padrão. Um zero válido não deve ser descartado automaticamente.
- **Transparência:** o ortomosaico não declara nodata; sua banda alpha mascara áreas transparentes nas bandas RGB. A própria alpha representa cobertura, não intensidade de cor, e seus zeros entram nas estatísticas dessa banda.
- **Métodos:** NumPy usa pixels lidos com `masked=True`, média e desvio em `float64` e desvio populacional (`ddof=0`). Rasterio usa `stats(approx=False)`.

## main-3.2.py — Binarização por limiar

Gera um TIFF com **1 onde pixel ≥ limiar** e **0 abaixo**, por banda.
Preserva o georreferenciamento e a máscara de pixels inválidos; alpha não é binarizada.


## Testando commit#1 na branch nova

## Testando commit#2 na branch nova

## Testando commit#3 na branch nova