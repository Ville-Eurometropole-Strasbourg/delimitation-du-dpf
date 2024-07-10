import numpy as np
import pandas as pd
from scipy.signal import savgol_filter
from scipy.signal import find_peaks


def curve_Savitzky_Golay(
    curve_data: pd.DataFrame,
    cross_section_data: pd.DataFrame,
    param_dist_curve: float,
    param_height_curve: float,
    param_prominence_curve: float,
) -> list:
    """
    Applique le filtre Savitzky-Golay pour lisser les données de courbure
    le long de chaque transect, détecte les pics de courbure significatifs et
    projette les points correspondants sur le profil en travers.

    :param curve_data: Données de courbure par profil.
    :param cross_section_data: Données des profil en travers.
    :param param_dist_curve: Distance minimale entre les pics de courbure détectés.
    :param param_height_curve: Hauteur minimale des pics de courbure détectés.
    :param param_prominence_curve: Prominence minimale des pics de courbure détectés.

    :return: Liste de tuples contenant les données projetées pour chaque transect:
             (x_sec_id, projected_distances, projected_altitudes).
             - x_sec_id: Identifiant du transect.
             - projected_distances: Distances projetées des pics sur le profil.
             - projected_altitudes: Altitudes correspondantes des pics projetés.
    """

    # Grouper les données de courbure par x_sec_id
    grouped_data = curve_data.groupby("x_sec_id")
    # Grouper les données brutes par x_sec_id
    grouped_cross_section_data = cross_section_data.groupby("x_sec_id")

    all_transect_data = []

    # Itérer sur chaque groupe
    for x_sec_id, group in grouped_data:
        projected_distances = []
        projected_altitudes = []
        print("Transect ID:", x_sec_id)  # Afficher l'ID du transect
        # Données de courbure pour ce transect
        curve = group["POINT_Z"]
        # Lissage de la courbe de courbure à l'aide d'un filtre
        smoothed_curve = savgol_filter(curve, window_length=9, polyorder=2)
        # print("smoothed_curve :", smoothed_curve)

        first_derivative = np.gradient(smoothed_curve)

        # Détection des pics dans la courbe de courbure
        peaks, _ = find_peaks(
            first_derivative,
            distance=param_dist_curve,
            height=param_height_curve,
            prominence=param_prominence_curve,
        )
        print(
            "Indices des pics de courbure détéctés:", peaks
        )  # Afficher les pics détectés

        # Filtrage des pics qui correspondent à des surfaces en eau
        filtered_peaks = [peak for peak in peaks if abs(smoothed_curve[peak]) > 0.001]
        print(
            "Indices des pics filtrés hors des zones en eau:", filtered_peaks
        )  # Afficher les pics filtrés

        # Grouper les données cross_section_data pour ce transect
        cross_section_group = grouped_cross_section_data.get_group(x_sec_id)

        # Réinitialiser l'index de cross_section_group
        cross_section_group.reset_index(drop=True, inplace=True)

        # Identification des berges
        river_center = cross_section_group[cross_section_group["RivCentre"] == True]
        river_banks = cross_section_group[cross_section_group["RivCentre"] == False]

        # Calcul de la moyenne des altitudes avant et après le point central
        mean_altitude_before = river_banks[
            river_banks["Distance"] < river_center.iloc[0]["Distance"]
        ]["POINT_Z"].mean()
        mean_altitude_after = river_banks[
            river_banks["Distance"] > river_center.iloc[0]["Distance"]
        ]["POINT_Z"].mean()
        print("Altitude moyenne à gauche du point central:", mean_altitude_before)
        print("Altitude moyenne à droite du point central:", mean_altitude_after)

        # Identification de la berge la plus basse
        if mean_altitude_before < mean_altitude_after:
            min_bank = "gauche"
        else:
            min_bank = "droite"
        print("Lowest bank:", min_bank)  # Afficher la berge la plus basse

        # Sélection des points sur la berge la plus basse
        if min_bank == "gauche":
            bank_indices = (
                river_banks[
                    river_banks["Distance"] < river_center.iloc[0]["Distance"]
                ].index
                - cross_section_group.index[0]
            )
        else:
            bank_indices = (
                river_banks[
                    river_banks["Distance"] > river_center.iloc[0]["Distance"]
                ].index
                - cross_section_group.index[0]
            )

        # Filtrage des pics sur la berge la plus basse
        filtered_peaks_on_lowest_bank = [
            peak for peak in filtered_peaks if peak in bank_indices
        ]
        print(
            "Pics filtrés sur la berge la plus basse:", filtered_peaks_on_lowest_bank
        )  # Afficher les pics sur la berge la plus basse

        # Projection des points filtrés sur le profil en travers
        projected_distances.extend(
            cross_section_group.loc[filtered_peaks_on_lowest_bank, "Distance"]
        )
        projected_altitudes.extend(
            cross_section_group.loc[filtered_peaks_on_lowest_bank, "POINT_Z"]
        )

        all_transect_data.append((x_sec_id, projected_distances, projected_altitudes))

    return all_transect_data
