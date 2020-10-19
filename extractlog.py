#!/usr/bin/env python3
"""
Extraction des informations présentes dans les logs récupérés sur le drone pour en faire
un fichier exploitable par Potree
"""

import argparse

def getColorDiscrete(value) :
    """ Fonction donnant la couleur correspondant à une valeur donnée
    en fonction d'une table prédéfinie.
    """
    if value < 0.2 :       # R = 255 / 2.5 * value
        return '0 0 255'
    elif value < 0.4:
        return '63 0 255'
    elif value < 0.6 :
        return '127 0 255'
    elif value < 0.8 :
        return '191 0 255'
    elif value < 1.0 :     
        return '255 0 255' # B = 255 / 2.5 * (5 - value)
    elif value < 1.5 :
        return '255 0 191'
    elif value < 2.0 :
        return '255 0 127'
    elif value < 3.5 :
        return '255 0 63'
    else : # au-delà de 3.5 tout est rouge
        return '255 0 0'

def getColorLinear(value):
    """ Fonction donnant la couleur correspondant à une valeur donnée 
        de façon linéaire suivant la valeur en partant d'un bleu pur
        et en augmentant le rouge jusqu'à la moitié de la plage de valeurs
        puis en diminuant le bleu pour finir par un rouge pur
    """
    if value < 2.5:
        red = str(int(255 * value / 2.5))
        green = '0'
        blue = '255'
    else:
        red = '255'
        green = '0'
        blue = str(int(255 * (5.0 - value) / 2.5))
    return " ".join([red, green, blue])

# Parsing de la ligne de commande pour récupérer les arguments
parser = argparse.ArgumentParser()
parser.add_argument("-i", "--infile", help="Nom du fichier de log (AVEC son extension) 'GPSLOG.TXT' par défaut", 
    default = "GPSLOG.TXT")
parser.add_argument("-o", "--outfile", help="Nom des fichiers de sortie (SANS extension) 'test' par défaut", 
    default="test")
parser.add_argument("-linear", action="store_true", 
    help="Option de sortie linéaire pour la couleur du point")
parser.add_argument("-dd", action="store_true", 
    help="Longitude et Latitude en degrés décimaux")
args = parser.parse_args()

# Choix du type de repésentation des points de couleur
if args.linear :
    getColor = getColorLinear
else:
    getColor = getColorDiscrete

if args.dd :
    divider = 100
else :
    divider = 1

# Ouverture du fichier de log -- le récupérer sur la ligne de commande dans une version ultérieure
#logfile = open("GPSLOG.TXT", "r")
logfile = open(args.infile, "r")
# Ouverture du fichier qui contiendra les valeurs extraites au format XYZ
extractfileXYZ = open(args.outfile + ".XYZ", "w")
# Ouverture du fichier qui contiendra les valeurs extraites au format XYZRGB
extractfileRGB = open(args.outfile + ".XYZRGB", "w")
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
        latitude = float(fields[2].lstrip("00")) / divider
        # le 4ème champ contient l'hémisphère (N ou S) pour la latitude
        if fields[3] == "S":
            latitude = -latitude
        # la longitude (X) est le 5ème champ
        longitude = float(fields[4].lstrip("00")) / divider
        # le 6ème champ contient l'hémisphère (E ou W) pour la longitude
        if fields[5] == "W":
            longitude = -longitude
        # l'altitude (Z) est le 10ème champ
        altitude = fields[9]
        # La valeur du capteur est le 16ème et dernier champ
        # On enlève le \n final qui fait partie du champ 
        sensorData = fields[15].rstrip("\n")
        # on écrit les données extraites dans une ligne du fichier final
        extractfileXYZ.write(" ".join([str(longitude), str(latitude), altitude, sensorData])+ "\n")
        # Détermination de la couleur discrète correspondant à la valeur de la donnée
        color = getColor(float(sensorData))
        extractfileRGB.write(" ".join([str(longitude), str(latitude), altitude, color])+ "\n")
# Fermeture des fichiers finaux
extractfileXYZ.close()
extractfileRGB.close()
