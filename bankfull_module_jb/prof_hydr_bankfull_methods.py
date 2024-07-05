import os
import numpy as np
import pandas as pd
from scipy.signal import find_peaks


def find_bankfull_M1(spline_results: list, directory_path, dist_pic) -> list:
    """
    Trouve l'altitude maximale de débordement pour chaque transect et affiche les amplitudes positives pour chaque transect.
    :param spline_results: Liste de tuples (group_name, ref_altitude_smooth, profondeur_hydraulique_smooth) représentant
        les résultats du lissage de la courbe de profondeur hydraulique.
    :param directory_path: Chemin du répertoire pour sauvegarder le fichier de sortie.
    :return: (list) Liste de tuples contenant l'indice du transect et l'altitude maximale
        de débordement pour ce transect.
    """
    altitude_max_amplitudes = []
    amplitudes_per_transect = {}  # Dictionnaire pour stocker les amplitudes par profil

    for (
        idx,
        ref_altitude_smooth,
        profondeur_hydraulique_smooth,
    ) in spline_results:

        profondeur_hydraulique_smooth_array = np.array(profondeur_hydraulique_smooth)

        peaks, _ = find_peaks(profondeur_hydraulique_smooth_array, distance=dist_pic)
        valleys, _ = find_peaks(-profondeur_hydraulique_smooth_array, distance=dist_pic)

        if peaks.any() and valleys.any():
            altitude_at_max_amplitude = None
            max_amplitude = -np.inf
            amplitudes_for_this_transect = []

            for peak_index in peaks:
                for valley_index in valleys:
                    if valley_index > peak_index:
                        amplitude = (
                            profondeur_hydraulique_smooth[peak_index]
                            - profondeur_hydraulique_smooth[valley_index]
                        )
                        if amplitude > max_amplitude:
                            max_amplitude = amplitude
                            altitude_at_max_amplitude = ref_altitude_smooth[peak_index]

                        # Ajouter toutes les amplitudes pour chaque transect
                        if amplitude is not None:
                            # amplitudes_for_this_transect.append(amplitude)
                            amplitudes_for_this_transect.append(abs(amplitude))

            if amplitudes_for_this_transect:
                amplitudes_per_transect[idx] = amplitudes_for_this_transect

            if altitude_at_max_amplitude is not None:
                altitude_max_amplitudes.append((idx, altitude_at_max_amplitude))

    # Créer un DataFrame à partir de la liste de tuples
    bankfull_max_amplitude = pd.DataFrame(
        altitude_max_amplitudes, columns=["x_sec_id", "altitude"]
    )
    # Export dans un fichier .csv
    df_output_path = os.path.join(directory_path, "bankfull_max_amplitude.csv")
    bankfull_max_amplitude.to_csv(df_output_path, sep=",", index=False)
    print(f"Les altitudes ont été exportées avec succès vers : {df_output_path}")

    return altitude_max_amplitudes, amplitudes_per_transect


def find_bankfull_M2(spline_results: list, directory_path, dist_pic) -> list:
    """
    Trouve l'altitude de débordement pour chaque profil en se basant sur l'altitude
    de débordement du profil précédent. L'altitude de débordement du premier profil
    est déterminée conformément à la fonction find_bankfull_M1.
    :param spline_results: Liste de tuples (idx, ref_altitude_smooth, profondeur_hydraulique_smooth) représentant
        les résultats du lissage de la courbe de profondeur hydraulique.
    :param directory_path: Chemin du répertoire pour sauvegarder le fichier de sortie.
    :return: Liste de tuples contenant l'indice du profil et l'altitude de débordement
        pour ce profil.
    """

    bankfull_values = []
    prev_bankfull = None

    # Appel à find_bankfull_M1 pour obtenir les altitudes maximales et les amplitudes par transect
    _, amplitudes_per_transect = find_bankfull_M1(spline_results, directory_path, dist_pic)

    for idx, ref_altitude_smooth, profondeur_hydraulique_smooth in spline_results:
        profondeur_hydraulique_smooth_np = np.array(profondeur_hydraulique_smooth)
        ref_altitude_smooth_np = np.array(ref_altitude_smooth)

        maxima_smooth, _ = find_peaks(profondeur_hydraulique_smooth_np, distance=dist_pic)
        minima_smooth, _ = find_peaks(-profondeur_hydraulique_smooth_np, distance=dist_pic)

        if maxima_smooth.size > 0 and minima_smooth.size > 0:
            if idx == 0:
                # Utiliser la même méthode que M1 pour le premier transect
                max_amplitude = -np.inf
                altitude_at_max_amplitude = None
                for peak_index in maxima_smooth:
                    for valley_index in minima_smooth:
                        if valley_index > peak_index:
                            amplitude = (
                                profondeur_hydraulique_smooth[peak_index]
                                - profondeur_hydraulique_smooth[valley_index]
                            )
                            if amplitude > max_amplitude:
                                max_amplitude = amplitude
                                altitude_at_max_amplitude = ref_altitude_smooth[peak_index]

                if altitude_at_max_amplitude is not None:
                    alti_bankfull = altitude_at_max_amplitude
                    prev_altitude = alti_bankfull
                    print(f"Altitude de débordement pour le profil {idx}: {alti_bankfull}")
            else:
                if amplitudes_per_transect.get(idx):
                    prev_altitude = prev_bankfull[1]

                    # Trouver l'amplitude dont l'altitude est la plus proche de celle du profil précédent
                    amplitude_at_maxima = ref_altitude_smooth_np[maxima_smooth]
                    distances = np.abs(amplitude_at_maxima - prev_altitude)
                    closest_amplitude_index = np.argmin(distances)
                    altitude_previous_amplitude = ref_altitude_smooth_np[
                        maxima_smooth[closest_amplitude_index]
                    ]
                    alti_bankfull = altitude_previous_amplitude
                    print(f"Altitude de débordement pour le profil {idx}: {alti_bankfull}")
                else:
                    alti_bankfull = None
        else:
            alti_bankfull = None

        if alti_bankfull is not None:
            bankfull_values.append((idx, alti_bankfull))
            prev_bankfull = (idx, alti_bankfull)

    # Créer un DataFrame à partir de la liste de tuples
    bankfull_previous_transects = pd.DataFrame(
        bankfull_values, columns=["x_sec_id", "altitude"]
    )

    # Exporter dans un fichier .csv
    df_output_path = os.path.join(directory_path, "bankfull_previous_transects.csv")
    bankfull_previous_transects.to_csv(df_output_path, sep=",", index=False)
    print(f"Les altitudes ont été exportées avec succès vers : {df_output_path}")

    return bankfull_values