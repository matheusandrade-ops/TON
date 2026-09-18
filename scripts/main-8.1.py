from shutil import copy2
from osgeo import gdal


INPUT_PATH = "Orthos/Orthomosaico.gpkg"
MAX_OVERVIEW_SIZE = 256


def build_overviews(raster_path: str) -> str:
    """Cria uma cópia com overviews de fator 2, preservando o raster original."""
    output_path = raster_path.removesuffix(".gpkg") + "_overviews.gpkg"
    copy2(raster_path, output_path)

    gdal.UseExceptions()
    dataset = gdal.OpenEx(
        output_path, gdal.OF_RASTER | gdal.OF_UPDATE,
        open_options=["TILE_FORMAT=PNG"],
    )
    # Dimensão em pixels = extensão geográfica / resolução original.
    factors = []
    factor = 1
    while max(dataset.RasterXSize, dataset.RasterYSize) > MAX_OVERVIEW_SIZE * factor:
        factor *= 2
        factors.append(factor)
    if factors:
        dataset.BuildOverviews("AVERAGE", factors)
    dataset = None
    return output_path


if __name__ == "__main__":
    print(build_overviews(INPUT_PATH))
 