import math, random

H = {"A":9, "B":7, "C":8, "D":6, "E":5, "F":7, "G":4, "H":5, "I":6, "J":3}

GRAPHE = {
    "A": ["B", "C"],
    "B": ["A", "D", "E"],
    "C": ["A", "F"],
    "D": ["B"],
    "E": ["B", "G", "H"],
    "F": ["C", "I"],
    "G": ["E"],
    "H": ["E"],
    "I": ["F", "J"],
    "J": ["I"],
}

def recuit_simule(depart, but, T=5.0, T_min=0.3, alpha=0.92):
    courant, meilleur, chemin = depart, depart, [depart]
    while T > T_min and courant != but:
        voisin = random.choice(GRAPHE[courant])
        delta = H[voisin] - H[courant]
        if delta <= 0 or random.random() < math.exp(-delta / T):
            courant = voisin
            chemin.append(courant)
            if H[courant] < H[meilleur]:
                meilleur = courant
        T *= alpha
    statut = "succes" if courant == but else f"froid — meilleur atteint : {meilleur} (h={H[meilleur]})"
    return chemin, statut

if __name__ == "__main__":
    chemin, statut = recuit_simule("A", "J")
    print(f"Chemin : {' → '.join(chemin)}")
    print(f"Statut : {statut}")
