import numpy as np
from scipy.interpolate import interp1d
from scipy.spatial.distance import euclidean
import matplotlib.pyplot as plt

def calculer_aire(dist, alti, alti_ref, filtrage_aires):

    """Calcul des aires entre la droite d'altitude de référence et le profil en travers
    
    :param dist:
    :param alti:
    :param alti_ref:
    :param filtrage_aires: """
    
    d1 = [(dist[i], alti[i]) for i in range(len(alti))]
            
    areas_iteration = []
    for i in range(len(alti_ref)):
        dref = [(dist[j], alti_ref[i]) for j in range(len(dist))]
        dist_dref, alti_dref = zip(*dref)

        f_d1 = interp1d(dist, alti, kind='linear')
        f_dref = interp1d(dist_dref, alti_dref, kind='linear')

        dist_interp = np.linspace(min(dist), max(dist), 1000)
        alti_d1_interp = f_d1(dist_interp)
        alti_dref_interp = f_dref(dist_interp)

        intersection_indices = np.where(np.diff(np.sign(alti_d1_interp - alti_dref_interp)))[0] + 1

        intersection_points = []  
        distances = []  
        intersection_indices_list = []  

        if len(intersection_indices) > 0:
            intersection_indices = np.insert(intersection_indices, 0, 0)  
            intersection_indices = np.append(intersection_indices, len(dist_interp) - 1)  
            color_zones = [(intersection_indices[j], intersection_indices[j + 1], plt.cm.jet(j / len(intersection_indices))) for j in range(len(intersection_indices) - 1)]
            areas_iteration_current = []
            for start_idx, end_idx, color in color_zones:
                area = np.trapz(alti_dref_interp[start_idx:end_idx] - alti_d1_interp[start_idx:end_idx], x=dist_interp[start_idx:end_idx])
                area = abs(area)
                if area > filtrage_aires:
                    x_centroid = np.trapz(dist_interp[start_idx:end_idx] * (alti_dref_interp[start_idx:end_idx] - alti_d1_interp[start_idx:end_idx]), x=dist_interp[start_idx:end_idx]) / np.trapz(alti_dref_interp[start_idx:end_idx] - alti_d1_interp[start_idx:end_idx], x=dist_interp[start_idx:end_idx])
                    y_centroid = np.trapz((alti_dref_interp[start_idx:end_idx] + alti_d1_interp[start_idx:end_idx]) / 2 * (alti_dref_interp[start_idx:end_idx] - alti_d1_interp[start_idx:end_idx]), x=dist_interp[start_idx:end_idx]) / np.trapz(alti_dref_interp[start_idx:end_idx] - alti_d1_interp[start_idx:end_idx], x=dist_interp[start_idx:end_idx])

                    if y_centroid > alti_ref[i]:
                        areas_iteration_current.append((area, 'above', alti_ref[i]))  
                    else:
                        areas_iteration_current.append((area, 'below', alti_ref[i]))  

                    if color != 'lightblue':
                        area *= -1
                        intersection_point = (dist_interp[start_idx], alti_dref_interp[start_idx], alti_d1_interp[start_idx])
                        intersection_points.append(intersection_point)
                        intersection_indices_list.append(start_idx)  
                        if start_idx != end_idx:
                            intersection_point = (dist_interp[end_idx], alti_dref_interp[end_idx], alti_d1_interp[end_idx])
                            intersection_points.append(intersection_point)
                            intersection_indices_list.append(end_idx)  

                            distance_between_intersections = euclidean(intersection_points[-2], intersection_points[-1])
                            distances.append(distance_between_intersections)

            areas_iteration.append((i, areas_iteration_current, distances, alti_ref[i], intersection_indices_list))  

    return areas_iteration
