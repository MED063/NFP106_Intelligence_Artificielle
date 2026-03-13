# TD01 — Réponses aux questions de comparaison des algorithmes

**Cours** : NFP106 — Intelligence Artificielle (CNAM)
**Algorithmes comparés** : BFS, DFS, UCS (modes 1, 2, 3)

---

## Question 1 — Quelle recherche semble trouver la solution le plus rapidement ?

### Réponse

**UCS mode 3 (Manhattan)** trouve la solution le plus rapidement, suivi de **BFS**, puis **UCS mode 2 (colonnes)**, puis **UCS mode 1 (aléatoire)**, et enfin **DFS** qui est le moins prévisible.


### Pourquoi UCS mode 3 gagne

Avec des coûts = distance de Manhattan jusqu'à E, les cases **les plus proches de E** sont les **moins chères**. UCS extrait toujours le nœud au coût cumulé minimal, donc il priorise naturellement les cases qui rapprochent de l'arrivée. Le résultat est une exploration très dirigée, similaire à A* avec heuristique Manhattan.



---

## Question 2 — Avantages et inconvénients de chaque recherche

### BFS (Breadth-First Search)

| | |
|--|--|
| **Avantages** | • Garantit le chemin **le plus court en nombre de pas** (optimalité en pas) |
| | • **Complet** : trouve toujours une solution si elle existe |
| | • Simple à implémenter (`deque` FIFO) |
| | • Comportement prévisible et régulier |
| **Inconvénients** | • Ne tient pas compte des **coûts** des cases (traite tous les déplacements comme équivalents) |
| | • Consomme beaucoup de **mémoire** (stocke toute une couche à la fois) |
| | • Explore beaucoup de nœuds inutiles dans des labyrinthes larges |
| **Cas idéal** | Graphe non pondéré, on veut le chemin avec le moins de pas |

---

### DFS (Depth-First Search)

| | |
|--|--|
| **Avantages** | • Faible consommation **mémoire** (pile proportionnelle à la profondeur) |
| | • Peut trouver **très rapidement** une solution si la bonne branche est choisie en premier |
| | • Utile pour détecter des **cycles** ou explorer toutes les branches |
| **Inconvénients** | • **Pas optimal** : le chemin trouvé peut être très long |
| | • Comportement **imprévisible** : dépend totalement de l'ordre des voisins |
| | • Peut explorer tout le labyrinthe avant de trouver E alors que E est juste à côté |
| | • Ne tient pas compte des coûts |
| **Cas idéal** | Exploration complète, détection de cycles, labyrinthe avec une seule solution |

---

### UCS mode 1 — Coûts aléatoires

| | |
|--|--|
| **Avantages** | • **Optimal en coût** : garantit le chemin de coût cumulé minimal |
| | • Complet |
| | • Simule un terrain réel avec des zones plus ou moins difficiles à traverser |
| **Inconvénients** | • **Aucun guidage** vers l'objectif : explore dans toutes les directions selon les coûts |
| | • Peut explorer plus de nœuds que BFS si les coûts sont défavorables |
| | • La solution optimale en coût peut être plus longue en nombre de pas |
| **Cas idéal** | Graphe pondéré sans information sur la position de E |

---

### UCS mode 2 — Coûts = distance en colonnes jusqu'à E

| | |
|--|--|
| **Avantages** | • **Guidage horizontal** : favorise les cases dans la même colonne que E |
| | • Explore moins de nœuds que le mode 1 dans les labyrinthes où E est à droite |
| | • Toujours optimal en coût |
| **Inconvénients** | • **Ignore la distance verticale** : ne tient pas compte des lignes |
| | • Peut favoriser des chemins qui longent la bonne colonne mais ne descendent pas |
| | • Heuristique **non admissible** en général (peut surestimer dans certains cas) |
| **Cas idéal** | Labyrinthe où E est dans une colonne bien identifiable et accessible horizontalement |

---

### UCS mode 3 — Coûts = distance de Manhattan jusqu'à E

| | |
|--|--|
| **Avantages** | • **Heuristique admissible et cohérente** pour un graphe 4-connexe |
| | • Explore un **minimum de nœuds** : se comporte comme A* |
| | • Combine optimalité en coût ET guidage spatial |
| | • Très efficace sur des labyrinthes de taille raisonnable |
| **Inconvénients** | • Le coût des cases n'est plus "libre" — il est imposé par la distance à E |
| | • En présence de nombreux murs entre la case et E, la distance Manhattan peut être trop optimiste |
| | • Plus complexe à concevoir que les coûts aléatoires |
| **Cas idéal** | Tout labyrinthe 4-connexe où on veut minimiser le nombre de nœuds explorés |

---



---

## Question 3 — Recherche non informée plus optimale pour le labyrinthe

La recherche non informée la plus adaptée à ce labyrinthe serait le **BFS bidirectionnel** : on lance un BFS depuis `S` et un autre depuis `E` simultanément, et on s'arrête dès que les deux frontières se rejoignent.

Par rapport au BFS classique, il explore environ **deux fois moins de nœuds** tout en garantissant le chemin optimal en nombre de pas, sans utiliser aucune information sur la position de l'arrivée.

---


