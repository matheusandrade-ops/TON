# Inspeção dos rasters

Inspeciona e compara os metadados dos rasters contidos em `Orthos.zip`.

## Como executar

Requisitos: Python 3.12 e uv.

Coloque `Orthos.zip` na raiz do projeto e execute:

```bash
uv venv --python 3.12
uv pip sync requirements.txt
uv run --no-sync main.py
```

## Relatórios

- `reports/raster_metadata.json`: metadados dos rasters.
- `reports/differences.md`: comparação dos metadados.
