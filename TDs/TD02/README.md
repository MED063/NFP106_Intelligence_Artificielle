# TD02 — Stratégies d'exploration informées (heuristiques)

**Cours** : NFP106 — Intelligence Artificielle, CNAM

---

## Réponses aux questions

---

### Question 1 — Quelle recherche semble trouver la solution le plus rapidement ?

**Réponse : le Glouton (exo2.py)**

Le Glouton est généralement le plus rapide à trouver *une* solution car il explore uniquement dans la direction qui minimise h(n), c'est-à-dire la case qui semble la plus proche du but. Il ignore complètement le coût du chemin déjà parcouru et fonce directement vers la sortie.

Sur le labyrinthe du TD (grille 11×23 avec couloirs contraints), le Glouton explore un nombre de nœuds nettement inférieur à A* avant d'atteindre E, car il ne "regarde pas en arrière".


---

### Question 2 — Avantages et inconvénients de chaque recherche

#### A* Standard (`exo1.py`) — `f = g + h`

| Avantages | Inconvénients |
|-----------|---------------|
| **Optimal** : garantit le chemin de coût minimal (si h admissible) | Explore davantage de nœuds que le Glouton |
| **Complet** : trouve toujours une solution s'il en existe une | Plus lent sur les grands labyrinthes |
| Bien adapté quand les coûts de cases varient (sable, eau…) | Consommation mémoire plus élevée (open set plus grand) |
| Comportement prévisible et prouvable mathématiquement | — |

#### Glouton / GBFS (`exo2.py`) — `f = h`

| Avantages | Inconvénients |
|-----------|---------------|
| **Très rapide** : peu de nœuds explorés | **Non optimal** : peut trouver un chemin coûteux |
| Simple à implémenter | Peut se "piéger" dans des culs-de-sac avant d'en sortir |
| Efficace sur des environnements "ouverts" sans obstacles complexes | Ignore totalement le coût déjà parcouru |
| Faible consommation mémoire | Comportement difficile à prévoir dans un labyrinthe tortueux |

#### A* Pondéré (`exo3.py`) — `f = g + w × h`

| Avantages | Inconvénients |
|-----------|---------------|
| **Paramétrable** : `w` ajuste le compromis vitesse/optimalité | Nécessite de choisir `w` selon le contexte |
| **Garantie bornée** : coût ≤ w × coût optimal | Non optimal dès que `w > 1` |
| Plus rapide qu'A* standard pour `w > 1` | Dégradation de qualité difficile à anticiper sans connaître le labyrinthe |
| Unifie A* (`w=1`) et Glouton (`w→∞`) dans un seul algorithme | — |

---

### Question 3 — Proposer une recherche informée plus optimale pour le labyrinthe

#### Analyse du labyrinthe du TD

Le labyrinthe est une grille **11×23**, 4-connexe, avec :
- Des **coûts d'entrée variables** par case (1 à 4)
- Des **couloirs étroits** et bifurcations multiples
- Une topologie contrainte (peu de chemins directs vers E)

#### Proposition : A* Bidirectionnel (Bidirectional A*)

**A* Bidirectionnel** :

```
Principe : lancer deux recherches A* simultanément —
  - une depuis S vers E  (recherche forward)
  - une depuis E vers S  (recherche backward)
  - arrêter quand les deux frontières se rejoignent
```

**Pourquoi c'est plus optimal ici :**

- Sur une grille de taille N, A* standard explore O(N) nœuds.
  A* bidirectionnel explore environ O(√N) nœuds dans chaque direction, soit O(2√N) au total — bien inférieur.
- Le labyrinthe a des chemins longs et sinueux : la frontière d'exploration "grossit" vite. En partant des deux côtés, chaque frontière reste petite.
- Le chemin reste **optimal** si les deux heuristiques sont admissibles et cohérentes.

**Implémentation  :**

```python
def astar_bidirectionnel(grille, depart, arrivee, couts):
    # Deux états A* indépendants
    etat_fwd = astar_initialiser(depart, arrivee)    # forward : S → E
    etat_bwd = astar_initialiser(arrivee, depart)    # backward : E → S

    mu = float("inf")   # meilleur coût de chemin complet trouvé

    while not (etat_fwd["termine"] and etat_bwd["termine"]):
        # Avancer la frontière la plus prometteuse (f minimal)
        if meilleur_f(etat_fwd) <= meilleur_f(etat_bwd):
            astar_faire_une_etape(grille, etat_fwd, arrivee, couts)
            courant = etat_fwd["courant"]
            # Vérifier si ce nœud est connu de la recherche inverse
            if courant in etat_bwd["visite"]:
                mu = min(mu, etat_fwd["g"][courant] + etat_bwd["g"][courant])
        else:
            astar_faire_une_etape(grille, etat_bwd, depart, couts)
            courant = etat_bwd["courant"]
            if courant in etat_fwd["visite"]:
                mu = min(mu, etat_fwd["g"][courant] + etat_bwd["g"][courant])

        # Critère d'arrêt : mu ≤ meilleur_f(fwd) + meilleur_f(bwd)
        if mu <= meilleur_f(etat_fwd) + meilleur_f(etat_bwd):
            break

    return reconstruire_chemin_bidir(etat_fwd["parent"], etat_bwd["parent"],
                                     depart, arrivee, mu)
```

#
---
