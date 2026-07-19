# Tic-Tac-Toe : IA MinMax avec élagage Alpha-Beta

TP02 (NFP106, Intelligence Artificielle) : implémenter un jeu en situation
d'adversité avec l'algorithme **MinMax + élagage Alpha-Beta**, et **visualiser
graphiquement** le fonctionnement de l'algorithme pendant la partie.


## 1. Présentation du jeu

### Description
Un morpion (Tic-Tac-Toe 3×3) jouable dans une fenêtre graphique **Pygame**.
Le joueur humain (**X**) affronte une **IA autonome** (**O**) pilotée par
l'algorithme MinMax avec élagage Alpha-Beta. L'IA joue de manière **optimale** :
elle est **imbattable**, au mieux vous faites match nul.

### Problème résolu
Comment un ordinateur peut-il choisir le **meilleur coup** dans un jeu à deux
joueurs à somme nulle, en supposant que l'adversaire joue lui aussi de façon
optimale ? C'est exactement ce que résout MinMax : il explore l'arbre de toutes
les parties possibles, en **maximisant** le score quand c'est à l'IA de jouer et
en le **minimisant** quand c'est à l'adversaire. L'élagage **Alpha-Beta** coupe
les branches inutiles pour explorer beaucoup moins d'états sans changer le
résultat.

### Public cible
Étudiants / curieux souhaitant **comprendre visuellement** MinMax et Alpha-Beta.
La particularité du projet : l'interface ne fait pas que jouer, elle **montre le
raisonnement de l'IA** à chaque tour.


## 2. Fonctionnalités

### La visualisation de l'algorithme (cœur du projet)
À chaque tour de l'IA, l'interface affiche **graphiquement** :

- **Le score MinMax de chaque case libre**, écrit directement sur la grille :
  - **vert / `+`** = ce coup mène à une victoire de l'IA,
  - **jaune / `0`** = ce coup mène à un match nul,
  - **rouge / `−`** = ce coup mène à une défaite de l'IA.
  - Les scores sont vus **du point de vue de l'IA** (`+10 − profondeur` pour une
    victoire, `−10 + profondeur` pour une défaite), ce qui pousse l'IA à gagner
    **le plus vite** possible et à perdre **le plus tard** possible.
- **La case choisie**, mise en surbrillance verte.
- **Un panneau latéral** avec :
  - le nombre de **nœuds (états) explorés**,
  - le nombre de **branches coupées par l'élagage Alpha-Beta**,
  - la **profondeur maximale** atteinte,
  - une **explication en français** de la décision.
- **Un bouton Alpha-Beta ON/OFF** : activez / désactivez l'élagage et observez
  en direct la **différence de nœuds explorés** (tout l'intérêt d'Alpha-Beta).

### Commandes
| Action | Commande |
|---|---|
| Ouvrir l'aide (règles + visualisation) | Bouton **Comment jouer ?** (affiché au lancement) |
| Jouer un coup (vous êtes **X**) | Clic gauche sur une case |
| Recommencer | Bouton **Nouvelle partie** |
| Afficher / masquer les scores | Bouton **Scores ON/OFF** |
| Activer / désactiver l'élagage | Bouton **Alpha-Beta ON/OFF** |
| Laisser l'IA (O) commencer | Bouton **IA commence** |
| Quitter | Fermer la fenêtre |

### Bonus / améliorations implémentés
- Comparaison en direct **MinMax pur vs Alpha-Beta** (compteur de nœuds).
- Préférence pour la **victoire la plus rapide** (score pondéré par la profondeur).
- **Tests unitaires** vérifiant, entre autres, que l'élagage donne le **même
  résultat** que MinMax pur tout en explorant **moins d'états**, et que l'IA est
  **imbattable**.


## 3. Installation

Prérequis : **Python 3.9+**.

```bash
# (recommandé) créer un environnement virtuel
python3 -m venv .venv
source .venv/bin/activate        # Windows : .venv\Scripts\activate

# installer les dépendances
pip install -r requirements.txt
```

## 4. Lancer le jeu

```bash
python main.py
```

La fenêtre s'ouvre : cliquez sur une case pour jouer contre l'IA.

## 5. Lancer les tests

```bash
pytest -v
```

Les 14 tests couvrent : détection des victoires, choix du coup gagnant, blocage
de l'adversaire, équivalence MinMax/Alpha-Beta, efficacité de l'élagage, et le
fait que l'IA ne perd jamais.


## 6. Démonstration vidéo

Une vidéo de démonstration commentée accompagne ce rendu. Elle a été **transmise
directement par courriel** au professeur, avec le lien vers ce dépôt.

Elle présente successivement :

1. le lancement du jeu et le menu d'aide ;
2. une partie **scores masqués** : l'IA joue bien, mais son raisonnement reste invisible ;
3. la même partie **scores affichés** : on voit l'IA écarter les deux coups menant à une
   fourchette (score −6) et sécuriser le match nul ;
4. la comparaison **Alpha-Beta activé / désactivé** sur une position identique : 497 états
   explorés contre 1 052, pour des scores et un coup choisi rigoureusement identiques ;
5. l'exécution des 14 tests unitaires.


## 7. Structure du projet

```
tp02_tictactoe_minmax/
├── algo.py            # Logique du jeu + MinMax/Alpha-Beta (aucun code graphique)
├── main.py            # Interface Pygame + visualisation de l'algorithme
├── test_algo.py       # 14 tests unitaires (pytest)
├── requirements.txt   # Dépendances
├── README.md          # Ce fichier
└── docummentation_algoMinMax_Morpion.pdf   # Documentation technique détaillée
```

Le découpage `algo.py` / `main.py` isole l'algorithme de l'affichage : le cœur
IA est **testable sans interface graphique**.


## 8. Comment lire l'algorithme dans le code

Fichier `algo.py` :
- `minimax(...)` : la fonction récursive. Nœud **MAX** quand c'est à l'IA,
  nœud **MIN** quand c'est à l'adversaire. L'élagage se fait avec les bornes
  `alpha` / `beta` (`if beta <= alpha: break`).
- `best_move(...)` : parcourt les coups possibles à la racine, appelle `minimax`
  pour chacun, et retourne le meilleur **plus les scores de tous les coups** et
  les **statistiques** (nœuds, élagage), ce sont ces données qui sont
  affichées à l'écran.
- `evaluate(...)` : score des états terminaux (`±(10 − profondeur)`).


## 9. Limites et pistes d'amélioration
- Le morpion 3×3 est **entièrement résoluble** : depuis le plateau vide, MinMax
  pur explore **549 945** états contre **34 202** avec l’élagage (~16× moins),
  ce qui tient sans table de transposition. Pour un plateau plus grand
  (Puissance 4, Gomoku), il faudrait **limiter la profondeur** + une **fonction
  d'évaluation heuristique** des positions non terminales.
- Ajouts possibles : mémoïsation (table de transposition), ordre des coups pour
  un élagage plus agressif, animation pas-à-pas de l'arbre de recherche, mode
  IA vs IA automatique, difficulté réglable (profondeur limitée).


## 10. Usage IA (déclaration obligatoire, §3 du sujet)

Conformément aux règles du TP, l'usage d'outils d'IA est déclaré ici.

**IA utilisée :** Claude (Anthropic).

**1. Pourquoi l'IA a été utilisée**
- Aide ponctuelle sur des parties **hors algorithme** : une fonction utilitaire
  d'affichage (retour à la ligne du texte dans le panneau latéral), deux tests
  de couverture des cas de victoire, et un appui à la rédaction de la
  documentation. Le cœur du projet (logique du jeu et algorithme
  **MinMax + Alpha-Beta** dans `algo.py`) a été écrit et compris par mes soins.

**2. Exemples de prompts / demandes**
- « Comment gérer proprement le retour à la ligne d'un texte dans un panneau
  Pygame de largeur fixe ? »
- « Génère des tests pytest couvrant la détection d'une victoire en colonne, en
  diagonale, et le cas du match nul sur plateau plein. »
- « Relis la structure de ma documentation et suggère une organisation des
  sections. »

**3. Ce qui a été modifié / compris / validé**
- Compréhension et validation du principe MAX/MIN, du rôle des bornes
  `alpha`/`beta`, et de la pondération du score par la profondeur (gagner vite).
- Validation par l'exécution des **14 tests unitaires** (tous verts) et par des
  parties manuelles confirmant que l'IA est **imbattable**.

**4. Encadrement du code généré**
Les blocs produits avec l'IA, soit la fonction utilitaire `_wrap` dans `main.py` et
deux tests de couverture dans `test_algo.py`, tous **hors algorithme**, sont
encadrés dans les fichiers sources par :

```python
# ######## CODE IA (Claude - Anthropic) #########
VOTRE CODE
# ###############################################
```

> Adaptez cette section (prompts réellement utilisés, vos modifications
> personnelles) avant le rendu pour qu'elle reflète votre propre travail.
