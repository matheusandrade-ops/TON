import json
from tempfile import TemporaryDirectory
from zipfile import ZipFile
import rasterio

ZIP_PATH = "Orthos.zip"
REPORTS_DIR = "reports"  # A pasta deve existir antes da execução.


def inspect_raster(raster_path: str) -> dict:
    """Lê os metadados do raster, sem carregar os pixels."""
    with rasterio.open(raster_path) as src:
        return {
            "crs": src.crs.to_string(),
            "crs_units": src.crs.linear_units if src.crs.is_projected else "degree",
            "gsd": {"x": src.res[0], "y": src.res[1]},
            "bounds": src.bounds._asdict(),
            "count": src.count,
            "dtypes": src.dtypes,
            "nodatavals": src.nodatavals,
        }


def describe_differences(rasters: dict) -> str:
    """Agrupa valores iguais e mostra apenas os metadados que diferem."""
    lines = ["# Diferenças entre os rasters", ""]
    for field, label in (
        ("crs", "CRS"), ("gsd", "GSD"), ("bounds", "Limites"),
        ("count", "Bandas"), ("dtypes", "Tipos"), ("nodatavals", "Nodata"),
    ):
        groups = {}
        for name, metadata in rasters.items():
            value = json.dumps(metadata[field], ensure_ascii=False)
            groups.setdefault(value, []).append(name)
        if len(groups) > 1:
            lines.extend([f"## {label}", "", "| Rasters | Valor |", "| --- | --- |"])
            for value, names in groups.items():
                names = ", ".join(names).replace("|", "\\|")
                value = value.replace("|", "\\|")
                lines.append(f"| {names} | **{value}** |")
            lines.append("")
    if len(lines) == 2:
        lines.append("Nenhuma diferença encontrada nos metadados comparados.")
    return "\n".join(lines) + "\n"


def main() -> dict:
    with TemporaryDirectory() as temp_dir:
        with ZipFile(ZIP_PATH) as archive:
            archive.extractall(temp_dir)
            rasters = {
                name: inspect_raster(f"{temp_dir}/{name}")
                for name in sorted(archive.namelist())
                if name.lower().endswith((".tif", ".tiff"))
            }

    with open(f"{REPORTS_DIR}/raster_metadata.json", "w", encoding="utf-8") as report:
        json.dump(rasters, report, ensure_ascii=False, indent=2)
        report.write("\n")
    with open(f"{REPORTS_DIR}/differences.md", "w", encoding="utf-8") as report:
        report.write(describe_differences(rasters))
    return rasters


if __name__ == "__main__":
    main()
