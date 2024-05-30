import geopandas as gpd
from centerline.geometry import Centerline
import os
import geopandas as gpd
from shapely.geometry import Point, LineString
from shapely.ops import linemerge
from qgis.core import QgsVectorLayer, QgsProject

def calculate_centerline(gdf):
    """
    Calcul de la ligne centrale pour le premier polygone d'un GeoDataFrame.

    :param gdf: GeoDataFrame contenant des polygones
    :return: GeoDataFrame contenant la ligne centrale et le nombre de lignes
    """
    # Sélection du premier polygone du GeoDataFrame
    polygon = gdf.geometry.iloc[0]

    # Définition des attributs de la ligne centrale
    attributes = {"id": 1, "name": "polygon", "valid": True}
    
    # Calcul de la ligne centrale
    centerline = Centerline(polygon, **attributes)
    
    # Création d'un GeoDataFrame pour stocker la ligne centrale
    centerline_gdf = gpd.GeoDataFrame(geometry=[line for line in centerline.geometry.geoms])
    
    # Nombre total de lignes en sortie
    lines_number = len(centerline_gdf)
    
    return centerline_gdf, lines_number

def clean_centerline(centerline_gdf, crs, directory_path):
    """
    Nettoie la ligne centrale pour enlever les extrémités isolées ou non connectées.

    :param centerline_gdf: GeoDataFrame contenant la ligne centrale
    :param crs: Système de coordonnées
    :param directory_path: Chemin vers le répertoire d'enregistrement
    :return: Tuple contenant le GeoDataFrame nettoyé
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
    num_original_lines = len(individual_lines)
    num_dangles = len(dangles)
    print("Nombre de dangles détectés :", num_dangles)
    
    filtered_lines = [line for line in individual_lines if Point(line.coords[0]) not in dangles and Point(line.coords[-1]) not in dangles]
    merged_filtered_line = linemerge(filtered_lines)
    
    # S'assurer que merged_filtered_line est une liste
    if isinstance(merged_filtered_line, LineString):
        merged_filtered_line = [merged_filtered_line]
    
    merged_filtered_gdf = gpd.GeoDataFrame(geometry=merged_filtered_line)
    merged_filtered_gdf.crs = crs
    output_shapefile_path = os.path.join(directory_path, "clean_centerline.shp")
    merged_filtered_gdf.to_file(output_shapefile_path, driver='ESRI Shapefile')
    
    if not merged_filtered_gdf.empty:
        print("Export réussi:", output_shapefile_path)
        # Ajout de la couche directement au projet
        layer = QgsVectorLayer(output_shapefile_path, "clean_centerline", "ogr")
        if not layer.isValid():
            print("La couche n'est pas valide.")
            return
        QgsProject.instance().addMapLayer(layer)
        print("Fichier clean_centerline.shp ajouté dans le projet avec succès")
    else:
        print("Géométrie vide")

    return merged_filtered_gdf