import os
import pandas as pd
import numpy as np
from scipy.signal import find_peaks
from scipy.interpolate import make_interp_spline


def CalculerPeaks(
        dist_pic: float, pts_interp: int, prominence: float, directory_path: str
) -> tuple:
    """
    Lissage d'une courbe et calcul des minimums et maximums locaux.

    :param dist_pic: Distance minimale entre les pics de profondeur hydraulique.
    :param pts_interp: Nombre de points pour l'interpolation de la courbe lissée.
    :param prominence: Prominence minimale des pics de profondeur hydraulique détectés.
    :param directory_path: Chemin du répertoire contenant le fichier "prof_hydr.csv".

    :return: Tuple contenant deux listes :
        - Liste de tuples représentant les résultats du lissage de la courbe.
        - Liste de listes représentant les données des pics détectés.
    """

    # Récupération des données présentes dans la DataFrame "prof_hydr.csv"
    prof_hydr_data = pd.read_csv(os.path.join(directory_path, "prof_hydr.csv"))

    # Groupement des données par profils en travers
    grouped_data = prof_hydr_data.groupby("x_sec_id")

    spline_results = []
    peaks_valleys_data = []

    for idx, group_data in grouped_data:
        ref_altitude = group_data["ref_altitude"].to_numpy()
        profondeur_hydraulique = group_data["profondeur_hydraulique"].to_numpy()

        # Lissage de la courbe en utilisant "make_interp_spline"
        spline = make_interp_spline(ref_altitude, profondeur_hydraulique, k=1)
        ref_altitude_smooth = np.linspace(
            ref_altitude.min(), ref_altitude.max(), pts_interp
        )
        profondeur_hydraulique_smooth = spline(ref_altitude_smooth)
        spline_results.append(
            (
                idx,
                ref_altitude_smooth.tolist(),
                profondeur_hydraulique_smooth.tolist(),
            )
        )
        # Détections des minimums et maximums locaux
        peaks, _ = find_peaks(
            profondeur_hydraulique_smooth, distance=dist_pic, prominence=prominence
        )
        valleys, _ = find_peaks(
            -profondeur_hydraulique_smooth, distance=dist_pic, prominence=prominence
        )

        # Récupérer les maximums locaux
        for peak_index in peaks:
            peaks_valleys_data.append(
                [
                    idx,
                    ref_altitude_smooth[peak_index],
                    profondeur_hydraulique_smooth[peak_index],
                    "Maximum local",
                ]
            )
        # Récupérer les minimums locaux
        for valley_index in valleys:
            peaks_valleys_data.append(
                [
                    idx,
                    ref_altitude_smooth[valley_index],
                    profondeur_hydraulique_smooth[valley_index],
                    "Minimum local",
                ]
            )
    # On retourne les données de la courbe lissée et
    # les données des maximums/minimums locaux
    return spline_results, peaks_valleys_data
