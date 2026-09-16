import argparse
from pathlib import Path
from osgeo import gdal


def convert_raster(
    input_path: str | Path,
    output_path: str | Path,
    *,
    output_format: str | None = None,
    creation_options: list[str] | None = None,
) -> Path:
    """Converte rasters usando um driver GDAL explícito ou a extensão da saída.

    Opções de criação dependem do driver: COMPRESS=LZW (GTiff), ZLEVEL=6
    (PNG), QUALITY=90 (JPEG).
    Metadados e máscaras dependem do formato; GDAL pode criar arquivos auxiliares.
    """
    source = Path(input_path).expanduser().resolve()
    destination = Path(output_path).expanduser().resolve()
    translate_options = {
        "format": output_format,
        "creationOptions": list(creation_options or []),
    }
    destination.parent.mkdir(parents=True, exist_ok=True)
    with gdal.Translate(str(destination), str(source), **translate_options):
        pass
    return destination


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("-of", "--format", dest="output_format")
    parser.add_argument("-co", "--creation-option", action="append", default=[])
    args = parser.parse_args()
    output = convert_raster(
        args.input, args.output, output_format=args.output_format,
        creation_options=args.creation_option,
    )


if __name__ == "__main__":
    main()
