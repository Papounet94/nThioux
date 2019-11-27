#!/usr/bin/env python3
"""
Extraction des informations présentes dans les logs récupérés sur le drone pour en faire
un fichier exploitable par Potree
"""

# Ouverture du fichier de log -- le récupérer sur la line de commande dans une version ultérieure
logfile = open("GPSLOG.TXT", "r")
# Ouverture du fichier qui contiendra les valeurs extraites
extractfile = open("Test.XYZ", "w")
# Récupération des données dans une liste
lines = logfile.readlines()
# Fermeture du fichier de données
logfile.close()
# Itération sur chaque ligne du fichier
for line in lines:
    # on ne regarde que les lignes commençant par $GPGGA
    if line.startswith("$GPGGA"):
        # on récupère tous les champs de la ligne dans une liste
        fields = line.split(",")
        # la latitude (Y) est le 3ème champ
        latitude = fields[2]
        # le 4ème champ contient l'hémisphère (N ou S) pour la latitude
        if fields[3] == "S":
            latitude = -latitude
        # la longitude (X) est le 5ème champ
        longitude = fields[4]
        # le 6ème champ contient l'hémisphère (E ou W) pour la longitude
        if fields[5] == "W":
            longitude = -longitude
        # l'altitude (Z) est le 10ème champ
        altitude = fields[9]
        # La valeur du capteur est le 16ème et dernier champ
        # On enlève le \n final qui fait partie du champ 
        sensorData = fields[15].split("\n")[0]
        # on écrit les données extraites dans une ligne du fichier final
        extractfile.write(" ".join([longitude, latitude, altitude, sensorData])+ "\n")
# Fermeture du fichier final
extractfile.close()
