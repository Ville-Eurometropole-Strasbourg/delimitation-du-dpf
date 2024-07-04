import pandas as pd
import os


def CalculerProfHydr(area_trapezes_data):
    """Calcul de l'indicateur de profondeur hydraulique

    :param area_trapezes_data: Informations sur les aires calculées entre les courbes à chaque itération
    """

    largest_negative_area = []

    # Sélection des lignes où l'aire est inférieure à zéro
    negative_area = area_trapezes_data.loc[(area_trapezes_data["area"] < 0)]

    # Grouper par transect et itération, puis trouver l'indice de la ligne
    # avec la plus grande aire négative
    idx = negative_area.groupby(["x_sec_id", "iteration"])["area"].idxmin()

    # Sélectionner les lignes correspondant aux indices trouvés
    largest_negative_area = area_trapezes_data.loc[idx]

    # Calcul de la profondeur hydraulique
    largest_negative_area["profondeur_hydraulique"] = (
        largest_negative_area["area"]
        / largest_negative_area["distance_between_intersections"]
        * -1
    )

    return largest_negative_area
