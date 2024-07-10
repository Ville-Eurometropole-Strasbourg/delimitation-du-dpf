import pandas as pd


def CalculerProfHydr(area_trapezes_data: pd.DataFrame) -> list:
    """
    Calcul de l'indicateur de profondeur hydraulique.

    Cette fonction identifie la plus grande aire négative pour chaque profil.
    L'indicateur de profondeur hydraulique est déterminé comme le rapport de
    cette plus grande aire négative sur la largeur au miroir. La largeur au
    miroir correspond à la distance entre les points d'intersection qui délimitent
    la section mouillée du profil.

    :param area_trapezes_data: Informations sur les aires calculées entre les courbes
                               à chaque itération.
    :return: Indicateur de profondeur hydraulique pour chaque profil.
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
