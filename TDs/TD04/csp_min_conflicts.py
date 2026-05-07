"""
CSP - Backtracking avec heuristique Min-Conflicts
"""


def est_coherent(variable, valeur, affectation, contraintes):
    """Verifie que la valeur ne viole aucune contrainte avec les vars deja assignees."""
    for (x, y) in contraintes:
        if x == variable and y in affectation:
            if affectation[y] == valeur:
                return False
        if y == variable and x in affectation:
            if affectation[x] == valeur:
                return False
    return True


def compter_conflits(variable, valeur, affectation, contraintes):
    """Retourne le nombre de conflits que genere valeur pour variable
    avec les variables deja affectees."""
    conflits = 0
    for (x, y) in contraintes:
        if x == variable and y in affectation:
            if affectation[y] == valeur:
                conflits += 1
        if y == variable and x in affectation:
            if affectation[x] == valeur:
                conflits += 1
    return conflits

def backtracking_min_conflicts(variables, domaines, contraintes, affectation=None):
    """Backtracking ou les valeurs sont essayees par ordre croissant
    de conflits (heuristique Min-Conflicts / LCV).
    """
    if affectation is None:
        affectation = {}

    # Cas de base : toutes les variables affectees => solution trouvee
    if len(affectation) == len(variables):
        return affectation

    # Selectionner la prochaine variable non affectee (ordre fixe)
    variable = next(v for v in variables if v not in affectation)

    # --- Min-Conflicts (LCV) ---
    #  valeur qui gene le moins les voisins deja assignes.
    valeurs_triees = sorted(
        domaines[variable],
        key=lambda v: compter_conflits(variable, v, affectation, contraintes)
    )

    for valeur in valeurs_triees:
        nb = compter_conflits(variable, valeur, affectation, contraintes)
        print(f"  Essai : {variable} = {valeur}  (conflits={nb}) | Affectation : {affectation}")

        if est_coherent(variable, valeur, affectation, contraintes):
            affectation[variable] = valeur

            resultat = backtracking_min_conflicts(variables, domaines, contraintes, affectation)
            if resultat is not None:
                return resultat

            # Backtrack : la valeur n'a pas mene a une solution
            print(f"  Backtrack sur {variable} = {valeur}")
            del affectation[variable]

    return None  # Aucune valeur possible => echec, on remonte


if __name__ == "__main__":
    # --- Exemple du cours : graphe K4 avec 4 couleurs ---
    variables   = ["A", "B", "C", "D"]
    domaines    = {v: [1, 2, 3, 4] for v in variables}
    contraintes = [("A", "B"), ("A", "D"), ("A", "C"), ("B", "C"), ("B", "D"), ("C", "D")]

    print("=== Backtracking + Min-Conflicts (LCV) ===")
    print(f"Variables   : {variables}")
    print(f"Domaines    : {domaines}")
    print(f"Contraintes : {contraintes}")
    print()

    solution = backtracking_min_conflicts(variables, domaines, contraintes)

    print()
    if solution:
        print(f"Solution trouvee : {solution}")
    else:
        print("Aucune solution.")

    # --- Exemple sans solution : K3 avec 2 couleurs ---
    print("\n=== Exemple sans solution (K3, 2 couleurs) ===")
    variables2   = ["A", "B", "C"]
    domaines2    = {v: [1, 2] for v in variables2}
    contraintes2 = [("A", "B"), ("A", "C"), ("B", "C")]

    solution2 = backtracking_min_conflicts(variables2, domaines2, contraintes2)
    print()
    if solution2:
        print(f"Solution trouvee : {solution2}")
    else:
        print("Aucune solution.")
