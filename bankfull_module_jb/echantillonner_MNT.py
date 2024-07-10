import pandas as pd
from qgis.core import (
    QgsPointXY,
    QgsRaster,
    QgsGeometry,
    QgsVectorLayer,
    QgsRasterLayer,
)


def nearest_points_RivCentre(
    centerline_layer: QgsVectorLayer, points_transects: list
) -> list:
    """
    Trouve le point le plus proche de la ligne centrale pour chaque profil.

    :param centerline_layer: QgsVectorLayer - Couche de la ligne centrale.
    :param points_transects: list - Liste de tuples contenant les coordonnées
                                 des points des profils.

    :return: list - Liste de tuples contenant l'indice du point du profil le plus proche
                   sur la ligne centrale et les coordonnées de ce point.
    """

    nearest_point_index = None
    min_distance = float("inf")
    nearest_points = []
    for i, point_coords in enumerate(points_transects):
        # Créer un objet QgsPoint à partir des coordonnées du point
        point = QgsPointXY(point_coords[0], point_coords[1])
        # Convertir le point en objet QgsGeometry
        point_geometry = QgsGeometry.fromPointXY(point)

        # Parcourir toutes les entités de la couche de la ligne centrale
        for feature in centerline_layer.getFeatures():
            centerline_geometry = feature.geometry()
            # Calculer la distance entre le point et la ligne centrale
            distance = centerline_geometry.distance(point_geometry)
            # Mise à jour de l'index du point le plus proche
            # si la distance actuelle est plus petite
            if distance < min_distance:
                nearest_point_index = i
                min_distance = distance
                nearest_points = [point_coords]
    return nearest_point_index, nearest_points


def echantillonner_mnt(
        transect: QgsVectorLayer, mnt: QgsRasterLayer, nb_pts: int
) -> list:
    """
    Échantillonne le modèle numérique de terrain (MNT) le long du transect.

    :param transect: Géométrie du transect.
    :param mnt: Couche du modèle numérique de terrain (MNT).
    :param nb_pts: Nombre de points à échantillonner le long du transect.

    :return: (list) Liste de tuples contenant les coordonnées 3D
            des points échantillonnés le long du transect.
    """

    if transect is None:  # Vérification si la géométrie de la tranche est nulle
        print("La géométrie de la tranche est nulle. Traitement ignoré.")
        return []

    points_3d = []  # Stockage des coordonnées 3D
    pixelSizeX = mnt.rasterUnitsPerPixelX()
    increment_distance = pixelSizeX

    for i in range(nb_pts):
        distance = i * increment_distance
        point = transect.interpolate(distance)
        x, y = point.asPoint()
        # Lire l'altitude du MNT au point donné
        ident = mnt.dataProvider().identify(
            QgsPointXY(x, y), QgsRaster.IdentifyFormatValue
        )
        z = ident.results()[1]
        # Ajout des coordonnées 3D à la liste
        points_3d.append((x, y, z))

    # Inverser la liste des points pour que le premier point soit à gauche
    points_3d.reverse()

    return points_3d


def ProjectionMNT(
    transect_layers: QgsVectorLayer,
    centerline_layers: QgsVectorLayer,
    transect_length: float,
    selected_MNT_layer: QgsRasterLayer,
) -> pd.DataFrame:
    """
    Trouve le point le plus proche sur la couche de ligne centrale
    pour chaque point du profil en travers.

    :param centerline_layer: Couche de ligne centrale.
    :param points_transects: Liste de tuples contenant les coordonnées des
                            points du profil.

    :return: DataFrame contenant l'indice du point du profil le plus proche de
            la ligne centrale et les coordonnées de ce point.
    """
    transect_layer = transect_layers[0]
    centerline_layer = centerline_layers[0]
    pixelSizeX = selected_MNT_layer.rasterUnitsPerPixelX()

    # Calculer le nombre de points en fonction de la
    # résolution et de la longueur des transects
    nb_pts = int(transect_length / pixelSizeX)
    print("Nombre de points interpolés le long des transects  :", nb_pts)

    points_transects = []

    for transect_num, feature in enumerate(transect_layer.getFeatures()):
        geom = feature.geometry()
        transect_points = echantillonner_mnt(geom, selected_MNT_layer, nb_pts)
        nearest_point_index, _ = nearest_points_RivCentre(
            centerline_layer, transect_points
        )
        # Création d'une liste contenant des booléens indiquant
        # si chaque point est le plus proche de la ligne centrale
        rivcentre_column = [
            i == nearest_point_index for i in range(len(transect_points))
        ]
        # Ajout d'une colonne 'RivCentre' remplie de
        # valeurs booléennes à la liste points_transects
        points_transects.extend(
            [
                (transect_num, i, point[0], point[1], point[2], is_nearest)
                for i, (point, is_nearest) in enumerate(
                    zip(transect_points, rivcentre_column)
                )
            ]
        )
    # Création de la DataFrame df_transects à partir de la liste points_transects
    df_transects = pd.DataFrame(
        points_transects,
        columns=[
            "x_sec_id",
            "x_sec_order",
            "POINT_X",
            "POINT_Y",
            "POINT_Z",
            "RivCentre",
        ],
    )
    return df_transects
