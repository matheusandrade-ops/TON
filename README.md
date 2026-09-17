# Análise de rasters e vetores

| Script | Objetivo |
| --- | --- |
| [main-2.1.py](main-2.1.py) | Inspecionar e comparar metadados dos TIFFs de um ZIP. |
| [main-2.2.py](main-2.2.py) | Converter formatos e aplicar compressão. |
| [main-3.1.py](main-3.1.py) | Comparar estatísticas por banda com Rasterio e NumPy. |
| [main-3.2.py](main-3.2.py) | Binarizar bandas por limiar. |
| [main-4.1.py](main-4.1.py) | Inspecionar CRS, geometrias e atributos de arquivos vetoriais. |
| [main-4.2.py](main-4.2.py) | Notas sobre a identificação da zona UTM do GeoJSON. |
| [main-4.3.py](main-4.3.py) | Analisar DN, filtrar por atributo e salvar o GeoJSON. |
| [main-4.4.py](main-4.4.py) | Identificar o UTM adequado, reprojetar e salvar o GeoJSON. |
| [main-5.1.py](main-5.1.py) | Calcular o comprimento das linhas em metros e salvar o GeoJSON. |
| [main-5.2.py](main-5.2.py) | Calcular a área dos polígonos em hectares e salvar o GeoJSON. |


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

## main-4.1.py — Inspeção de vetores

A função `load_vector()` lê o arquivo com GeoPandas e retorna um GeoDataFrame
sem alterar os dados. Imprime a quantidade de elementos, o CRS, os tipos de
geometria e as colunas com seus tipos e valores ausentes.


### Observações dos dados

- `MATOLOGIA_Orthomosaico.geojson`: 82 polígonos, com atributos `DN`, `AREA` e `ID` preenchidos.
- `shape.geojson`: um polígono com todos os atributos não geométricos ausentes.
- Ambos usam EPSG:4326, com coordenadas em graus.

## main-4.2.py — Identificação da zona UTM

A função `identify_utm_crs(gdf)` usa o centro dos limites (`total_bounds`) para calcular o fuso e o hemisfério. Depois, busca o código EPSG no catálogo, **preservando o datum do arquivo**.

Para áreas locais, trata limites que cruzam ±180°. Se houver vários EPSG
compatíveis, escolhe o menor número de código, sem indicar maior precisão.

### Como a zona foi calculada

As feições são convertidas para EPSG:4326 em uma cópia porque a fórmula do
fuso precisa da longitude em graus; o arquivo de entrada pode ter coordenadas
projetadas em metros. Essa conversão serve apenas para localizar a área:
o datum original é mantido na escolha do EPSG final. Se o arquivo já está em
EPSG:4326, as coordenadas não mudam.

O centro dos limites fornece a longitude e a latitude usadas no cálculo:

```text
longitude central = (longitude mínima + longitude máxima) / 2
latitude central = (latitude mínima + latitude máxima) / 2
zona UTM = piso((longitude central + 180) / 6) + 1
```

`piso` arredonda para baixo. A zona fica entre 1 e 60; latitude central
positiva ou zero indica Norte, e negativa indica Sul. Para áreas que cruzam
±180°, as longitudes são ajustadas antes de calcular o centro.
O código consulta o catálogo para obter o EPSG do fuso, hemisfério e datum
original. O resultado é exibido ao lado da estimativa de `gdf.estimate_utm_crs()`.

### Quando confiar na estimativa automática

- **Boa referência:** área pequena, dentro de um único fuso e hemisfério,
  com geometrias válidas e CRS de origem correto. Confira se o datum e a
  área de uso do EPSG retornado correspondem aos dados.
- **Conferir manualmente:** área próxima de um limite de fuso, que ocupa
  vários fusos, cruza o Equador ou reúne feições muito distantes. O centro
  dos limites pode não representar bem toda a área.

## main-4.3.py — Filtro por atributo

A função `filter_by_attribute(gdf, expression)` usa `.query()` para filtrar e mostra o
tipo de `DN`, os valores únicos e a quantidade de geometrias por classe no resultado.
Use `expression=None` para analisar todas as feições.

O filtro atual é `DN == 3`: salva 62 geometrias em
`vectors_case_1/MATOLOGIA_Orthomosaico_filtrado.geojson`.

## main-4.4.py — Reprojeção para UTM

`gdf.estimate_utm_crs()` estima o UTM pelos, `reproject_gdf(gdf, target_epsg)` transforma as coordenadas e retorna um novo GeoDataFrame. O CRS de origem deve estar corretamente informado no arquivo.

## main-5.1.py — Comprimento das linhas

`add_linestring_length(gdf, col_name="length_m")` retorna uma cópia com o
comprimento de cada linha em metros. Estima o UTM com `estimate_utm_crs()` e
reprojeta temporariamente para calcular `geometry.length`, usando o Shapely
por meio do GeoPandas.

## main-5.2.py — Área dos polígonos

`add_polygon_area(gdf, col_name="area_ha")` retorna uma cópia com a área em
hectares. Estima o UTM com `estimate_utm_crs()` e reprojeta temporariamente
para calcular `geometry.area / 10000`.
