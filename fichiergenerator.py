import random

with open("exemple1.txt", "w") as f:
    for i in range(10):
        # Génère une liste de 5 valeurs aléatoires entre 0 et 100
        valeurs = [str(random.randint(0, 100)) for _ in range(5)]
        # Écrit la ligne dans le fichier
        f.write(" ".join(valeurs) + "\n")


with open("exemple2.txt", "w") as f:
    for i in range(10):
        # Génère une liste de 5 valeurs aléatoires entre 0 et 100
        valeurs = [str(random.randint(0, 100)) for _ in range(5)]
        # Écrit la ligne dans le fichier
        f.write(" ".join(valeurs) + "\n")
