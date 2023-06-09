import matplotlib.pyplot as plt
import numpy as np
import json
import datetime

"""
niveau sonore
frequences pour tout les mouvements (autre graphique)
posture du dos (graphique baton)
"""

def graphique_son(donnees_x, donnees_y, titre):
    # Données pour l'axe des x
    # Création de la figure et des axes

    donnees_x_int = []
    for i in donnees_x:
        donnees_x_int.append(int("".join(i.split(":"))))

    print(len(donnees_x_int))
    fig, ax = plt.subplots()

    """
    Travail répétitif : 30rep /min /15
    Décibel : 80 db / 70db
    """

    # Tracé de la courbe principale
    ax.plot(donnees_x_int, donnees_y, color='blue', label='Courbe principale')

    ax.xaxis.set_ticks(donnees_x_int)
    ax.xaxis.set_ticklabels(donnees_x, rotation=45)

    # Définition des limites des zones verte et rouge
    seuil_vert = 70
    seuil_rouge = 80

    # Calcul des indices où les valeurs de y dépassent les seuils
    #indices_vert = np.where(np.array(donnees_y) >= seuil_vert)[0]
    #indices_rouge = np.where(np.array(donnees_y) <= seuil_rouge)[0]
    # Remplissage de la zone verte
    ax.fill_between(donnees_x_int, donnees_y, seuil_vert, where=(np.array(donnees_y) <= seuil_vert), interpolate=True, facecolor='green', alpha=0.3)

    # Remplissage de la zone rouge
    ax.fill_between(donnees_x_int, donnees_y, seuil_rouge, where=(np.array(donnees_y) >= seuil_rouge), interpolate=True, facecolor='red', alpha=0.3)

    # Légende et titre du graphique
    ax.legend()
    ax.set_title(titre)

    # Affichage du graphique
    


    plt.savefig('graphique.png') # revoir pour que tout les graphiques ne s'appellent pas pareil
    plt.show() # à enlever quand on voudra juste sauvegarder

with open("ouvriers.json", 'r') as fichier:
    # Lecture du contenu JSON
    ouvriers_dict = json.load(fichier)

donnees = ouvriers_dict["2"]["mesures"]["2023-06-02"]["Bras droit"]
list_x, list_y = [], []
for i in donnees:
    list_x.append(i[0])
    list_y.append(float(i[1]))
print(list_x)
list_x.sort()

#graphique_son(list(list_x), list(list_y), titre="Bras droit")

def frequence_mouvements(data_json, day, id_ouvrier):
    """
    A partir des données sur un journée, retourne un liste de vecteurs comprenant pour chaque
    minutes le niveau de pénibilité du mouvement de chaque articulation parmis les 2 poignets et
    les 2 coudes.
    Les 3 niveau sont faible (0), moyen (1), élevé (2).
    jour au format AAAA-MM-JJ
    """
    
    #on récupère les données de la journée pour chacun des capteurs
    with open("ouvriers.json", 'r') as fichier:
        # Lecture du contenu JSON
        ouvriers_dict = json.load(fichier)

    donnees = ouvriers_dict[str(id_ouvrier)]["mesures"][str(day)]

    #on récupère les données de chaque capteur
    donnees_bras_gauche = [i[1] for i in donnees["Bras gauche"]]
    donnees_bras_droit = [i[1] for i in donnees["Bras droit"]]
    donnees_poignet_gauche = [i[1] for i in donnees["Poignet gauche"]]
    donnees_poignet_droit = [i[1] for i in donnees["Poignet droit"]]

    #on crée le vecteur de niveau de pénibilité
    vecteur_intensite = []

    for i in range(len(donnees_bras_gauche)):
        valeurs = [donnees_bras_gauche[i], donnees_bras_droit[i], donnees_poignet_gauche[i], donnees_poignet_droit[i]]
        intensites = []
        for valeur in valeurs:
            if valeur < 15:
                intensites.append(0)
            elif valeur < 30:
                intensites.append(1)
            else:
                intensites.append(2)
        vecteur_intensite.append(intensites)

    return vecteur_intensite

def analyse_repetition(data_json, day, id_ouvrier):
    """
    On définit cherche à identifier les mouvements répétitifs et à déterminer leur durée.
    """

    vecteur_intensite = frequence_mouvements(data_json, day, id_ouvrier)
    is_hard = lambda vecteur: True if 2 in vecteur else False
    count = 0
    previous = [-1, -1, -1, -1]
    mouvements_identifies = {} #clef : valeurs d'intensités, valeur : nombre de fois que ce mouvement est apparu
    for vecteur in vecteur_intensite:
        if count > 0 and is_hard(vecteur):
            if vecteur == previous:
                count += 1
            else:
                if vecteur in mouvements_identifies and count >= 5:
                    mouvements_identifies[vecteur] += count
                elif count >= 5:
                    mouvements_identifies[vecteur] = count
                count = 0

        previous = vecteur

    return mouvements_identifies





def periodes_inactivite(data_json, day, id_ouvrier):
    """
    On cherche à identifier les périodes d'inactivité.
    """
    vecteurs_intensite = frequence_mouvements(data_json, day, id_ouvrier)
    li_activite = []
    for vecteur in vecteurs_intensite:
        if vecteur == [0, 0, 0, 0]:
            li_activite.append(0)
        else:
            li_activite.append(1)
        
    return li_activite


#print(periodes_inactivite(ouvriers_dict, "2023-06-02", 2))

def affichage_vecteur(vecteur):
    """
    Affiche un vecteur de niveau de pénibilité.
    """
    Z = np.array(vecteur)

    fig, ax = plt.subplots()

    # Define the colormap
    cmap = plt.cm.colors.ListedColormap(['green', 'gray', 'red'])

    # Set the colormap bounds and norm
    bounds = [0, 1, 2, 3]
    norm = plt.cm.colors.BoundaryNorm(bounds, cmap.N)

    c = ax.pcolor(Z, cmap=cmap, norm=norm)
    ax.set_title('Pcolor Plot')

    fig.tight_layout()
    plt.show()

    #il faut changer les titres des axes pour bien montrer chaque articulation et le temps
   

data = [
    [0, 2, 1, 0],
    [1, 2, 1, 0],
    [2, 2, 0, 2],
]

affichage_vecteur(data)


        

