# TD03 — Algorithmes d'Exploration Locale

## Contexte

Ce TD compare deux algorithmes d'exploration locale appliqués à un graphe et à un labyrinthe, puis propose un troisième algorithme alternatif.

Le graphe utilisé :

```
A(9) — B(7) — D(6)
 |      |
C(8)   E(5) — G(4)
 |      |
F(7)   H(5)
 |
I(6) — J(3) ← but
```

Les valeurs entre parenthèses sont les heuristiques `h` (distance estimée au but). L'objectif est d'aller de `A` à `J` en minimisant `h`.

---

## 1. Hill Climbing

### Principe

À chaque étape, l'algorithme choisit le voisin avec la **plus petite heuristique `h`**, à condition qu'il améliore la position courante. Il s'arrête dès qu'aucun voisin n'améliore la situation.


### Avantages

| Critère | Détail |
|---|---|
| Rapidité | O(b) par étape (b = nombre de voisins ≤ 4). Très faible coût de calcul. |
| Mémoire | Stocke uniquement le chemin courant. Négligeable. |
| Simplicité | Facile à implémenter et à comprendre. |
| Déterminisme | Toujours le même résultat pour le même graphe — reproductible et débogable. |
| Efficace si convexe | Optimal sur un espace sans optima locaux. |

### Inconvénients

| Critère | Détail |
|---|---|
| Optima locaux | Bloque si tous les voisins ont un `h` supérieur, même si la solution existe. |
| Plateaux | Peut errer si plusieurs voisins ont le même `h`. |
| Incomplétude | Ne garantit pas de trouver une solution même si elle existe. |
| Pas de backtracking | Aucun retour en arrière possible — un mauvais choix est fatal. |
| Sensible à l'heuristique | Une heuristique mal calibrée mène directement à l'échec. |

---

## 2. Recuit Simulé

### Principe

Inspiré du refroidissement des métaux : à **haute température**, l'algorithme accepte des dégradations pour explorer ; à **basse température**, il se comporte comme un Hill Climbing et exploite.



### Avantages

| Critère | Détail |
|---|---|
| Échappe aux optima locaux | Accepte parfois des dégradations — peut sortir d'un cul-de-sac. |
| Complétude asymptotique | Avec un refroidissement assez lent, converge vers l'optimum global en théorie. |
| Généricité | S'applique à presque tout problème d'optimisation sans contrainte structurelle. |
| Flexible | Un seul paramètre de compromis (la température) pilote exploration/exploitation. |

### Inconvénients

| Critère | Détail |
|---|---|
| Non déterministe | Résultats différents à chaque exécution (sauf seed fixée). |
| Calibration délicate | `T_init`, `alpha`, `iter_par_T` doivent être choisis avec soin selon le problème. |
| Lenteur possible | Un refroidissement trop progressif allonge considérablement le temps d'exécution. |
| Aucune garantie finie | Peut ne jamais trouver la solution optimale en temps limité. |
| Débogage difficile | Le caractère aléatoire rend les bugs difficiles à reproduire. |

---

## 3. Comparaison directe

| Critère | Hill Climbing | Recuit Simulé |
|---|---|---|
| Complétude | Non | Oui (asymptotique) |
| Optimalité | Non | Oui (asymptotique) |
| Optima locaux | Bloquant | Contournés |
| Déterminisme | Oui | Non |
| Complexité mémoire | O(chemin) | O(chemin) |
| Paramètres à régler | 0 | 3 |
| Facilité d'impl. | Très simple | Modérée |
| Usage typique | Espaces convexes, temps réel | Optimisation combinatoire |

**Verdict  :** le recuit simulé est supérieur quand l'espace est non convexe (la distance Manhattan ne reflète pas la distance réelle derrière les murs) et comporte des optima locaux. Le Hill Climbing s'y bloque systématiquement.

---

## 4. Troisième algorithme proposé : Recherche Tabou

### Idée

La **Recherche Tabou** (Glover, 1986) ajoute une **liste de mémoire à court terme** qui interdit de revisiter les états récemment explorés. Elle accepte des dégradations de façon **déterministe** — sans aléatoire.




### Avantages par rapport aux deux autres

| Critère | Hill Climbing | Recuit Simulé | Recherche Tabou |
|---|:---:|:---:|:---:|
| Échappe aux optima locaux | Non | Oui | **Oui** |
| Déterministe | Oui | Non | **Oui** |
| Paramètres | 0 | 3 | **1** (taille liste) |
| Mémoire des états | Non | Non | **Oui** |
| Évite les cycles | Non | Non | **Oui** |

- **Déterministe comme HC, mais sans ses blocages** — reproductible et débogable.
- **Un seul paramètre** à calibrer : la taille de la liste tabou.
- **Critère d'aspiration** : peut ignorer la liste tabou si un état est exceptionnellement bon.
- **Évite les oscillations** que le recuit simulé peut produire en phase chaude.

### Inconvénients

- La taille de la liste tabou influence fortement le comportement : trop petite → cycles courts, trop grande → blocage.
- Peut manquer la solution optimale si la liste tabou bloque tous les voisins utiles.
- Moins adapté aux très grands espaces d'état où une liste courte est insuffisante.

---

