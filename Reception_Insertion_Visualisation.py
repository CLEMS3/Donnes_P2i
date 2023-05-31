# -*- coding: utf-8 -*-

# Python built-in Packages
import time
# Requirement: package pyserial // Terminal >> pip install pyserial
from arduino_manager import ArduinoManager
import mysql.connector as mysql
from datetime import datetime


class ArduinoDataHandler:
    
    # COMPLETER CENTRALE INERTIELLE + TROUVER MANIERE D'OBTENIR ID CAPTEUR

    # Constructeur : attributs et paramètres à adapter aux besoins de votre projet (connexion BD, etc.)
    def __init__(self):
        
        self.connexion_bd = mysql.connect(
            host = "fimi-bd-srv1.insa-lyon.fr",
            port = 3306,
            user = "G223_C",
            password = "G223_C",
            database = "G223_C_BD1"
            )
        
        #Données reçues ou accumulées de manière à correspondre à une minute, l'intervalle de temps standard
        self.elongation_minute = ""
        
        self.son_minute = ""
        
        self.coude_droit_minute = ""
        self.coude_gauche_minute = ""
        
        self.poignet_droit_minute = "" #Feel free to change the initial value of this variable, doesn't have to be a str
        self.poignet_gauche_minute = "" #Feel free to change the initial value of this variable, doesn't have to be a str
        
        
        #Compteurs incrémentés à chaque fois qu'un message des bras (émis toutes les secondes) arrive
        self.compteur_minute_gauche = 0
        self.compteur_minute_droite = 0
        
        self.a_inserer = [] #Liste des tuples à insérer dans la BD à l'issue du traitement de chaque paquet. Initialisée vide
        
        


    # Méthode appelée lorsque le module Arduino reçoit une ligne de données
    def on_arduino_data(self, input_line):
        
        print("[ArduinoDataHandler] Message de l'Arduino: " + input_line)
        
        paquet = input_line.split() #Les parties du paquet sont délimitées par des espaces
        provenance_paquet = paquet[0] #Le premier élément du paquet est sa provenance : gauche, droit ou dos
        print(f"\n ---------Provenance paquet : {provenance_paquet}")
        
        
        self.a_inserer = [] #Réinitialisation de la liste de données à insérer à l'arrivée d'un nouveau paquet
        maintenant = datetime.now().strftime("%Y-%m-%d %H:%M:%S") #On extrait et formatte la date de réception, qui deviendra la date de mesure
        self.extraire_informations(paquet, provenance_paquet, maintenant) #Lancer la fonction qui va extraire les infos, les traiter et les placer dans la liste "à insérer"
        
        
        print(f"A insérer : {self.a_inserer}")
        
        #Insérer les données traitées dans la BD
        if self.compteur_minute_gauche == 60 or self.compteur_minute_droite == 60 :
            self.inserer_donnees()
        
        
        
    def extraire_informations(self, paquet, provenance_paquet, maintenant):
        """Extrait et traite les informations du paquet selon sa provenance"""
        print("work well !")
        if provenance_paquet == "GAUCHE":
            
            
            coude_gauche_seconde, poignet_gauche_seconde  = paquet[1], paquet[2] #On récupère les valeurs émises pour la seconde
            self.coude_gauche_minute += coude_gauche_seconde #On les accumule pour pouvoir les traiter plus tard, 
            self.poignet_gauche_minute += poignet_gauche_seconde #Quand le compteur de secondes sera arrivé à 60
            
            print(f"\nPaquet du bras gauche numéro {self.compteur_minute_gauche} : Coude {coude_gauche_seconde} ")
            
            self.compteur_minute_gauche += 1 #On compte les paquets pour détecter quand le seuil de la minute est atteint
            
            
            if self.compteur_minute_gauche == 60: #Quand on a toutes les données d'une minute, on procède au traitement des données
                print("compteur 60")
                donnee_coude_gauche = self.traiter_donnees_coude(self.coude_gauche_minute)
                donnee_poignet_gauche = self.traiter_donnees_poignet(self.poignet_gauche_minute)
                self.compteur_minute_gauche = 0 #Puis on réinitialise le compteur de secondes
                
                print(f"**Minute atteinte : données exploitées du coude : {donnee_coude_gauche} mouvements/min")
                #Le correspond à une idpanoplie pour l'instant insérée à la main
                self.a_inserer.append((donnee_coude_gauche, maintenant, 2, 2)) #On souhaite ajouter ce tuple correspondant à la donnée du coude gauche (0 = Flexion)
                self.a_inserer.append((donnee_poignet_gauche, maintenant, 1, 1)) #On ajoute aussi le tuple pour la donnée du poignet gauche (2 = accélération angulaire)
                self.inserer_donnees()
            
            
        elif provenance_paquet == "DROITE": #Même chose pour le bras droit
            coude_droit_seconde, poignet_droit_seconde  = paquet[1], paquet[2]
            self.coude_droit_minute += coude_droit_seconde
            self.poignet_droit_minute += poignet_droit_seconde
            
            print(f"\nPaquet du bras droit numéro {self.compteur_minute_droite} : Coude {coude_droit_seconde} ")
            
            self.compteur_minute_droite += 1
            
            if self.compteur_minute_droite == 60:
                donnee_coude_droit = self.traiter_donnees_coude(self.coude_droit_minute)
                donnee_poignet_droit = self.traiter_donnees_poignet(self.poignet_droit_minute)
                self.compteur_minute_droite = 0
                
                print(f"**Minute atteinte : données exploitées du coude : {donnee_coude_droit} mouvements/min")
                
                self.a_inserer.append((donnee_coude_droit, maintenant, 3, 0)) #On souhaite ajouter ce tuple correspondant à la donnée du coude droit (0 = Flexion)
                self.a_inserer.append((donnee_poignet_droit, maintenant, 4, 2)) #On ajoute aussi le tuple pour la donnée du poignet droit (3 = accélération angulaire)
            
            
            
        elif provenance_paquet == "DOS":
            self.son_minute, self.elongation_minute  = paquet[1], paquet[2] #Récupération des informations
            donnee_elongation = self.traiter_donnees_elongation(self.elongation_minute) #Traitement des données
            
            print(f"\nPaquet du dos : élongation {donnee_elongation} min de mauvaise position, son {self.son_minute}")
            
            self.a_inserer.append((float(self.son_minute), maintenant, 6, 4)) #La moyenne sonore n'a pas besoin de traitement complexe (4 = niveau sonore)
            self.a_inserer.append((donnee_elongation, maintenant, 5, 1)) # (1 = élongation)
        
            
        else: #Si la provanance n'est ni le dos, ni la gauche, ni la droite (erreur de réception)
            print("ERREUR : Paquet non identifiable !")
            
    
        
    def traiter_donnees_coude(self, donnees):
        """Compte le nombre de mouvements piler-déplier du coude dans une minute"""
        compteur_mouvements = 0 #Compte combien de fois on passe de 0 à 1 et inversement
        bit_precedent = -1 #Initialisé à -1 au début, quand il n'y a pas de bit précédent
        
        for bit in donnees:
            if  (bit_precedent != -1) and (bit != bit_precedent): #S'il y a un changement de 0 à 1 ou inversement :
                compteur_mouvements += 1
            bit_precedent = bit #On stocke le bit précédent en mémoire
            
        return compteur_mouvements/2 # 1 mouvement = 1-0-1 ou bien 0-1-0, donc il faut diviser par deux
        
    def traiter_donnees_poignet(self, donnees):
        """Compte le nombre de mouvements du poignet dans une minute"""
        pass #A COMPLETER!!!!!!!!!!!!
    
    def traiter_donnees_elongation(self, donnees):
        """Calcule le temps passé en mauvaise position du dos en une minute
        Résultat exprimé en min, comme si c'était un 'pourcentage de minute'
        """
        return round(donnees.count("1")/len(donnees), 2) #On compte le nombre de "1" dans la chaîne de bits. 1 = mauvaise position
    
    def inserer_donnees(self):
        """Insère les tuples contenus dans 'a_inserer' dans la base de données"""
        valeur_mesure_1, date_mesure_1, idCapteur_1, idTypeMesure_1 = self.a_inserer[0]
        valeur_mesure_2, date_mesure_2, idCapteur_2, idTypeMesure_2 = self.a_inserer[1]
        valeur_mesure_1 = 1.563
        valeur_mesure_2 = 5
        cursor = self.connexion_bd.cursor()
        #cursor.execute("INSERT INTO Entreprise(idEntreprise, nomEntreprise, adresseEntreprise) VALUES (5,"Hp","65 rue de linformation Paris")"
        cursor.execute("INSERT INTO Mesure(valeurMesure, dateMesure, idCapteur, idTypeMesure) VALUES (%s,%s,%s,%s)" , [valeur_mesure_1, date_mesure_1, idCapteur_1, idTypeMesure_1])
        cursor.execute("INSERT INTO Mesure(valeurMesure, dateMesure, idCapteur, idTypeMesure) VALUES (%s,%s,%s,%s)", [valeur_mesure_2, date_mesure_2, idCapteur_2, idTypeMesure_2])
        self.connexion_bd.commit()
        cursor.close()
        
        

    
        
        


print("** Début du script **")

port_arduino = None

while port_arduino is None:
    # Trouver le port du device Arduino
    print("Recherche du Port Arduino...")
    port_arduino = ArduinoManager.trouver_port_arduino()
    # si le device Arduino n'a pas encore été trouvé : attendre 5s, puis reboucler
    if port_arduino is None:
        print("Port Arduino non trouvé, attente de 5s")
        try:
            time.sleep(5)
        except KeyboardInterrupt:
            # en cas d'interruption du script
            print("Arrêt de la recherche du Port Arduino")
            break


if port_arduino is not None:

    arduino_data_handler = ArduinoDataHandler()

    print("Port Arduino trouvé")
    arduino_manager = ArduinoManager(port_arduino, arduino_data_handler, baudrate=115200)

    print("Ouverture de la communication USB avec l'Arduino")
    arduino_manager.open()

    print("Écrire une ligne pour l'envoyer à l'Arduino ou 'stop' (ou 'Q') pour arrêter la communication")

    while True:
        try:
            console_input_line = input()  # Saisie au clavier
        except KeyboardInterrupt:
            print("Arrêt de l'attente de la saisie au clavier")
            break

        if console_input_line == 'stop' or console_input_line == 'Q':
            break
        elif len(console_input_line) > 0:
            print("Envoi de la ligne à l'Arduino >>> " + console_input_line)
            arduino_manager.write_line(console_input_line)

    print("Fermeture de la communication USB avec l'Arduino")
    arduino_manager.close()

print("** Fin du script **")
