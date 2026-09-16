# Inspeção dos rasters

Inspeciona e compara os metadados dos rasters contidos em `Orthos.zip`.

## Como executar

Requisitos: Python 3.12 e uv.

Coloque `Orthos.zip` na raiz do projeto e execute:

```bash
uv run --python 3.12 main.py
```

## Relatórios

- `reports/raster_metadata.json`: metadados dos rasters.
- `reports/differences.md`: comparação dos metadados.

## Conversão de rasters

```text
uv run main-2.py <entrada> <saida> [--format DRIVER] [-co NOME=VALOR]
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
