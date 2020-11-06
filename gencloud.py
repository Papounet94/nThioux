#!/usr/bin/env python3
"""
Génération d'un fichier de cloud fictif simulant un nuage de pollution
"""

import argparse, configparser
import math, random

#import pymap3d as pm

def detect(x, y, z):
    """
    Calcul de la valeur du capteur en fonction de sa position vis-à-vis de la zone de pollution.
    On suppose une valeur décroissante exponentiellement en dehors de la zone en 
    horizontal, et constante sur la zone.
    En vertical, on prend une décroissance  exponentiellle  également.
    """
    if (x < x0):
        valx = math.exp((x - (x0 - distance)) / distance) 
    elif (x < x1):
        valx = math.exp(1) 
    else:
        valx = math.exp(((x1 + distance) - x )/ distance) 
    if (y < y0):
        valy = math.exp((y - (y0 - distance)) / distance)
    elif (y < y1):
        valy = math.exp(1) 
    else:
        valy = math.exp(((y1 + distance) - y) / distance) 
    valz = (math.exp(-z / distance))
    return (valx * valy * valz) / 2

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
parser.add_argument("-o", "--outfile", 
    help="Nom des fichiers de sortie (SANS extension) 'simu' par défaut", 
    default="simu")    
parser.add_argument("-s", "--settings", 
    help="Nom du fichier de paramètres (AVEC extension) 'simu.ini' par défaut", 
    default="simu.ini")    
parser.add_argument("-linear", action="store_true", 
    help="Option de sortie linéaire pour la couleur du point")
args = parser.parse_args()

# Choix du type de repésentation des points de couleur
if args.linear :
    getColor = getColorLinear
else:
    getColor = getColorDiscrete

# Ouverture du fichier qui contiendra les valeurs calculées au format XYZ
compfileXYZ = open(args.outfile + ".XYZ", "w")
# Ouverture du fichier qui contiendra les valeurs calculées au format XYZRGB
compfileRGB = open(args.outfile + ".XYZRGB", "w")
# Ouverture du fichier qui contient les valeurs des paramètres de la simulation
config = configparser.ConfigParser()
config.read(args.settings)
# Récupération des paramètres
# Paramètres de la zone scannée
xmin = config.getfloat("SCAN ZONE","xmin")
xmax = config.getfloat("SCAN ZONE","xmax")
ymin = config.getfloat("SCAN ZONE","ymin")
ymax = config.getfloat("SCAN ZONE","ymax")
zmin = config.getfloat("SCAN ZONE","zmin")
zmax = config.getfloat("SCAN ZONE","zmax")
# Paramètres du balayage
xstep = config.getint("STEPS", "xstep")
ystep = config.getint("STEPS", "ystep")
zstep = config.getint("STEPS", "zstep")
# Précision des vols
hdop = config.getint("PRECISION", "hdop")
vdop = config.getint("PRECISION", "vdop")
# Zone de pollution
largeur = config.getint("POLLUTION", "largeur")
longueur = config.getint("POLLUTION", "longueur")
# Position du centre de la zone  de pollution
centerx = config.getfloat("POLLUTION", "centerx")
centery = config.getfloat("POLLUTION", "centery")
# distance de décroissance de valeur du capteur
distance = config.getfloat("POLLUTION", "distance")
random.seed()
# Calcul des limites de la zone de pollution
x0 = centerx - largeur / 2 
x1 = centerx + largeur / 2 
y0 = centery - longueur / 2 
y1 = centery + longueur / 2 
# Calcul du cloud
for i in range(xstep + 1): # coordonnée x
    for j in range(ystep + 1): # coordonnée y
        for k in range(zstep + 1): # coordonnée z
            # Calcul des coordonnées x, y, z dans la zone de balayage
            # avec un facteur aléatoire 
            x = xmin + i * (xmax - xmin) / xstep + ((random.random() - 0.5 * 2) * hdop)
            y = ymin + j * (ymax - ymin) / ystep + ((random.random() - 0.5 * 2) * hdop)
            z = zmin + k * (zmax - zmin) / zstep + ((random.random() - 0.5 * 2) * vdop)
            # Calcul de la valeur du capteur à ces coordonnées
            val = detect(x, y, z)
            # Ecriture dans les fichiers ligne par ligne
            compfileXYZ.write(" ".join([str(x), str(y), str(z), str(val)]) + "\n")
            color = getColor(float(val))
            compfileRGB.write(" ".join([str(x), str(y), str(z), color])+ "\n")
# Fermeture des fichiers finaux
compfileXYZ.close()
compfileRGB.close()
