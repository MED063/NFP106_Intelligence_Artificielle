# ChatBot IA — Assistant Informatique

Projet Master 1 Intelligence Artificielle — NFP106 — Domaine : **Informatique**

## Description

ChatBot IA capable de répondre aux questions d'informatique (algorithmes, structures de données, langages de programmation, IA). Le système intègre les trois piliers fondamentaux de l'intelligence artificielle :

| Pilier | Implémentation | Concepts |
|---|---|---|
| Recherche | Parcours du graphe de connaissances | BFS, DFS, A* |
| Apprentissage | Amélioration continue via les retours utilisateurs | TF-IDF, similarité cosinus, Naïve Bayes |
| Reconnaissance | Compréhension du langage naturel (NLP manuel) | Tokenisation, stemming, NER, classification d'intention |

## Fonctionnalités

- Réponses aux questions sur Python, algorithmes, structures de données, IA, etc.
- Classification automatique de l'intention (DEFINITION, EXPLICATION, COMPARAISON, EXEMPLE, LISTE, QUESTION)
- Extraction d'entités par matching direct et distance de Levenshtein (NER)
- Parcours du graphe de connaissances via BFS, DFS et A*
- Apprentissage par feedback utilisateur (TF-IDF + Naïve Bayes)
- Re-entraînement automatique tous les 3 retours utilisateurs
- Interface CLI interactive

## Prérequis

- Python 3.10+
- numpy, pytest (voir `requirements.txt`)

## Installation

```bash
git clone https://github.com/MED063/NFP106_Intelligence_Artificielle.git
cd NFP106_Intelligence_Artificielle/projet/chatbot_ia
pip install -r requirements.txt
```

## Lancement

```bash
python main.py
```

## Tests

```bash
pytest tests/ -v
```

## Benchmark BFS / DFS / A*

```bash
python benchmark_search.py
```

Compare les trois algorithmes (chemin, nœuds explorés, temps) sur 12 requêtes du graphe de connaissances.

## Structure du projet

```
chatbot_ia/
├── main.py              # Point d'entrée + classe ChatBot
├── ui.py                # Interface CLI
├── nlp_engine.py        # Tokenisation, stemming, NER, classification d'intention
├── knowledge_base.py    # Graphe de connaissances orienté pondéré
├── search_engine.py     # BFS / DFS / A* + comparaison (nœuds explorés, temps)
├── learning_engine.py   # TF-IDF / similarité cosinus / Naïve Bayes / feedback
├── benchmark_search.py  # Comparaison BFS/DFS/A* sur 12 requêtes du graphe
├── data/
│   ├── qa_pairs.json        # 55 paires question/réponse
│   ├── knowledge_graph.json # Graphe (50 concepts, 62 relations)
│   └── feedback_log.json    # Historique des retours utilisateur
├── tests/
│   ├── test_knowledge_base.py
│   ├── test_nlp_engine.py
│   ├── test_search_engine.py
│   └── test_learning_engine.py
└── requirements.txt
```

## Exemples d'utilisation

```
Vous : Bonjour
Bot  : Bonjour ! Comment puis-je vous aider ?

Vous : Qu'est-ce que Python ?
Bot  : Python est un langage de programmation interprété, de haut niveau...

Vous : Quelle est la différence entre BFS et DFS ?
Bot  : BFS explore le graphe niveau par niveau (en largeur)...

Vous : Comment fonctionne A* ?
Bot  : A* est un algorithme de recherche de chemin heuristique...
```

## Architecture technique

### Pipeline de traitement d'une question

```
Question utilisateur
       ↓
  NLPEngine.preprocess()    # tokenize → remove_stopwords → stem
       ↓
  NLPEngine.classify_intent()  # règles + Naïve Bayes
       ↓
  NLPEngine.extract_entities() # matching direct + Levenshtein
       ↓
  SearchEngine.find_best_answer()  # BFS/A* sur le graphe
       ↓
  LearningEngine.rank_answers()    # TF-IDF + cosinus
       ↓
       Réponse
```

### Heuristique A*

L'heuristique utilisée est `h(n) = 1 - Jaccard(bigrammes(n), bigrammes(goal))` (`SearchEngine.heuristic_bigram`). Elle est admissible : la similarité de Jaccard est toujours ≤ 1, donc `h(n) ≥ 0`, et elle ne peut jamais surestimer le coût réel restant (`1 - poids`, lui aussi ≥ 0). Deux concepts orthographiquement proches partagent davantage de bigrammes, ce qui guide la recherche sans jamais la biaiser vers un chemin sous-optimal.

`SearchEngine.compare_algorithms(start, goal)` instrumente les trois algorithmes (nœuds explorés via `self.nodes_explored`, temps via `time.perf_counter`) et retourne un dictionnaire comparatif. Sur les 12 requêtes du benchmark (`benchmark_search.py`), A* explore systématiquement autant ou moins de nœuds que BFS (ex. `algorithme -> arbre` : 12 nœuds pour BFS contre 7 pour A*).

### Feedback loop

1. L'utilisateur note la réponse de 1 à 5
2. Tous les 3 retours, `retrain()` est appelé automatiquement
3. Les réponses bien notées (≥ 4) renforcent le TF-IDF et les poids du graphe (+0.05)
4. Les réponses mal notées (≤ 2) pénalisent les poids (-0.05)
5. Le log est sauvegardé dans `feedback_log.json` à la fin de la session

## Limites identifiées

- Base de connaissances limitée à 55 Q/R et 50 concepts
- NLP optimisé pour le français (stemming par règles de suffixes)
- Pas de prise en compte du contexte conversationnel multi-tour
- Heuristique A* basée sur des bigrammes de caractères — proxy simple, pas de vraie sémantique

## Pistes d'amélioration (M2)

- Remplacer le stemming par des embeddings denses (transformers)
- Heuristique A* basée sur la similarité cosinus entre embeddings denses
- Architecture distribuée pour la base de connaissances
- Interface web Flask

## Usage IA

Ce projet a été développé avec l'assistance de Claude (Anthropic) pour :
- Génération du squelette initial des modules
- Débogage et refactoring
- Génération des données JSON (qa_pairs, knowledge_graph)
- Génération et amélioration des tests unitaires

Tout le code a été relu, compris et validé par l'auteur. L'auteur est capable d'expliquer chaque décision technique devant le jury.
