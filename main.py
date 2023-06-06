#importations
import mysql.connector as mysql
import json
import datetime

def ouvrir_connexion_bd():
    """
    Fonction qui ouvre une connexion à la base de données
    """
    print("")
    print("***********************")
    print("** Connexion à la BD **")
    print("***********************")

    connexion_bd = None
    try:
        connexion_bd = mysql.connect(
                host="fimi-bd-srv1.insa-lyon.fr",
                port=3306,
                user="G223_C",
                password="G223_C",
                database="G223_C_BD1"
            )
    except Exception as e:
        if type(e) == NameError and str(e).startswith("name 'mysql'"):
            print("[ERROR] MySQL: Driver 'mysql' not installed ? (Python Exception: " + str(e) + ")")
            print("[ERROR] MySQL:" +
                  " Package MySQL Connector should be installed [Terminal >> pip install mysql-connector-python ]" +
                  " and imported in the script [import mysql.connector as mysql]")
        else:
            print("[ERROR] MySQL: " + str(e))

    if connexion_bd is not None:
        print("=> Connexion établie...")
    else:
        print("=> Connexion échouée...")

    return connexion_bd

def fermer_connexion_bd(connexion_bd):
    print("")
    print("Fermeture de la Connexion à la BD")

    if connexion_bd is not None:
        try:
            connexion_bd.close()
            print("=> Connexion fermée...")
        except Exception as e:
            print("[ERROR] MySQL: "+str(e))
    else:
        print("=> pas de Connexion ouverte")

# def creation_json():
#     # Données des ouvriers
#     mesures = {
#     }

#     # Convertir en JSON
#     json.dump(mesures, 'ouvriers.json' , indent=4)

def ajout_ouvrier(nom:str, prenom:str, poste:str, identifiant:int):
    # Charger le JSON existant
    
    with open('ouvriers.json', 'r') as file:
        data = json.load(file)

    # Ajouter les données du nouvel ouvrier
    nouvel_ouvrier = {
        identifiant: {
            "identite": {
                "nom": nom,
                "prenom": prenom,
                "poste": poste
            },
            "mesures": {

            }
        }
    }

    data.update(nouvel_ouvrier)

    # Enregistrer le JSON mis à jour
    
    with open('ouvriers.json', 'w') as file:
        json.dump(data, file, indent=4)

def ajout_mesure(jour, liste_valeur:list, type:str, ouvrier:str):
    """
    On passe la liste des valeurs en paramètre. Il ne peut pas il y avoir ce type de variable ce jour là
    déjà dans le JSON car on importe les données une fois en tout.
    En revanche, la date peut être déjà présente dans le JSON, il faut donc vérifier si la date est déjà présente
    La liste de valeur est une liste de tuple (heure, valeur)
    """
    
    
    # Charger le JSON existant
    with open('ouvriers.json', 'r') as file:
        data = json.load(file)
        data = dict(data)
        jour = str(jour)
        ouvrier = str(ouvrier)
        if ouvrier in data.keys() : 
            print("On est sur la bonne voie !")
        
    if str(ouvrier) not in data.keys():
        print("L'ouvrier n'est pas dans la base de données")
        return
    
    else : 
        print("En vrai c'est quali ça")

    # On vérifie si la date est déjà présente dans le JSON
    if jour in data[str(ouvrier)]["mesures"]:
        # La date est déjà présente dans le JSON, on ajoute donc les valeurs à la liste des valeurs déjà présentes
        
        print('les mesures sont dans la place')
        print(jour)
        
        data[str(ouvrier)]["mesures"][jour][type] = [(valeur[0], valeur[1]) for valeur in liste_valeur]
        
    else : 
        print("la voie de la raison est grande ouverte")
        
        # La date n'est pas présente dans le JSON, on ajoute donc la date et les valeurs
        
        print(jour)
        nouvelle_mesure = {
            jour: {
                type: [(valeur[0], valeur[1]) for valeur in liste_valeur]
            }
        }
        data[ouvrier]["mesures"].update(nouvelle_mesure)

    # Enregistrer le JSON mis à jour
    with open('ouvriers.json', 'w') as file:
        json.dump(data, file, indent=4)

# Import des données
def import_donnees(idPrestation):
    # creation_json()
    connexion_bd = ouvrir_connexion_bd()
    cursor = connexion_bd.cursor()
    cursor.execute("SELECT * " +
                   "FROM Ouvrier, Prestation " +
                   "WHERE idPrestation = 1 " +
                   "AND Ouvrier.idEntreprise = Prestation.idEntreprise ")
    
    print(cursor)
    
    for data in cursor :
        print("je suis là")
        
        idOuvrier , nomOuvrier , prenomOuvrier , posteOuvrier, idEntreprise_1, idPrestation, dateDebut, dateFin, idEntreprise_2 = data
         
        ajout_ouvrier(nomOuvrier, prenomOuvrier, posteOuvrier, idOuvrier)
        
        # /!\ est ce que ça passe pour le type de capteur
        cursor.execute("SELECT Mesure.dateMesure, Mesure.valeurMesure, AppartientA.localisation, Mesure.idTypeMesure " +
                       "FROM Mesure, AppartientA , Panople , MobilisePour, Porte , Ouvrier , Capteur " +
                       "WHERE Ouvrier.idOuvrier =  %s " +
                       "AND idPrestation = %s " +
                       "AND AppartientA.idCapteur = Capteur.idCapteur " +
                       "AND AppartientA.idPanople = Porte.idPanople " +
                       "AND AppartientA.idPanople = MobilisePour.idPanople " +
                       "AND Panople.idPanople = Porte.idPanople " +
                       "AND Ouvrier.idOuvrier = Porte.idOuvrier " +
                       "AND Capteur.idCapteur = Mesure.idCapteur ", (idOuvrier, idPrestation))
        
        mesures = {}
        for donnees_capteur in cursor :
            dateMesure, valeurMesure, appartientA, typeMesure = donnees_capteur
            #print(f' ici les donnees capteurs {donnees_capteur}')
            if appartientA not in mesures:
                print(appartientA)
                mesures[appartientA] = []
            jour = dateMesure.date()
            heure = dateMesure.time()
            heure = str(heure)
            jour = str(jour)
            valeurMesure = str(valeurMesure)
            print(jour, heure)
            mesures[appartientA].append((heure, valeurMesure))
            
        for type_mesure in mesures.keys():
            print(f' Ici les type de mesure {type_mesure}')
            liste_valeur = mesures[type_mesure]
            ajout_mesure(jour, liste_valeur, type_mesure, idOuvrier)

    fermer_connexion_bd(connexion_bd)
    
import_donnees(1)