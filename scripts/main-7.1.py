from math import ceil

import geopandas as gp
from shapely.geometry import box

VECTOR_PATH = "vectors_case_2/plantio_area.geojson"
GRID_PATH = "vectors_case_2/grid.geojson"


def create_grid(bounds: gp.GeoDataFrame, cell_size: float) -> gp.GeoDataFrame:
    """Cria uma grade em metros recortada pelo contorno da área.

    ``bounds`` é o GeoDataFrame da área de interesse. Seu CRS deve estar
    informado; coordenadas não métricas são reprojetadas para UTM.
    As células nas bordas podem ser menores que cell_size.
    """

    axes = bounds.crs.axis_info[:2]
    is_metric = (
        bounds.crs.is_projected
        and len(axes) == 2
        and all(axis.unit_conversion_factor == 1.0 for axis in axes)
    )
    area = bounds
    if not is_metric:
        metric_crs = bounds.estimate_utm_crs()
        area = bounds.to_crs(metric_crs)

    minx, miny, maxx, maxy = area.total_bounds
    width, height = maxx - minx, maxy - miny
    columns = ceil(width / cell_size)
    rows = ceil(height / cell_size)

    cells = [
        box(
            minx + column * cell_size,
            miny + row * cell_size,
            minx + (column + 1) * cell_size,
            miny + (row + 1) * cell_size,
        )
        for column in range(columns)
        for row in range(rows)
    ]

    grid = gp.GeoDataFrame(geometry=cells, crs=area.crs)
    grid = gp.clip(grid, area, keep_geom_type=True)
    return grid.loc[grid.area > 0].reset_index(drop=True)


def main() -> None:
    gdf = gp.read_file(VECTOR_PATH)
    grid = create_grid(gdf, cell_size=200)
    grid.to_file(GRID_PATH, driver="GeoJSON", index=False)
    
    
if __name__ == "__main__":
    main()  
 