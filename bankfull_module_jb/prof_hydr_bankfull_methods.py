import os
import numpy as np
import pandas as pd
from scipy.signal import find_peaks

def find_bankfull_M1(spline_results, directory_path):
    """
    Trouve l'altitude maximale de débordement pour chaque transect.
    :param spline_results: (list) Liste de tuples (idx, x_smooth, y_smooth) représentant
        les résultats de l'interpolation par spline pour chaque transect.

    :return: (list) Liste de tuples contenant l'indice du transect et l'altitude maximale
        de débordement pour ce transect.
    """
    altitude_max_amplitudes = []  # Liste pour stocker les altitudes maximales de débordement
    for idx, x_smooth, y_smooth in spline_results:
        y_smooth_np = np.array(y_smooth)
        maxima_smooth, _ = find_peaks(y_smooth_np)
        minima_smooth, _ = find_peaks(-y_smooth_np)
        diff_smooth = np.diff(y_smooth)
        if maxima_smooth.any() and minima_smooth.any():
            # Calcul des amplitudes des ruptures de pente
            amplitudes_smooth = [y_smooth[max_index] - y_smooth[min_index] for max_index, min_index in zip(maxima_smooth, minima_smooth)]
            if amplitudes_smooth:
                max_amplitude_index = np.argmax(amplitudes_smooth)
                altitude_max_amplitude = x_smooth[maxima_smooth[max_amplitude_index]]
            else:
                max_diff_index = np.argmax(diff_smooth)
                altitude_max_amplitude = x_smooth[max_diff_index + 1]
        else:
            max_diff_index = np.argmax(diff_smooth)
            altitude_max_amplitude = x_smooth[max_diff_index + 1]
        altitude_max_amplitudes.append((idx, altitude_max_amplitude))
    # Créer un DataFrame à partir de la liste de tuples
    bankfull_max_amplitude = pd.DataFrame(altitude_max_amplitudes, columns=['x_sec_id', 'altitude'])
    # Export dans un fichier .csv
    df_output_path = os.path.join(directory_path, "bankfull_max_amplitude.csv")
    bankfull_max_amplitude.to_csv(df_output_path, sep=',', index=False)
    print(f"Les altitudes ont été exportées avec succès vers : {df_output_path}")
    return altitude_max_amplitudes

def find_bankfull_M2(spline_results, directory_path):
    """
    Trouve l'altitude de débordement pour chaque transect en se basant sur l'altitude
    de débordement du transect précédent.
    :param spline_results: (list) Liste de tuples (idx, x_smooth, y_smooth) représentant
        les résultats de l'interpolation par spline pour chaque transect.
    :return: (list) Liste de tuples contenant l'indice du transect et l'altitude de débordement
        pour ce transect.
    """
    bankfull_values = []  # Liste pour stocker les altitudes de débordement de tous les transects
    prev_bankfull = None  # Tuple pour stocker l'altitude de débordement du transect précédent
    for idx, x_smooth, y_smooth in spline_results:
        y_smooth_np = np.array(y_smooth)
        maxima_smooth, _ = find_peaks(y_smooth_np)
        minima_smooth, _ = find_peaks(-y_smooth_np)
        # Calcul des amplitudes des ruptures de pente
        if maxima_smooth.any():
            amplitudes_smooth = [y_smooth_np[max_index] - y_smooth_np[min_index] for max_index, min_index in zip(maxima_smooth, minima_smooth)]
            if amplitudes_smooth:
                if idx == 0:
                    max_amplitude_index = np.argmax(amplitudes_smooth)
                    alti_bankfull = x_smooth[maxima_smooth[max_amplitude_index]]
                    prev_amplitude = amplitudes_smooth[max_amplitude_index]
                else:
                    closest_amplitude_index = np.abs(np.array(amplitudes_smooth) - prev_amplitude).argmin()
                    alti_bankfull = x_smooth[maxima_smooth[closest_amplitude_index]]
                    prev_amplitude = amplitudes_smooth[closest_amplitude_index]
            else:
                alti_bankfull = prev_bankfull[1]
        else:
            alti_bankfull = prev_bankfull[1]
        bankfull_values.append((idx, alti_bankfull))
        prev_bankfull = (idx, alti_bankfull)
    
    # Créer un DataFrame à partir de la liste de tuples
    bankfull_previous_transects = pd.DataFrame(bankfull_values, columns=['x_sec_id', 'altitude'])
    # Export dans un fichier .csv
    df_output_path = os.path.join(directory_path, "bankfull_previous_transects.csv")
    bankfull_previous_transects.to_csv(df_output_path, sep=',', index=False)
    print(f"Les altitudes ont été exportées avec succès vers : {df_output_path}")

    return bankfull_values
