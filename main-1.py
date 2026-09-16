from pathlib import Path
import json
import math
from tempfile import TemporaryDirectory
from zipfile import ZipFile
import rasterio

ZIP_PATH = "Orthos.zip"
REPORTS_DIR = "reports"
BASE_DIR = Path(__file__).resolve().parent


def inspect_raster(raster_path: str | Path) -> dict:
    """Extrai metadados sem carregar os pixels; GSD e bounds usam a unidade do CRS."""
    with rasterio.open(raster_path) as src:
        units = None
        if src.crs:
            units = src.crs.linear_units if src.crs.is_projected else "degree"

        # Converte nodata não finito para texto, pois JSON não aceita NaN/Infinity.
        nodata = [
            str(value) if value is not None and not math.isfinite(value) else value
            for value in src.nodatavals
        ]
        return {
            # Sistema de referência que posiciona o raster na Terra (ex.: EPSG:32721).
            # None, gravado como null no JSON, indica que o CRS não foi definido.
            "crs": src.crs.to_string() if src.crs else None,

            # Unidade das coordenadas horizontais e de GSD/bounds (ex.: metros).
            # Não informa a unidade dos valores dos pixels, como a elevação do MDS.
            "crs_units": units,

            # Tamanho do pixel nos eixos X e Y, na unidade do CRS.
            # Ex.: 0.03002 metro = 3.002 cm/pixel; não representa precisão posicional.
            "gsd": {"x": src.res[0], "y": src.res[1]},

            # Retângulo envolvente nas coordenadas do CRS:
            # left = menor X; bottom = menor Y; right = maior X; top = maior Y.
            # Pode incluir áreas sem dados nas bordas do raster.
            "bounds": src.bounds._asdict(),

            # Número de bandas: cada banda contém uma camada de valores por pixel.
            # Exemplos de conteúdo: vermelho, verde, azul, índice ou elevação.
            "count": src.count,

            # Tipo numérico de cada banda, na ordem das bandas.
            # uint8: inteiros de 0 a 255; float32: ponto flutuante de 32 bits.
            "dtypes": src.dtypes,

            # Valor que sinaliza ausência de dados em cada banda (ex.: -10000).
            # None/null = nodata não declarado; máscaras ainda podem marcar pixels inválidos.
            "nodatavals": nodata,
        }


def extract_orthos(zip_path: str | Path, destination: str | Path) -> Path:
    """Extrai o ZIP para a pasta de destino e retorna o caminho absoluto da pasta extraída."""
    destination = Path(destination).resolve()
    with ZipFile(zip_path) as archive:
        archive.extractall(destination)
    return destination


def inspect_rasters(orthos_dir: str | Path) -> dict:
    """Consolida TIFFs da pasta e subpastas, indexados pelo caminho relativo."""
    orthos_dir = Path(orthos_dir)
    rasters = {}
    for path in sorted(orthos_dir.rglob("*")):
        if path.is_file() and path.suffix.lower() in {".tif", ".tiff"}:
            name = path.relative_to(orthos_dir).as_posix()
            rasters[name] = inspect_raster(path)
    return rasters


def format_cell(value: object) -> str:
    """Formata valores ausentes e sequências de bandas para a tabela."""
    if isinstance(value, (list, tuple)):
        return ", ".join(format_cell(item) for item in value)
    return "Não definido" if value is None else str(value)


def describe_differences(rasters: dict) -> str:
    """Destaca valores diferentes em tabelas, agrupando arquivos iguais."""
    lines = ["# Diferenças entre os rasters", ""]
    for field, label in (
        ("crs", "CRS"), ("gsd", "GSD (X/Y, na unidade do CRS)"),
        ("bounds", "Bounds (na unidade do CRS)"),
        ("count", "Número de bandas"), ("dtypes", "Tipos por banda"),
        ("nodatavals", "Nodata por banda")
    ):
        groups = {}
        for name, data in rasters.items():
            value = data[field]
            key = json.dumps(value, ensure_ascii=False)
            groups.setdefault(key, (value, []))[1].append(name)
        if len(groups) < 2:
            continue

        lines.extend([f"## {label}", ""])
        # Separa X/Y e os limites em colunas para comparar lado a lado.
        first_value = next(iter(groups.values()))[0]
        columns = list(first_value) if isinstance(first_value, dict) else ["Valor"]
        lines.append("| Arquivos | " + " | ".join(columns) + " |")
        lines.append("| --- | " + " | ".join("---" for _ in columns) + " |")
        for value, names in groups.values():
            cells = list(value.values()) if isinstance(value, dict) else [value]
            cells = [format_cell(cell) for cell in cells]
            files = ", ".join(name.replace("|", "\\|") for name in names)
            highlighted = " | ".join(f"**{cell}**" for cell in cells)
            lines.append(f"| {files} | {highlighted} |")
        lines.append("")

    if len(lines) == 2:
        lines.append("Nenhuma diferença encontrada nos metadados comparados.")
    return "\n".join(lines) + "\n"


def main() -> dict:
    zip_path = BASE_DIR / Path(ZIP_PATH).expanduser()
    output_dir = BASE_DIR / Path(REPORTS_DIR).expanduser()

    with TemporaryDirectory(prefix="ton956_orthos_") as temp_dir:
        orthos_dir = extract_orthos(zip_path, temp_dir)
        rasters = inspect_rasters(orthos_dir)

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "raster_metadata.json").write_text(
        json.dumps(rasters, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    (output_dir / "differences.md").write_text(describe_differences(rasters), encoding="utf-8")
    return rasters


if __name__ == "__main__":
    main()
