import numpy as np
import rasterio
from rasterio.enums import ColorInterp

THRESHOLD = 0.05  # Limiar para Indice GLI
# THRESHOLD = 728  # Limiar para MDS
# THRESHOLD = [120, 200, 120]  # Limiar para RGB

RASTER_PATH = "Orthos/Indice_GLI.tif"
OUTPUT_PATH = "Orthos/Indice_GLI_mask.tif"


def mask_raster_by_threshold(
    raster_path: str,
    threshold: float | list[float] | tuple[float, ...],
    output_path: str,
) -> str:
    """Binariza por limiar comum ou por banda, excluindo alfa e preservando a máscara."""
    with rasterio.open(raster_path) as dataset:
        bands = [
            band for band, color in zip(dataset.indexes, dataset.colorinterp)
            if color != ColorInterp.alpha
        ]
        pixels = dataset.read(bands, masked=True)
        valid = ~np.ma.getmaskarray(pixels).any(axis=0)
        thresholds = np.broadcast_to(np.asarray(threshold, dtype=float), (len(bands),))
        binary = (pixels.data >= thresholds[:, None, None]).astype(np.uint8)
        binary[:, ~valid] = 0

        with rasterio.Env(GDAL_TIFF_INTERNAL_MASK=True):
            with rasterio.open(
                output_path, "w", driver="GTiff",
                width=dataset.width, height=dataset.height,
                count=len(bands), dtype="uint8", nodata=None,
                crs=dataset.crs, transform=dataset.transform,
                photometric="MINISBLACK",
            ) as output:
                output.write(binary)
                output.write_mask(valid)
    return output_path


def main() -> None:
    output = mask_raster_by_threshold(RASTER_PATH, THRESHOLD, OUTPUT_PATH)
    print(f"TIFF binário criado: {output}")


if __name__ == "__main__":
    main()
