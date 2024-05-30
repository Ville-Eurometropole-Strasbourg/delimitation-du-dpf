import os
import math
import pandas as pd

def export_data(df_transects, directory_path, output_file_name):
    """
    Exporte les données d'un DataFrame dans un fichier CSV.

    :param df_transects: DataFrame contenant les données à exporter
    :param directory_path: Chemin vers le répertoire d'enregistrement
    :param output_file_name: Nom du fichier de sortie
    """
    POINT_X = df_transects['POINT_X'].tolist()
    POINT_Y = df_transects['POINT_Y'].tolist()
    POINT_Z = df_transects['POINT_Z'].tolist()
    
    distances_along_transect = []
    for index, row in df_transects.iterrows():
        # Récupérer les coordonnées de l'origine du transect correspondant à ce point
        origin_x = df_transects.loc[(df_transects['x_sec_id'] == row['x_sec_id']) & (df_transects['x_sec_order'] == 0), 'POINT_X'].iloc[0]
        origin_y = df_transects.loc[(df_transects['x_sec_id'] == row['x_sec_id']) & (df_transects['x_sec_order'] == 0), 'POINT_Y'].iloc[0]
    
        # Calculer la distance entre chaque point et l'origine du transect
        distance = math.sqrt((row['POINT_X'] - origin_x)**2 + (row['POINT_Y'] - origin_y)**2)
        distances_along_transect.append(distance)
    
    df_transects['Distance'] = distances_along_transect
    
    output_path = os.path.join(directory_path, output_file_name)
    df_transects.to_csv(output_path, sep=",", index=False)
    print(f"La DataFrame a été exportée avec succès dans le fichier : {output_path}")
