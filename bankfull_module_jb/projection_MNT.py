from qgis.core import QgsPointXY, QgsRaster, QgsGeometry
import pandas as pd

def nearest_points_RivCentre(centerline_layer, points_transects):
    
    """
    Trouve le point le plus proche sur la couche de ligne centrale pour chaque point de transect.

    :param centerline_layer: (QgsVectorLayer) Couche de ligne centrale.
    :param points_transects: (list) Liste de tuples contenant les coordonnées des points de transect.

    :return: (tuple) Tuple contenant l'indice du point de transect le plus proche sur la ligne centrale
        et les coordonnées de ce point.
    """

    nearest_point_index = None
    min_distance = float('inf')
    nearest_points = []
    for i, point_coords in enumerate(points_transects):
        # Créer un objet QgsPoint à partir des coordonnées du point
        point = QgsPointXY(point_coords[0], point_coords[1])
        # Convertir le point en objet QgsGeometry
        point_geometry = QgsGeometry.fromPointXY(point)
        
        # Parcourir toutes les entités de la couche centerline_layer pour trouver la plus proche
        for feature in centerline_layer.getFeatures():
            centerline_geometry = feature.geometry()
            # Calculer la distance entre le point et la ligne centrale
            distance = centerline_geometry.distance(point_geometry)
            # Mise à jour de l'index du point le plus proche si la distance actuelle est plus petite
            if distance < min_distance:
                nearest_point_index = i
                min_distance = distance
                nearest_points = [point_coords]
    return nearest_point_index, nearest_points

def echantillonner_mnt(transect, mnt, nb_pts):
    """
    Échantillonne le modèle numérique de terrain (MNT) le long du transect.

    :param transect: (QgsGeometry) Géométrie du transect.
    :param mnt: (QgsRasterLayer) Couche du modèle numérique de terrain (MNT).
    :param nb_pts: (int) Nombre de points à échantillonner le long du transect.

    :return: (list) Liste de tuples contenant les coordonnées 3D des points échantillonnés le long du transect.
    """

    if transect is None:  # Vérification si la géométrie de la tranche est nulle
        print("La géométrie de la tranche est nulle. Traitement ignoré.")
        return []
    
    points_3d = [] # Stockage des coordonnées 3D
    pixelSizeX = mnt.rasterUnitsPerPixelX()
    increment_distance = pixelSizeX
    
    for i in range(nb_pts):
        distance = i * increment_distance
        point = transect.interpolate(distance)
        x, y = point.asPoint()
        # Lire l'altitude du MNT au point donné
        ident = mnt.dataProvider().identify(QgsPointXY(x, y), QgsRaster.IdentifyFormatValue)
        z = ident.results()[1]
        # Ajout des coordonnées 3D à la liste
        points_3d.append((x, y, z))
        
    # Inverser la liste des points pour que le premier point soit à gauche
    points_3d.reverse()
    
    return points_3d