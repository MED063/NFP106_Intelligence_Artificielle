"""
CSP Backtracking 
"""


def est_coherent(variable, valeur, affectation, contraintes):
    """Verif que la valeur ne viole aucune contrainte avec les vars deja assignees."""
    for (x, y) in contraintes:
        if x == variable and y in affectation:
            if affectation[y] == valeur:
                return False
        if y == variable and x in affectation:
            if affectation[x] == valeur:
                return False
    return True


def backtracking(variables, domaines, contraintes, affectation=None):
    if affectation is None:
        affectation = {}

    # Toutes les variables sont assignées : solution trouvée
    if len(affectation) == len(variables):
        return affectation

    # Choisir la prochaine variable non assignée 
    variable = next(v for v in variables if v not in affectation)

    for valeur in domaines[variable]:
        print(f"  Essai : {variable} = {valeur}  | Affectation courante : {affectation}")

        if est_coherent(variable, valeur, affectation, contraintes):
            affectation[variable] = valeur

            resultat = backtracking(variables, domaines, contraintes, affectation)
            if resultat is not None:
                return resultat

            # Backtrack
            print(f"  Backtrack sur {variable} = {valeur}")
            del affectation[variable]

    return None  # Aucune valeur possible : échec


if __name__ == "__main__":
    # 
    variables   = ["A", "B", "C", "D"]
    domaines    = {v: [1, 2, 3] for v in variables}
    contraintes = [("A", "B"), ("A", "D"), ("A", "C"), ("B", "C"), ("B", "D"), ("C", "D")]

    print("=== CSP Backtracking ===")
    print(f"Variables : {variables}")
    print(f"Domaines  : {domaines}")
    print(f"Contraintes (≠) : {contraintes}")
    print()

    solution = backtracking(variables, domaines, contraintes)

    print()
    if solution:
        print(f"Solution trouvée : {solution}")
    else:
        print("Aucune solution.")

    
    print("\n=== Exemple sans solution ===")
    variables2   = ["A", "B", "C"]
    domaines2    = {v: [1, 2] for v in variables2}
    contraintes2 = [("A", "B"), ("A", "C"), ("B", "C")]

    solution2 = backtracking(variables2, domaines2, contraintes2)
    print()
    if solution2:
        print(f"Solution trouvée : {solution2}")
    else:
        print("Aucune solution.")
