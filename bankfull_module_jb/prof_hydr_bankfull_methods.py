import os
import numpy as np
import pandas as pd
from scipy.signal import find_peaks


def find_bankfull_M1(spline_results: list, directory_path) -> list:
    """
    Trouve l'altitude maximale de débordement pour chaque transect.
    :param spline_results: Liste de tuples (group_name, ref_altitude_smooth, profondeur_hydraulique_smooth) représentant
        les résultats du lissage de la courbe de profondeur hydraulique
        group_name = numéro du profil

    :return: (list) Liste de tuples contenant l'indice du transect et l'altitude maximale
        de débordement pour ce transect.
    """
    altitude_max_amplitudes = []
    # print(spline_results)

    for (
        idx,
        ref_altitude_smooth,
        profondeur_hydraulique_smooth,
    ) in spline_results:

        profondeur_hydraulique_smooth_array = np.array(profondeur_hydraulique_smooth)

        peaks, _ = find_peaks(profondeur_hydraulique_smooth_array, distance=10)
        valleys, _ = find_peaks(-profondeur_hydraulique_smooth_array, distance=10)

        if peaks.any() and valleys.any():
            altitude_at_max_amplitude = None
            max_amplitude = -np.inf

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

    return altitude_max_amplitudes


def find_bankfull_M2(spline_results: list, directory_path) -> list:
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
    bankfull_values = []  # Liste pour stocker les altitudes de débordement de tous les transects
    prev_bankfull = None  # Tuple pour stocker l'altitude de débordement du transect précédent

    for idx, ref_altitude_smooth, profondeur_hydraulique_smooth in spline_results:
        profondeur_hydraulique_smooth_np = np.array(profondeur_hydraulique_smooth)
        ref_altitude_smooth_np = np.array(ref_altitude_smooth)  # Conversion en array NumPy
        
        # Trouver les maxima et minima de la profondeur hydraulique
        maxima_smooth, _ = find_peaks(profondeur_hydraulique_smooth_np)
        minima_smooth, _ = find_peaks(-profondeur_hydraulique_smooth_np)
        
        if maxima_smooth.size > 0 and minima_smooth.size > 0:
            amplitudes_smooth = [
                profondeur_hydraulique_smooth_np[max_index] - profondeur_hydraulique_smooth_np[min_index]
                for max_index, min_index in zip(maxima_smooth, minima_smooth)
                if max_index < min_index  # Assure que le minimum vient après le maximum
            ]

            if amplitudes_smooth:
                print(f"Transect {idx}: Amplitudes de rupture = {amplitudes_smooth}")

                # Afficher les amplitudes et les altitudes associées
                for i, amplitude in enumerate(amplitudes_smooth):
                    altitude_at_max_amplitude = ref_altitude_smooth_np[maxima_smooth[i]]
                    print(f"Amplitude {i}: {amplitude}, Altitude associée: {altitude_at_max_amplitude}")

                if idx == 0:
                    # Pour le premier transect, sélectionner l'amplitude maximale
                    max_amplitude_index = np.argmax(amplitudes_smooth)
                    altitude_at_max_amplitude = ref_altitude_smooth_np[maxima_smooth[max_amplitude_index]]
                    alti_bankfull = altitude_at_max_amplitude
                    prev_altitude = altitude_at_max_amplitude
                    print(f"Transect {idx}: Amplitude sélectionnée = {amplitudes_smooth[max_amplitude_index]}")
                    print(f"Transect {idx}: Altitude correspondante = {alti_bankfull}")
                else:
                    # Pour les transects suivants, sélectionner l'amplitude dont l'altitude est la plus proche de celle du transect précédent
                    prev_altitude = prev_bankfull[1]
                    altitude_at_maxima = ref_altitude_smooth_np[maxima_smooth]
                    distances = np.abs(altitude_at_maxima - prev_altitude)
                    closest_amplitude_index = np.argmin(distances)
                    altitude_at_max_amplitude = ref_altitude_smooth_np[maxima_smooth[closest_amplitude_index]]
                    alti_bankfull = altitude_at_max_amplitude
                    print(f"Transect {idx}: Amplitude sélectionnée = {amplitudes_smooth[closest_amplitude_index]}")
                    print(f"Transect {idx}: Altitude correspondante = {alti_bankfull}")
            else:
                alti_bankfull = None
        else:
            alti_bankfull = None

        if alti_bankfull is not None:
            bankfull_values.append((idx, alti_bankfull))
            prev_bankfull = (idx, alti_bankfull)

    # Créer un DataFrame à partir de la liste de tuples
    bankfull_previous_transects = pd.DataFrame(bankfull_values, columns=["x_sec_id", "altitude"])

    # Exporter dans un fichier .csv
    df_output_path = os.path.join(directory_path, "bankfull_previous_transects.csv")
    bankfull_previous_transects.to_csv(df_output_path, sep=",", index=False)
    print(f"Les altitudes ont été exportées avec succès vers : {df_output_path}")

    return bankfull_values