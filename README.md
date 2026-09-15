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
