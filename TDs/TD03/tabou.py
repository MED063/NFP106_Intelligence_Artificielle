from collections import deque

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

def recherche_tabou(depart, but, max_tabou=3):
    courant, meilleur = depart, depart
    tabou = deque(maxlen=max_tabou)
    tabou.append(courant)

    while courant != but:
        candidats = [(H[v], v) for v in GRAPHE[courant] if v not in tabou]
        if not candidats:
            return meilleur, "bloqué (tous voisins tabous)"
        _, courant = min(candidats)
        tabou.append(courant)
        if H[courant] < H[meilleur]:
            meilleur = courant

    return meilleur, "succes"

if __name__ == "__main__":
    meilleur, statut = recherche_tabou("A", "J")
    print(f"Meilleur : {meilleur} (h={H[meilleur]})")
    print(f"Statut   : {statut}")