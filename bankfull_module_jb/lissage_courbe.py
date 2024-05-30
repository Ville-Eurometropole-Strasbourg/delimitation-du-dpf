import numpy as np
from scipy.interpolate import UnivariateSpline
from sklearn.model_selection import train_test_split

def LissageCourbe(deb_intervalle, fin_intervalle, pas, test_size, prof_hydr):

    """Lisse les courbes de profondeur hydraulique pour chaque transect en utilisant la régression spline.

    :param deb_intervalle: (float) Valeur de départ de l'intervalle pour la recherche des paramètres de lissage.
    :param fin_intervalle: (float) Valeur de fin de l'intervalle pour la recherche des paramètres de lissage.
    :param pas: (float)  Pas entre chaque valeur de l'intervalle pour la recherche des paramètres de lissage.
    :param test_size: (float) Taille de l'ensemble de test pour la validation croisée.
    :param prof_hydr: (float) DataFrame contenant les données de profondeur hydraulique par transect.
    
    :return: (list) Liste de tuples contenant les résultats du lissage pour chaque transect. Chaque tuple contient :
        - name (int): Identifiant du transect.
        - x_smooth (list): Liste des valeurs lissées de l'altitude de référence.
        - y_smooth (list): Liste des valeurs lissées de la profondeur hydraulique.
    """
    
    grouped_prof_hydr = prof_hydr.groupby('x_sec_id')
    s_values = np.arange(deb_intervalle, fin_intervalle, pas)
    k_values = [1, 2, 3, 4, 5]
    t_size = test_size
    x_smooth_list = []
    y_smooth_list = []
    spline_results = []

    for name, group in grouped_prof_hydr:
        x_transect = group['ref_altitude']
        y_transect = group['profondeur_hydraulique']
        x_train, x_test, y_train, y_test = train_test_split(x_transect, y_transect, test_size=test_size, random_state=50)
        sort_indices = np.argsort(x_train)
        x_train = x_train.iloc[sort_indices]
        y_train = y_train.iloc[sort_indices]
        scores = np.zeros((len(k_values), len(s_values)))
        for i, k in enumerate(k_values):
            for j, s in enumerate(s_values):
                spline = UnivariateSpline(x_train, y_train, k=k, s=s)
                y_pred = spline(x_test)
                ss_res = np.sum((y_test - y_pred)**2)
                ss_tot = np.sum((y_test - np.mean(y_test))**2)
                r2_score = 1 - (ss_res / ss_tot)
                scores[i, j] = r2_score
        best_k_index, best_s_index = np.unravel_index(np.argmax(scores), scores.shape)
        best_k = k_values[best_k_index]
        best_s = s_values[best_s_index]
        spline = UnivariateSpline(x_transect, y_transect, k=best_k, s=best_s)
        x_smooth = np.linspace(x_transect.min(), x_transect.max(), 1000).tolist()
        y_smooth = spline(x_smooth).tolist()
        x_smooth_list.append(x_smooth)
        y_smooth_list.append(y_smooth)
        spline_results.append((name, x_smooth, y_smooth))
    
    return spline_results