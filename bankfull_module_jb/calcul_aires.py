import numpy as np
from scipy.interpolate import interp1d
from scipy.spatial.distance import euclidean
import matplotlib.pyplot as plt


def calculer_aire(
    dist: list, alti: list, alti_ref: list, filtrage_aires: float
) -> list:
    """
    Calcul des aires entre deux courbes.
    Les aires sont calculées et filtrées selon un critère spécifié par l'utilisateur.

    :param dist: Liste des distances le long du profil en travers.
    :param alti: Liste des altitudes du profil en travers.
    :param alti_ref: Liste des altitudes uniques triées dans l'ordre croissant.
    :param filtrage_aires: Critère de filtrage des aires (aire minimale à considérer).

    :return: Liste de tuples contenant pour chaque altitude de référence :
             - Indice de l'altitude de référence.
             - Liste des aires calculées (au-dessus ou en-dessous de la référence).
             - Liste des distances entre les points d'intersection.
             - Altitude de référence.
             - Liste des indices des points d'intersection.
    """

    areas_iteration = []

    # Boucle sur les altitudes de référence
    for i in range(len(alti_ref)):
        dref = [(dist[j], alti_ref[i]) for j in range(len(dist))]
        dist_dref, alti_dref = zip(*dref)

        # Définition des courbes
        dist_interp = np.linspace(min(dist), max(dist), 1000)
        alti_d1_interp = interp1d(dist, alti, kind="linear")(dist_interp)
        alti_dref_interp = interp1d(dist_dref, alti_dref, kind="linear")(dist_interp)
        # Recherche des indices des points d'intersection entre les deux courbes

        intersection_indices = (
            np.where(np.diff(np.sign(alti_d1_interp - alti_dref_interp)))[0] + 1
        )

        intersection_points = []
        distances = []
        intersection_indices_list = []

        # Vérification si au moins 1 intersection trouvée
        if len(intersection_indices) > 0:
            intersection_indices = np.insert(intersection_indices, 0, 0)
            intersection_indices = np.append(intersection_indices, len(dist_interp) - 1)

            # Création de zones de couleur pour chaque aire créée
            color_zones = [
                (
                    intersection_indices[j],
                    intersection_indices[j + 1],
                    plt.cm.jet(j / len(intersection_indices)),
                )
                for j in range(len(intersection_indices) - 1)
            ]

            areas_iteration_current = []

            # Parcours des zones de couleur
            for start_idx, end_idx, color in color_zones:
                # Calcul de l'aire entre le profil et la droite de référence
                area = np.trapz(
                    alti_dref_interp[start_idx:end_idx]
                    - alti_d1_interp[start_idx:end_idx],
                    x=dist_interp[start_idx:end_idx],
                )
                # Conversion en valeur absolue de l'aire
                area = abs(area)
                # Vérification du critère de filtrage
                if area > filtrage_aires:
                    # Calcul du centre de gravité de l'aire pour déterminer si
                    # elle est au-dessus ou en-dessous de l'altitude de référence
                    y_centroid = np.trapz(
                        (
                            alti_dref_interp[start_idx:end_idx]
                            + alti_d1_interp[start_idx:end_idx]
                        )
                        / 2
                        * (
                            alti_dref_interp[start_idx:end_idx]
                            - alti_d1_interp[start_idx:end_idx]
                        ),
                        x=dist_interp[start_idx:end_idx],
                    ) / np.trapz(
                        alti_dref_interp[start_idx:end_idx]
                        - alti_d1_interp[start_idx:end_idx],
                        x=dist_interp[start_idx:end_idx],
                    )
                    # Si y_centroïde est supérieur à la droite de référence
                    if y_centroid > alti_ref[i]:
                        # Ajout d'un tuple indiquant que l'aire est au dessus
                        # de la droite de référence
                        areas_iteration_current.append((area, "above", alti_ref[i]))
                    else:
                        # L'aire est en dessous de la droite de référence
                        areas_iteration_current.append((area, "below", alti_ref[i]))

                    area *= -1
                    intersection_point = (
                        dist_interp[start_idx],
                        alti_dref_interp[start_idx],
                        alti_d1_interp[start_idx],
                    )

                    intersection_points.append(intersection_point)
                    intersection_indices_list.append(start_idx)
                    if start_idx != end_idx:
                        intersection_point = (
                            dist_interp[end_idx],
                            alti_dref_interp[end_idx],
                            alti_d1_interp[end_idx],
                        )
                        intersection_points.append(intersection_point)
                        intersection_indices_list.append(end_idx)
                        # Distance euclidienne entre les deux points d'intersection
                        distance_between_intersections = euclidean(
                            intersection_points[-2], intersection_points[-1]
                        )
                        distances.append(distance_between_intersections)
            # Ajout de informations de l'itération i à la liste globale
            areas_iteration.append(
                (
                    i,
                    areas_iteration_current,
                    distances,
                    alti_ref[i],
                    intersection_indices_list,
                )
            )

    return areas_iteration
