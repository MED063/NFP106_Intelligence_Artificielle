# ChatBot IA — Assistant Santé

Projet Master 1 Intelligence Artificielle — NFP106 — Domaine : **Santé**

## Description

ChatBot IA capable de répondre aux questions sur la santé (maladies chroniques, symptômes, traitements, prévention). Le système intègre les trois piliers fondamentaux de l'intelligence artificielle :

| Pilier | Implémentation | Concepts |
|---|---|---|
| Recherche | Parcours du graphe de connaissances | BFS, DFS, A* |
| Apprentissage | Amélioration continue via les retours utilisateurs | TF-IDF, similarité cosinus, Naïve Bayes |
| Reconnaissance | Compréhension du langage naturel (NLP manuel) | Tokenisation, stemming, NER, classification d'intention |

## Fonctionnalités

- Réponses aux questions sur les maladies, symptômes, causes, facteurs de risque, traitements et prévention
- Classification de l'intention en deux temps : règles par mots-clés (V1), puis filet de sécurité Naïve Bayes entraîné sur les intentions étiquetées des `qa_pairs` (V2)
- Extraction d'entités par matching direct (avec normalisation des accents/ligatures françaises) et distance de Levenshtein (NER)
- Parcours du graphe de connaissances via BFS, DFS et A*, avec comparaison mesurée (chemin, nœuds explorés, temps)
- Sélection de réponse par score de graphe (chevauchement d'entités + proximité + intention), départagée par similarité TF-IDF quand plusieurs Q/A sont ex æquo
- Apprentissage par feedback utilisateur (TF-IDF + Naïve Bayes), re-entraînement automatique tous les 3 retours
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

Compare les trois algorithmes (chemin, nœuds explorés, temps) sur 12 requêtes du graphe de connaissances santé.

## Évaluation (métriques du rapport technique)

```bash
python evaluate.py
```

Calcule les 5 métriques attendues (précision des réponses, précision des intentions, temps de réponse moyen, nœuds explorés BFS vs A*, gain par feedback sur 3 cycles) sur les 62 questions de `qa_pairs.json`. Résultats mesurés sur cette base :

| Métrique | Résultat mesuré | Cible |
|---|---|---|
| Précision des réponses | 96,8 % (60/62) | ≥ 70 % |
| Précision des intentions | 100 % (62/62) | ≥ 80 % |
| Temps de réponse moyen | ~1,4 ms | ≤ 2 s |
| Nœuds explorés (12 requêtes) | BFS 5,2 vs A* 3,0 | A* < BFS |
| Gain par feedback (3 cycles) | +0,0 % | ≥ +5 % |

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
├── evaluate.py           # Rapport d'évaluation (5 métriques du sujet)
├── data/
│   ├── qa_pairs.json        # 62 paires question/réponse
│   ├── knowledge_graph.json # Graphe (36 concepts, 60 relations)
│   └── feedback_log.json    # Historique des retours utilisateur
├── tests/
│   ├── test_knowledge_base.py
│   ├── test_nlp_engine.py
│   ├── test_search_engine.py
│   ├── test_learning_engine.py
│   └── test_main.py
└── requirements.txt
```

## Exemples d'utilisation

```
Vous : Bonjour
Bot  : Bonjour ! Comment puis-je vous aider ?

Vous : Qu'est-ce que le diabète ?
Bot  : Le diabète est une maladie chronique caractérisée par un taux de sucre...

Vous : Quelle est la différence entre le diabète de type 1 et le diabète de type 2 ?
Bot  : Le diabète de type 1 est une maladie auto-immune où le pancréas...

Vous : Comment prévenir l'hypertension ?
Bot  : La prévention de l'hypertension passe par le régime méditerranéen...
```

## Architecture technique

### Pipeline de traitement d'une question

```
Question utilisateur
       ↓
  NLPEngine.preprocess()    # tokenize (+ normalisation accents) → remove_stopwords → stem
       ↓
  NLPEngine.classify_intent()  # V1 regles -> V2 Naive Bayes (filet de securite)
       ↓
  NLPEngine.extract_entities() # matching direct + Levenshtein
       ↓
  SearchEngine.find_best_answer()  # score de graphe, top-k candidats
       ↓
  LearningEngine.rank_answers()    # TF-IDF + cosinus, uniquement en cas d'ex aequo
       ↓
       Réponse
```

### Heuristique A*

L'heuristique utilisée est `h(n) = 1 - Jaccard(bigrammes(n), bigrammes(goal))` (`SearchEngine.heuristic_bigram`). Elle est admissible : la similarité de Jaccard est toujours ≤ 1, donc `h(n) ≥ 0`, et elle ne peut jamais surestimer le coût réel restant (`1 - poids`, lui aussi ≥ 0). Deux concepts orthographiquement proches partagent davantage de bigrammes, ce qui guide la recherche sans jamais la biaiser vers un chemin sous-optimal.

`SearchEngine.compare_algorithms(start, goal)` instrumente les trois algorithmes (nœuds explorés via `self.nodes_explored`, temps via `time.perf_counter`) et retourne un dictionnaire comparatif. Sur les 12 requêtes du benchmark (`benchmark_search.py`), A* explore en moyenne moins de nœuds que BFS (3,0 contre 5,2 — voir `evaluate.py`).

### Sélection de la réponse

`SearchEngine.find_best_answer` note chaque Q/A candidate selon : le chevauchement pondéré par précision entre les entités extraites et les concepts de la Q/A, la proximité de ces concepts dans le graphe, et une forte prime en cas de correspondance d'intention (ex : distinguer une DEFINITION d'un TRAITEMENT sur le même concept). Quand plusieurs Q/A obtiennent le score maximal (ex æquo — cas des concepts strictement identiques comme IMC/obésité), `LearningEngine.rank_answers` les départage par similarité cosinus TF-IDF avec la question d'origine, réponses et requête étant tokenisées par le même pipeline NLP pour rester comparables.

### Classification de l'intention (V1 + V2)

`NLPEngine.classify_intent` applique d'abord des règles par mots-clés (V1). Si aucune règle ne matche, elle délègue à un classifieur Naïve Bayes multinomial (`LearningEngine.train_naive_bayes` / `predict_intent`, implémentation maison) entraîné au démarrage sur les intentions étiquetées des `qa_pairs` (V2), comme filet de sécurité.

### Feedback loop

1. L'utilisateur note la réponse de 1 à 5
2. Tous les 3 retours, `retrain()` est appelé automatiquement
3. Les réponses bien notées (≥ 4) renforcent le TF-IDF et les poids du graphe (+0.05)
4. Les réponses mal notées (≤ 2) pénalisent les poids (-0.05)
5. Le log est sauvegardé dans `feedback_log.json` à la fin de la session

## Limites identifiées

- Base de connaissances limitée à 62 Q/R et 36 concepts
- NLP optimisé pour le français (stemming par règles de suffixes, pas d'embeddings)
- Pas de prise en compte du contexte conversationnel multi-tour
- Heuristique A* basée sur des bigrammes de caractères — proxy simple, pas de vraie sémantique
- Le graphe modélise des relations dirigées génériques (pas explicitement « cause de » vs « associé à ») : sur quelques questions de type CAUSES, une Q/A voisine mais moins pertinente peut l'emporter
- Le mécanisme de feedback ajuste le classement entre réponses déjà connues mais ne comble pas une lacune de la base (concept manquant) ; sur le jeu de test actuel, la précision est déjà proche du plafond donc le gain mesuré par `evaluate.py` est nul (voir tableau ci-dessus) — la démonstration du mécanisme reste effective sur des cas ambigus (ex-aequo)

## Pistes d'amélioration (M2)

- Remplacer le stemming par des embeddings denses (transformers)
- Heuristique A* basée sur la similarité cosinus entre embeddings denses
- Modéliser explicitement la sémantique des relations (cause/conséquence/traitement) plutôt qu'un simple poids
- Architecture distribuée pour la base de connaissances
- Interface web Flask

## Usage IA

Ce projet a été développé avec l'assistance de Claude (Anthropic) pour :
- Génération du squelette initial des modules
- Débogage et refactoring
- Génération des données JSON (qa_pairs, knowledge_graph)
- Génération et amélioration des tests unitaires
- Exploration du sujet pour identifier les exigences manquantes (câblage du Naïve Bayes V2, script d'évaluation des métriques, correction de bugs de scoring et de normalisation d'accents affectant la précision des réponses) et implémentation des correctifs correspondants

Tout le code a été relu, compris et validé par l'auteur. L'auteur est capable d'expliquer chaque décision technique devant le jury.
