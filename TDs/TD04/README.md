# TD04 CSP : Backtracking vs Backtracking + Min-Conflicts

## Contexte

Ce TD implémente deux variantes de résolution de problèmes de satisfaction de contraintes (CSP)
appliquées au coloriage de graphe : chaque variable (nœud) doit recevoir une couleur (valeur)
telle qu'aucune paire de nœuds reliés n'ait la même couleur.

---

## Fichiers

| Fichier | Algorithme |
|---|---|
| `csp_backtracking.py` | Backtracking classique |
| `csp_min_conflicts.py` | Backtracking + heuristique Min-Conflicts (LCV) |

---

## Algorithmes

### Backtracking classique (`csp_backtracking.py`)

Recherche en profondeur (DFS) avec détection précoce d'échec.
Pour chaque variable, les valeurs du domaine sont essayées dans l'ordre fixe `[1, 2, 3, ...]`.
Si une affectation viole une contrainte, on revient en arrière et on essaie la valeur suivante.

- Sélection de variable : ordre fixe (A → B → C → D)
- Sélection de valeur : ordre fixe (1 → 2 → 3 → ...)
- Aucune information sur les conflits futurs n'est exploitée

### Backtracking + Min-Conflicts / LCV (`csp_min_conflicts.py`)

Même structure que le backtracking classique, mais les valeurs sont **triées par nombre de
conflits croissant** avant d'être essayées (heuristique LCV – Least Constraining Value).
La valeur qui génère le moins de violations avec les voisins déjà affectés est essayée en premier.

- Sélection de variable : ordre fixe (identique au classique)
- Sélection de valeur : triée par `nb_conflits` croissant ← **seule différence**
- Guide la recherche vers les branches prometteuses dès le départ

---

## Comparaison

| Critère | Backtracking classique | Backtracking + LCV |
|---|---|---|
| Ordre des valeurs | Fixe | Trié par conflits |
| Backtracks (K4, 4 couleurs) | Nombreux | **0** (solution directe) |
| Implémentation | Simple | +1 fonction `compter_conflits` |
| Complétude | Oui | Oui |
| Optimalité | Non (1ère solution) | Non (1ère solution) |

---

## Résultat sur le graphe K4 (4 variables)

**Backtracking classique** : explore de nombreuses branches avant de trouver une solution.

**Backtracking + LCV** : trouve la solution en 4 essais directs, sans aucun backtrack.
```
A=1 (0 conflit) → B=2 (0 conflit) → C=3 (0 conflit) → D=4 (0 conflit) ✓
```

---

## Meilleur choix

**`csp_min_conflicts.py`** est préférable dans la majorité des cas.

tri des valeurs  négligeable face au gain en exploration évitée.
Sur des problèmes de grande taille, la réduction du nombre de backtracks peut être
considérable, car l'heuristique LCV oriente la recherche dès les premiers niveaux de l'arbre.
