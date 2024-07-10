import geopandas as gpd
from shapely.geometry import Point, LineString
import os
from qgis.core import QgsProject, QgsVectorLayer
import numpy as np


def get_angle(pt1, pt2):
    """Calcul d'un angle en degré entre deux points.
    :param pt1: Point 1.
    :param pt2: Point 2.
    """
    x_diff = pt2.x - pt1.x
    y_diff = pt2.y - pt1.y
    return np.degrees(np.arctan2(y_diff, x_diff))


def get_point1(pt, bearing, dist):
    """Calcul d'un nouveau point à une distance et un angle donnés
    par rapport à un point de départ.

    :param pt: Point de départ.
    :param bearing: Angle de direction initiale en degré.
    :param dist: Distance à laquelle le nouveau point doit être calculé.
    """
    angle = bearing + 90
    bearing = np.radians(angle)
    x = pt.x + dist * np.cos(bearing)
    y = pt.y + dist * np.sin(bearing)
    return Point(x, y)


def get_point2(pt, bearing, dist):
    """Fonction similaire à get_point1 mais utilise directemlent l'angle sans ajustement

    :param pt: Point de départ.
    :param bearing: Angle de direction initiale en degré.
    :param dist: Distance à laquelle le nouveau point doit être calculé.
    """

    bearing = np.radians(bearing)
    x = pt.x + dist * np.cos(bearing)
    y = pt.y + dist * np.sin(bearing)
    return Point(x, y)


def CalculTransects(
    transect_length: float, transect_spacing: float, directory_path: str, crs: str
) -> None:
    """Calcul des transects perpendiculaires à la ligne centrale
    :param transect_length: Longueur des profils.
    :param transect_spacing: Pas d'espacement entre les profils.
    :param directory_path: Chemin vers le répertoire d'enregistrement.
    :param crs: SCR du projet.
    """

    distance = transect_spacing
    tick_length = transect_length

    layer = os.path.join(directory_path, "ligne_centrale.gpkg")
    gdf = gpd.read_file(layer)

    tick_lines = []

    for idx, row in gdf.iterrows():
        line = row["geometry"]
        list_points = []
        current_dist = distance
        line_length = line.length
        list_points.append(Point(list(line.coords)[-1]))

        while current_dist < line_length:
            list_points.append(line.interpolate(line_length - current_dist))
            current_dist += distance
        list_points.append(Point(list(line.coords)[0]))
        list_points.reverse()

        for num, pt in enumerate(list_points, 1):
            if num == 0:
                angle = get_angle(pt, list_points[num])
                line_end_1 = get_point1(pt, angle, tick_length / 2)
                angle = get_angle(line_end_1, pt)
                line_end_2 = get_point2(line_end_1, angle, tick_length)
                tick_lines.append(
                    LineString(
                        [(line_end_1.x, line_end_1.y), (line_end_2.x, line_end_2.y)]
                    )
                )
            if num < len(list_points) - 1:
                angle = get_angle(pt, list_points[num])
                line_end_1 = get_point1(list_points[num], angle, tick_length / 2)
                angle = get_angle(line_end_1, list_points[num])
                line_end_2 = get_point2(line_end_1, angle, tick_length)
                tick_lines.append(
                    LineString(
                        [(line_end_1.x, line_end_1.y), (line_end_2.x, line_end_2.y)]
                    )
                )
            if num == len(list_points):
                angle = get_angle(list_points[num - 2], pt)
                line_end_1 = get_point1(pt, angle, tick_length / 2)
                angle = get_angle(line_end_1, pt)
                line_end_2 = get_point2(line_end_1, angle, tick_length)
                tick_lines.append(
                    LineString(
                        [(line_end_1.x, line_end_1.y), (line_end_2.x, line_end_2.y)]
                    )
                )

    # Inverser les tick_lines pour correspondre à la numérotation inversée
    tick_lines.reverse()

    # Ajouter des attributs d'identifiant inversés aux lignes
    tick_lines_with_ids = []
    num_transects = len(tick_lines)
    for i, line in enumerate(tick_lines):
        tick_lines_with_ids.append({"geometry": line, "id": num_transects - 1 - i})

    output_path = os.path.join(directory_path, "profils.gpkg")
    gdf_tick_lines = gpd.GeoDataFrame(tick_lines_with_ids)
    gdf_tick_lines.crs = crs
    gdf_tick_lines.to_file(output_path, driver="GPKG")

    try:
        layer = QgsVectorLayer(output_path, "profils", "ogr")
        QgsProject.instance().addMapLayer(layer)
    except Exception as e:
        print(
            "Erreur lors de l'ajout de la couche des profils en travers au projet :", e
        )
