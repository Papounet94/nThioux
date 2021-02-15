#!/usr/bin/env python3
"""
Affichage du fichier .XYZRGB en 3D.

La couleur des points reflète l'intensité du signal de mesure
"""

import argparse
import numpy as np
from mpl_toolkits import mplot3d
import matplotlib.pyplot as plt


# Parsing de la ligne de commande pour récupérer les arguments
parser = argparse.ArgumentParser()
parser.add_argument(
    "-i", "--infile",
    help="Nom du fichier .XYZRGB (SANS son extension) 'simu' par défaut",
    default="simu")
args = parser.parse_args()

# Lecture du fichier de points
plotfile = open(args.infile + ".XYZRGB", "r")
lines = plotfile.readlines()
# print(len(lines))
# Réservation des matrices de données
x = np.zeros(len(lines))
y = np.zeros(len(lines))
z = np.zeros(len(lines))
colors = np.zeros((len(lines), 3))

# Itération sur le fichier pour récupérer les données
# et les convertir en float pour x, y, z
# et en float sur [0, 1] pour R, G, B
i = 0
for line in lines:
    vals = line.split(" ")
    x[i] = float(vals[0])
    y[i] = float(vals[1])
    z[i] = float(vals[2])
    colors[i, 0] = float(vals[3])/255.0
    colors[i, 1] = float(vals[4])/255.0
    colors[i, 2] = float(vals[5])/255.0
    i += 1
# print(i)
# Creating figure
fig = plt.figure(figsize=(10, 7))
ax = plt.axes(projection="3d")

# Creating plot
ax.scatter3D(x, y, z, c=colors)
plt.title("simple 3D scatter plot")

# show plot
plt.show()
