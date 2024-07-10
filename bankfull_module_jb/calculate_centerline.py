import os

import geopandas as gpd
from centerline.geometry import Centerline
from shapely.geometry import Point
from shapely.ops import linemerge


def calculate_centerline(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Calcul de la ligne centrale d'un polygone.

    :param gdf: GeoDataFrame contenant le polygone.
    :return: GeoDataFrame contenant la ligne centrale.
    """
    # Sélection du premier polygone du GeoDataFrame
    polygon = gdf.geometry.iloc[0]

    # Définition des attributs de la ligne centrale
    attributes = {"id": 1, "name": "polygon", "valid": True}

    # Calcul de la ligne centrale
    centerline = Centerline(polygon, **attributes)

    # Création d'un GeoDataFrame pour stocker la ligne centrale
    centerline_gdf = gpd.GeoDataFrame(
        geometry=[line for line in centerline.geometry.geoms]
    )

    return centerline_gdf


def clean_centerline(
    centerline_gdf: gpd.GeoDataFrame, crs: str, directory_path: str
) -> gpd.GeoDataFrame:
    """
    Nettoie la ligne centrale pour enlever les extrémités isolées ou non connectées.

    :param centerline_gdf: GeoDataFrame contenant la ligne centrale
    :param crs: Système de coordonnées
    :param directory_path: Chemin vers le répertoire d'enregistrement
    :return: GeoDataFrame de la ligne centrale nettoyée
    """
    # Nettoyage de la ligne centrale
    merged_line = linemerge(centerline_gdf.geometry.unary_union)
    individual_lines = list(merged_line.geoms)

    endpoints = []
    for line in individual_lines:
        endpoints.append(line.coords[0])
        endpoints.append(line.coords[-1])

    point_counts = {}
    for point in endpoints:
        if point not in point_counts:
            point_counts[point] = 1
        else:
            point_counts[point] += 1

    # Suppression des extrémités isolées ou non connectées
    dangles = [Point(point) for point, count in point_counts.items() if count == 1]
    num_dangles = len(dangles)
    print("Nombre de dangles détectés :", num_dangles)

    filtered_lines = [
        line
        for line in individual_lines
        if Point(line.coords[0]) not in dangles
        and Point(line.coords[-1]) not in dangles
    ]
    merged_filtered_line = linemerge(filtered_lines)
    merged_filtered_gdf = gpd.GeoDataFrame(
        {"geometry": [merged_filtered_line]}, crs=crs
    )

    output_shapefile_path = os.path.join(directory_path, "clean_centerline.shp")
    merged_filtered_gdf.to_file(output_shapefile_path, driver="ESRI Shapefile")

    return merged_filtered_gdf
