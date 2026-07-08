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

## Structure du projet

```
chatbot_ia/
├── main.py              # Point d'entrée + classe ChatBot
├── ui.py                # Interface CLI
├── nlp_engine.py        # Tokenisation, stemming, NER, classification d'intention
├── knowledge_base.py    # Graphe de connaissances orienté pondéré
├── search_engine.py     # BFS / DFS / A*
├── learning_engine.py   # TF-IDF / similarité cosinus / Naïve Bayes / feedback
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

L'heuristique utilisée est `h(n) = 0` (heuristique nulle, garantissant l'admissibilité). En M2, elle sera remplacée par une similarité cosinus basée sur des embeddings denses. Avec `h = 0`, A* se comporte comme Dijkstra et garantit le chemin de coût minimal. Le coût d'une arête est `1 - poids`, ce qui favorise les relations fortement pondérées.

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
- Heuristique A* triviale (nulle) — à améliorer avec des embeddings en M2

## Pistes d'amélioration (M2)

- Remplacer le stemming par des embeddings denses (transformers)
- Heuristique A* basée sur la similarité cosinus entre embeddings
- Architecture distribuée pour la base de connaissances
- Interface web Flask

## Usage IA

Ce projet a été développé avec l'assistance de Claude (Anthropic) pour :
- Génération du squelette initial des modules
- Débogage et refactoring
- Génération des données JSON (qa_pairs, knowledge_graph)
- Génération et amélioration des tests unitaires

Tout le code a été relu, compris et validé par l'auteur. L'auteur est capable d'expliquer chaque décision technique devant le jury.
