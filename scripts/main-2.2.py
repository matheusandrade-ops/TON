import argparse
from osgeo import gdal


def convert_raster(
    input_path: str,
    output_path: str,
    *,
    output_format: str | None = None,
    creation_options: list[str] | None = None,
) -> str:
    """Converte o raster pelo formato ou extensão, aplicando as opções de criação."""
    with gdal.Translate(
        output_path, input_path, format=output_format,
        creationOptions=creation_options or [],
    ):
        pass
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("output")
    parser.add_argument("-of", "--format", dest="output_format")
    parser.add_argument("-co", "--creation-option", action="append", default=[])
    args = parser.parse_args()
    convert_raster(
        args.input, args.output, output_format=args.output_format,
        creation_options=args.creation_option,
    )


if __name__ == "__main__":
    main()
