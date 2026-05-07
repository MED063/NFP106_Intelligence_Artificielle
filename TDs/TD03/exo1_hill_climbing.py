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

def hill_climbing(depart, but):
    courant, visite, chemin = depart, {depart}, [depart]
    while courant != but:
        candidats = [(H[v], v) for v in GRAPHE[courant] if v not in visite]
        if not candidats or min(candidats)[0] >= H[courant]:
            return chemin, f"echec (optimum local en {courant})"
        courant = min(candidats)[1]
        visite.add(courant)
        chemin.append(courant)
    return chemin, "succes"

if __name__ == "__main__":
    chemin, statut = hill_climbing("A", "J")
    print(f"Chemin : {' → '.join(chemin)}")
    print(f"Statut : {statut}")
