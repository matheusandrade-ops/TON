from math import ceil, floor
import rasterio
from rasterio.windows import Window, from_bounds


INPUT_PATH = "Orthos/Orthomosaico.tif"
OUTPUT_PATH = "Orthos/Orthomosaico_recorte.tif"
BBOX = (683690, 8227500, 683740, 8227550)


def clip_raster_bbox(raster_path, bbox, output_path):
    """Recorta a bbox no CRS do raster, incluindo os pixels das bordas."""
    with rasterio.open(raster_path) as source:
        window = from_bounds(*bbox, transform=source.transform)
        window = Window.from_slices(
            (floor(window.row_off), ceil(window.row_off + window.height)),
            (floor(window.col_off), ceil(window.col_off + window.width)),
        )
        profile = source.meta.copy()
        profile.update(
            driver="GTiff", width=window.width, height=window.height,
            transform=source.window_transform(window),
        )
        with rasterio.open(output_path, "w", **profile) as output:
            output.write(source.read(window=window))
            output.colorinterp = source.colorinterp
    return output_path


if __name__ == "__main__":
    print(clip_raster_bbox(INPUT_PATH, BBOX, OUTPUT_PATH)) 
