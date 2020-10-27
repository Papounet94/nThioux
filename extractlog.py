#!/usr/bin/env python3
"""
Extraction des informations présentes dans les logs récupérés sur le drone pour en faire
un fichier exploitable par Potree
"""

import argparse

import pymap3d as pm

def valid_latitude(angle):
    """ Fonction déterminant si une latitude est bien comprise entre -180° et +180°
    """
    value = float(angle)
    if (value < -180.0) or (value > 180.0) :
        msg = "%r n'est pas une Latitude valide [-180, +180]" % angle
        raise argparse.ArgumentTypeError(msg)
    return value

def valid_longitude(angle):
    """ Fonction déterminant si une longitude est bien comprise entre -90° et +90°
    """
    value = float(angle)
    if (value < -90.0) or (value > 90.0) :
        msg = "%r n'est pas une Longitude valide [-90, +90]" % angle
        raise argparse.ArgumentTypeError(msg)
    return value

def getColorDiscrete(value) :
    """ Fonction donnant la couleur correspondant à une valeur donnée
    en fonction d'une table prédéfinie.
    + Modif THX du 1810
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
parser.add_argument("-lat0", type=valid_latitude,
    help="Latitude de Référence en degrés décimaux")
parser.add_argument("-lon0", type=valid_longitude,
    help="Longitude de Référence en degrés décimaux")
parser.add_argument("-alt0", type=float,
    help="Altitude de Référence en mètres")
    
args = parser.parse_args()

# Choix du type de repésentation des points de couleur
if args.linear :
    getColor = getColorLinear
else:
    getColor = getColorDiscrete

# le switch -dd est supprimé et on passe obligatoirement  en degrés décimaux
divider = 100

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
# Une valeur booléenne pour déterminer la position  de l'Observateur à partir
# de la 1ère ligne de données si elle n'est pas passée en paramètres
firstLine = True
# Itération sur chaque ligne du fichier
for line in lines:
    # On ne regarde que les lignes commençant par $GPGGA
    if line.startswith("$GPGGA"):
        # On récupère tous les champs de la ligne dans une liste
        fields = line.split(",")
        # On vérifie que ue TOUS les 16 champs sont présents et que le GPS est correct
        # 7ème champ = 0 ==> GPS incorrect
        # print(len(fields))
        if (len(fields) == 16) and (fields[6] != '0'):
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
            altitude = float(fields[9])
            # Extraction de la position de l'Observateur de la première ligne
            if firstLine :
                firstLine = False
                # La Latitude de référence est-elle définie ?
                if not(args.lat0):
                    lat0 = latitude
                else:
                    lat0 = args.lat0
                # La Longitude de référence est-elle définie ?
                if not(args.lon0):
                    lon0 = longitude
                else:
                    lon0 = args.lon0
                # L'Altutude de référence est-elle définie ?
                if not(args.alt0):
                    alt0 = altitude
                else:
                    alt0=args.alt0

            # Conversion du triplet Latitude, Longitude, Altitude en distances 
            # North, East, Up par rapport  à l'Observateur situé à la Latitude, 
            # la Longitude et l'Altitude de référence.
            east, north, up = pm.geodetic2enu(latitude, longitude, altitude, lat0, lon0, alt0)
            # La valeur du capteur est le 16ème et dernier champ
            # On enlève le \n final qui fait partie du champ 
            sensorData = fields[15].rstrip("\n")
            # on écrit les données extraites dans une ligne du fichier final au format texte
            extractfileXYZ.write(" ".join([str(east), str(north), str(up), sensorData])+ "\n")
            # Détermination de la couleur discrète correspondant à la valeur de la donnée
            color = getColor(float(sensorData))
            extractfileRGB.write(" ".join([str(east), str(north), str(up), color])+ "\n")
# Fermeture des fichiers finaux
extractfileXYZ.close()
extractfileRGB.close()
