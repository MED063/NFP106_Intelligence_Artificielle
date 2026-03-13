# DFS : Visualisation Interactive du Parcours en Profondeur

## Table des matières

1. [Présentation du projet](#présentation-du-projet)
2. [Objectifs pédagogiques](#objectifs-pédagogiques)
3. [Architecture générale](#architecture-générale)
4. [Algorithmes implémentés](#algorithmes-implémentés)
5. [Fonctions complétées](#fonctions-complétées)
6. [Installation et exécution](#installation-et-exécution)
7. [Guide d'utilisation](#guide-dutilisation)
8. [Concepts d'IA enseignés](#concepts-dia-enseignés)
9. [Remarques pédagogiques](#remarques-pédagogiques)

---

## Présentation du projet

Ce projet fait partie du cours **NFP106 - Intelligence Artificielle** du CNAM. Il implémente une visualisation interactive du **DFS (Depth-First Search / Parcours en Profondeur)** sur un labyrinthe avec une interface graphique moderne utilisant **Pygame**.

### Caractéristiques principales

- **Visualisation en temps réel** : observez le pingouin explorer le labyrinthe pas à pas
- **Mode automatique et manuel** : explorez le DFS en continu ou étape par étape
- **Brouillard de guerre** : activation/désactivation pour voir le "champ de vision" de l'algorithme
- **Comparaison BFS/DFS** : le BFS est aussi implémenté pour calculer le chemin optimal et le contraster avec le DFS
- **Interface moderne** : thème sombre avec couleurs contrastées et animation fluide

### Labyrinthe de démonstration

```
#######################
#S#.......#...........#
#.#.#####.#.#####.###.#
#.#.....#.......#...#.#
#.#####.#.###.#.###.#.#
#.....#.#...#.#.....#.#
###.#.#.###.#.#####.#.#
#...#.#.....#.....#.#E#
#.###.###########.#.###
#.....................#
#######################
```

**Légende** :
- `#` : mur (non traversable)
- `.` : sol traversable
- `S` : position de départ
- `E` : position d'arrivée (sortie)

---

## Objectifs pédagogiques

Ce TD vise à enseigner les concepts fondamentaux de la recherche en graphe :

1. **Comprendre les structures de données** : files (FIFO) et piles (LIFO)
2. **Maîtriser le DFS** : un algorithme de parcours fondamental en IA
3. **Comparer DFS avec BFS** : différences et cas d'usage respectifs
4. **Visualiser l'exploration** : voir comment l'algorithme construit progressivement un arbre couvrant
5. **Implémenter des algorithmes incrémentaux** : exécuter pas à pas (approche réactive)
6. **Appliquer à des problèmes réels** : utiliser la recherche pour résoudre un problème de cheminement

---

## Architecture générale

### Structure du fichier `DFS_a_completer.py`

| Section | Contenu |
|---------|---------|
| **0. Imports** | Dépendances : `pygame`, `collections.deque`, `math`, `random` |
| **1. Paramètres** | Constantes : taille des cases, FPS, vitesses d'animation |
| **2. Thème moderne** | Palette de couleurs (fond, murs, overlays DFS, brouillard) |
| **3. Outils grille** | Fonctions utilitaires : `hauteur`, `largeur`, `voisins_4`, etc. |
| **4. BFS Solution** | Implémentation BFS incrémentale ← **TODO complétés** |
| **4bis. DFS** | Implémentation DFS incrémentale ← **TODO complétés** |
| **5. Pingouin** | Génération des sprites et animation du personnage |
| **6. Route parent** | Reconstruction de chemin via LCA (ancêtre commun) |
| **7. Outils dessin** | Fonctions de rendu graphique (bevel, overlay RGBA, glow) |
| **8. Application** | Classe `AppliDFS` et boucle événementielle Pygame |

---

## Algorithmes implémentés

### BFS : Breadth-First Search (Parcours en Largeur)

#### Principe

Le BFS explore le graphe **couche par couche** depuis le nœud de départ. Il utilise une **file FIFO (First In First Out)** : le premier nœud enfilé est le premier traité.

```
BFS(grille, départ, arrivée):
    file ← File([départ])
    visité ← {départ}
    parent[départ] ← NIL
    dist[départ] ← 0

    tant que file non vide:
        nœud ← file.popleft()          ← FIFO : le plus ancien
        si nœud == arrivée → SUCCÈS

        pour chaque voisin de nœud:
            si NON visité:
                visité.add(voisin)
                parent[voisin] ← nœud
                dist[voisin] ← dist[nœud] + 1
                file.append(voisin)

    retourner ÉCHEC
```

#### Propriétés BFS

| Propriété | Valeur |
|-----------|--------|
| Optimalité | **Oui** — garantit le chemin le plus court |
| Complétude | Oui — trouve une solution si elle existe |
| Complexité temps | O(V + E) |
| Complexité espace | O(V) |
| Structure | File FIFO (`deque`) |

---

### DFS : Depth-First Search (Parcours en Profondeur)

#### Principe

Le DFS explore le graphe **en profondeur** : il descend le plus loin possible dans une branche avant de revenir en arrière. Il utilise une **pile LIFO (Last In First Out)** : le dernier nœud empilé est le premier traité.

```
DFS(grille, départ, arrivée):
    pile ← Pile([départ])
    visité ← {départ}
    parent[départ] ← NIL
    profondeur[départ] ← 0

    tant que pile non vide:
        nœud ← pile.pop()              ← LIFO : le plus récent
        si nœud == arrivée → SUCCÈS

        pour chaque voisin de nœud (en ordre INVERSE):
            si NON visité:
                visité.add(voisin)
                parent[voisin] ← nœud
                profondeur[voisin] ← profondeur[nœud] + 1
                pile.append(voisin)

    retourner ÉCHEC
```

> **Pourquoi l'ordre inverse ?**
> `voisins_4()` génère les voisins dans l'ordre : Haut, Bas, Gauche, Droite.
> Avec une pile (`pop()` = dernier élément), pour *visiter* dans cet ordre, on doit *empiler* dans l'ordre inverse : Droite, Gauche, Bas, Haut — ainsi Haut sera dépilé en premier.

#### Propriétés DFS

| Propriété | Valeur |
|-----------|--------|
| Optimalité | **Non** — chemin trouvé arbitraire |
| Complétude | Oui — trouve une solution si elle existe |
| Complexité temps | O(V + E) |
| Complexité espace | O(V) |
| Structure | Pile LIFO (liste Python) |

---

### BFS vs DFS : tableau comparatif

| Aspect | BFS | DFS |
|--------|-----|-----|
| **Structure** | `deque` (FIFO) | `list` (LIFO) |
| **Extraction** | `popleft()` | `pop()` |
| **Insertion voisins** | ordre normal | ordre **inverse** |
| **Ordre d'exploration** | largeur d'abord | profondeur d'abord |
| **Chemin retourné** | **optimal** (plus court) | arbitraire |
| **`dist[n]`** | distance réelle en pas | profondeur DFS |
| **Usage dans ce projet** | calcul chemin optimal (offline) | exploration principale (animée) |

---

## Fonctions complétées

### 1. `bfs_initialiser(depart)`

**Rôle** : créer l'état initial du BFS (dictionnaire avec tous les champs nécessaires).

```python
return {
    "file": deque([depart]),   # file FIFO
    "visite": {depart},
    "parent": {depart: None},
    "dist": {depart: 0},
    "ordre": {depart: 1},
    "prochain_id": 2,
    "courant": None,
    "termine": False,
    "trouve": False,
}
```

---

### 2. `bfs_faire_une_etape(grille, etat, arrivee)`

**Rôle** : exécuter **une** itération du BFS (un nœud traité par appel).

Étapes :
1. Si `termine` → return immédiat
2. Si file vide → `termine=True, trouve=False`
3. `courant = etat["file"].popleft()` (FIFO)
4. Si `courant == arrivee` → `termine=True, trouve=True`
5. Pour chaque voisin non visité : l'ajouter à `visite`, `parent`, `dist` (dist+1), `ordre`, et l'enfiler

---

### 3. `bfs_reconstruire_chemin(parent, depart, arrivee)`

**Rôle** : reconstruire le chemin optimal en remontant l'arbre des parents.

```python
# Remonter de arrivee → depart via parent
chemin = []
cur = arrivee
while cur is not None:
    chemin.append(cur)
    cur = parent[cur]
chemin.reverse()
# Vérifier que ça commence bien au départ
```

---

### 4. `bfs_cout_optimal(dist, arrivee)`

**Rôle** : retourner la distance BFS jusqu'à l'arrivée, ou `None` si non atteinte.

```python
return dist.get(arrivee, None)
```

---

### 5. `dfs_initialiser(depart)`

**Rôle** : créer l'état initial du DFS. Identique à `bfs_initialiser` **sauf** que la file est une **liste** (pile LIFO) au lieu d'une `deque`.

```python
return {
    "file": [depart],          # pile LIFO (liste Python)
    "visite": {depart},
    "parent": {depart: None},
    "dist": {depart: 0},       # profondeur DFS, pas distance réelle
    "ordre": {depart: 1},
    "prochain_id": 2,
    "courant": None,
    "termine": False,
    "trouve": False,
}
```

---

### 6. `dfs_faire_une_etape(grille, etat, arrivee)`

**Rôle** : exécuter **une** itération du DFS (un nœud traité par appel).

Différences clés par rapport au BFS :
- Extraction : `courant = etat["file"].pop()` (LIFO, pas `popleft`)
- Voisins empilés en **ordre inverse** : `for rr, cc, _ in reversed(voisins)`

```python
voisins = list(voisins_4(grille, courant[0], courant[1]))
for rr, cc, _ in reversed(voisins):   # ← ordre inverse = visite dans l'ordre normal
    nxt = (rr, cc)
    if nxt not in etat["visite"]:
        etat["visite"].add(nxt)
        etat["parent"][nxt] = courant
        etat["dist"][nxt] = etat["dist"][courant] + 1
        etat["ordre"][nxt] = etat["prochain_id"]
        etat["prochain_id"] += 1
        etat["file"].append(nxt)
```

---

## Installation et exécution

### Prérequis

- **Python 3.7+**
- **Pygame 2.0+**

### Installation de Pygame

```bash
pip install pygame
```

### Lancement

```bash
cd /chemin/vers/TD01
python3 DFS_a_completer.py
```

---

## Guide d'utilisation

### Commandes clavier

| Touche | Action |
|--------|--------|
| `E` | Lancer le DFS en mode **automatique** |
| `ESPACE` | DFS **pas à pas** (une étape par appui) |
| `P` | Animer le **chemin optimal BFS** |
| `R` | **Réinitialiser** complètement |
| `F` | **Brouillard** on/off |
| `Q` | **Quitter** |

### Interface visuelle

| Couleur | Signification |
|---------|---------------|
| Bleu clair | Case **visitée** par le DFS |
| Jaune/orange | **Frontière** (pile DFS = cases à explorer) |
| Bleu vif | Case **courante** (nœud en cours de traitement) |
| Vert | **Chemin optimal** BFS (touche P) |
| Violet | **Rebroussement** du pingouin (LCA) |

### Workflow typique

1. Lancer le programme
2. Appuyer sur **E** → observer l'exploration DFS automatique
3. Appuyer sur **R** → réinitialiser
4. Appuyer sur **ESPACE** plusieurs fois → DFS pas à pas
5. Appuyer sur **P** → voir le chemin optimal BFS (comparaison)
6. Appuyer sur **F** → activer/désactiver le brouillard

---

## Concepts d'IA enseignés

### 1. Recherche en graphe

Deux stratégies fondamentales :
- **BFS** : garantit le chemin optimal (exploration systématique en largeur)
- **DFS** : explore une branche jusqu'au bout avant de revenir (peut trouver vite, mais pas optimal)

### 2. Structures de données et leur impact

Le **choix de la structure** détermine entièrement le comportement de l'algorithme :
- Remplacer `deque.popleft()` par `list.pop()` transforme un BFS en DFS
- File FIFO → exploration en largeur → optimalité
- Pile LIFO → exploration en profondeur → pas d'optimalité

### 3. Reconstruction de chemin via les parents

Mémoriser le **parent** de chaque nœud découvert permet de reconstruire le chemin sans re-explorer le graphe.

### 4. Algorithmes incrémentaux

Découper l'algorithme en **étapes unitaires** (`faire_une_etape`) permet :
- La visualisation pas à pas
- La réactivité de l'interface (pas de blocage)
- Le débogage facile

### 5. Représentation de grille

- Indexage `(r, c)` (ligne, colonne) vs `(x, y)` (pixel)
- Voisinage **4-connexe** : Haut, Bas, Gauche, Droite
- Conversion case → pixel : `x = c * TAILLE_CASE`, `y = HAUT_BAR_H + r * TAILLE_CASE`

### 6. Complexité algorithmique

| Algorithme | Temps | Espace |
|------------|-------|--------|
| BFS | O(V + E) | O(V) |
| DFS | O(V + E) | O(V) |

Même complexité théorique, mais comportement pratique très différent selon le graphe.

---

## Remarques pédagogiques

### Points clés à retenir

1. **Une seule ligne change tout** : `popleft()` (BFS) vs `pop()` (DFS)
2. **L'ordre des voisins compte** : avec une pile, empiler en ordre inverse pour visiter dans l'ordre attendu
3. **DFS ≠ optimal** : le BFS séparé est nécessaire pour afficher le vrai chemin court
4. **`dist` a un sens différent** : distance réelle (BFS) vs profondeur d'exploration (DFS)

### Extensions possibles

- Implémenter **A\*** avec heuristique (distance de Manhattan)
- Ajouter **Dijkstra** pour des graphes pondérés
- Implémenter la recherche **bidirectionnelle** (depuis départ ET arrivée)
- Comparer visuellement le nombre de nœuds explorés par BFS vs DFS

---

**Cours** : NFP106 — Intelligence Artificielle (CNAM)
**TD** : TD01 — Parcours de graphes (BFS / DFS)
**Fichier** : `DFS_a_completer.py`
