# ChatBot IA : Assistant Santé

Projet du Master 1 TRIED - UE : Intelligence Artificielle - Code UE : NFP106 - Domaine : **Santé**

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
- Deux interfaces au choix : CLI interactive (`main.py`) et interface web Flask (`web_app.py`)
- Reformulation optionnelle des réponses par un LLM (approche RAG, désactivée par défaut)

## Prérequis

- Python 3.10+
- numpy, pytest, flask (voir `requirements.txt`)

## Installation

```bash
git clone https://github.com/MED063/NFP106_Intelligence_Artificielle.git
cd NFP106_Intelligence_Artificielle/projet/chatbot_ia
pip install -r requirements.txt
```

## Lancement

Interface en ligne de commande :

```bash
python main.py
```

Interface web (Flask) :

```bash
python web_app.py
```

puis ouvrir http://127.0.0.1:5000 dans un navigateur. L'interface (thème clair/sombre automatique) envoie les questions au point d'entrée `/ask` (réponse JSON) et permet de noter chaque réponse de 1 à 5 via `/feedback` ; le modèle se ré-entraîne automatiquement tous les 3 retours, comme en CLI. Le bot est instancié une seule fois au démarrage et partagé entre les requêtes.

Un interrupteur en haut de page (« Reformulation IA ») permet d'**activer ou désactiver le LLM optionnel** sans redémarrer, via les points d'entrée `/llm/status` et `/llm/toggle` ; il affiche le modèle utilisé et signale l'absence de clé API le cas échéant.

L'interface **rend visibles les trois piliers de l'IA** à chaque réponse : un panneau « Analyse » affiche l'**intention détectée** et les **entités extraites** (reconnaissance), et un **graphe de connaissances interactif** dessine le sous-graphe exploré autour des concepts, avec les arêtes colorées par type de relation (`cause_de`, `associe_a`, `traite_par`…) et les nœuds cliquables pour rebondir d'un concept à l'autre (recherche). Deux fonctions natives du navigateur complètent l'ensemble : la **saisie vocale** (Web Speech API) et la **lecture à voix haute** des réponses. Le point d'entrée `/ask` renvoie désormais, en plus de la réponse, l'intention, les entités et le sous-graphe typé.

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

Calcule les 5 métriques attendues (précision des réponses, précision des intentions, temps de réponse moyen, nœuds explorés BFS vs A*, gain par feedback sur 3 cycles) sur les 79 questions de `qa_pairs.json`. Résultats mesurés sur cette base :

| Métrique | Résultat mesuré | Cible |
|---|---|---|
| Précision des réponses | 100 % (79/79) | ≥ 70 % |
| Précision des intentions | 100 % (79/79) | ≥ 80 % |
| Temps de réponse moyen | ~1,5 ms | ≤ 2 s |
| Nœuds explorés (12 requêtes) | BFS 5,5 vs A* 3,1 | A* < BFS |
| Gain par feedback (3 cycles) | +20 % (73,3 % → 93,3 %) | ≥ +5 % |

La métrique de feedback est mesurée sur un jeu de **reformulations inédites** (questions « utilisateur » jamais vues à l'entraînement), car les 79 `qa_pairs` sont déjà répondues à 100 % — sans marge de progression mesurable. Certaines reformulations sont initialement mal routées (intention mal détectée ou entité non reconnue) ; en 3 cycles, l'utilisateur pénalise la mauvaise réponse et enseigne la bonne, et la précision passe de 73,3 % à 93,3 %.

## Structure du projet

```
chatbot_ia/
├── main.py              # Point d'entrée + classe ChatBot (journalisation)
├── config.py            # Configuration centralisée (chemins, paramètres, logs, LLM)
├── llm_engine.py        # Reformulation LLM optionnelle (RAG, API compatible OpenAI)
├── ui.py                # Interface CLI
├── web_app.py           # Interface web Flask (/, /ask, /feedback, /llm, statut)
├── templates/
│   └── index.html       # Page de discussion (markup de l'interface web)
├── static/
│   └── style.css        # Feuille de style de l'interface web
├── nlp_engine.py        # Tokenisation, stemming, NER, classification d'intention
├── knowledge_base.py    # Graphe de connaissances orienté pondéré (relations typées)
├── search_engine.py     # BFS / DFS / A* + comparaison (nœuds explorés, temps)
├── learning_engine.py   # TF-IDF / similarité cosinus / Naïve Bayes / feedback
├── benchmark_search.py  # Comparaison BFS/DFS/A* sur 12 requêtes du graphe
├── evaluate.py           # Rapport d'évaluation (5 métriques du sujet)
├── data/
│   ├── qa_pairs.json        # 79 paires question/réponse
│   ├── knowledge_graph.json # Graphe (46 concepts, 80 relations typées)
│   └── feedback_log.json    # Historique des retours utilisateur
├── tests/
│   ├── test_knowledge_base.py
│   ├── test_nlp_engine.py
│   ├── test_search_engine.py
│   ├── test_learning_engine.py
│   ├── test_main.py
│   ├── test_web_app.py
│   ├── test_config.py
│   └── test_llm_engine.py
└── requirements.txt
```

### Configuration et journalisation

Le module `config.py` centralise en un seul endroit les chemins de données (`DATA_DIR`, `KNOWLEDGE_GRAPH`, `QA_PAIRS`, `FEEDBACK_LOG`), les paramètres de comportement (`FEEDBACK_RETRAIN_EVERY`, `LEVENSHTEIN_MAX_DISTANCE`) et la configuration des logs. Les interfaces (`main.py`, `ui.py`, `web_app.py`) importent ces valeurs plutôt que de coder des constantes en dur, ce qui facilite l'ajustement du comportement sans toucher au code métier.

La classe `ChatBot` journalise via `config.get_logger()` chaque question reçue, l'intention détectée et les cas sans réponse, dans le fichier `chatbot.log` (niveau et emplacement configurables dans `config.py`). Le logger est idempotent (pas de handler dupliqué) et n'écrit pas sur la sortie standard, pour ne pas interférer avec la CLI ni les tests.

### Option : reformulation par un LLM (RAG)

Le module `llm_engine.py` permet, **de façon facultative**, de reformuler les réponses en langage naturel à l'aide d'un modèle de langage. L'approche est du **RAG** (retrieval-augmented generation) : le moteur maison (graphe + TF-IDF) reste le cœur qui *trouve* la réponse, et le LLM ne fait que la *reformuler* à partir de ce contexte, sans avoir le droit d'inventer d'information médicale. Il sert aussi de filet de secours quand aucune réponse n'est trouvée. Toute erreur (clé absente, réseau, délai) fait retomber sur la réponse brute du moteur maison : le LLM ne peut jamais casser le pipeline.

L'option est **désactivée par défaut** (`USE_LLM=False`) : le système fonctionne intégralement sans LLM et sans dépendance supplémentaire (appels via `urllib` standard). Elle est compatible avec toute API « OpenAI-compatible ». Exemple avec l'offre gratuite de Groq (créer une clé sur console.groq.com, sans carte bancaire) :

```bash
export USE_LLM=1
export LLM_API_KEY="votre_cle_groq"
# valeurs par défaut : Groq + openai/gpt-oss-20b
# (lister les modèles de ta clé : curl .../v1/models ; surcharger avec LLM_MODEL)
python web_app.py     # ou python main.py
```

Pour un autre fournisseur (Mistral, endpoint compatible Gemini, serveur local Ollama…), il suffit de surcharger `LLM_API_BASE` et `LLM_MODEL`. La clé est toujours lue dans l'environnement, jamais écrite dans le dépôt.

> Avertissement : les réponses de l'assistant, avec ou sans LLM, sont fournies à titre informatif et ne remplacent pas un avis médical professionnel. Lorsque le LLM est activé, la précision mesurée par `evaluate.py` (comparaison mot à mot avec la réponse de référence) n'est plus pertinente : le LLM sert le confort de lecture, pas la métrique.

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

`SearchEngine.compare_algorithms(start, goal)` instrumente les trois algorithmes (nœuds explorés via `self.nodes_explored`, temps via `time.perf_counter`) et retourne un dictionnaire comparatif. Sur les 12 requêtes du benchmark (`benchmark_search.py`), A* explore en moyenne moins de nœuds que BFS (3,1 contre 5,5 — voir `evaluate.py`).

### Sélection de la réponse

`SearchEngine.find_best_answer` note chaque Q/A candidate selon : le chevauchement pondéré par précision entre les entités extraites et les concepts de la Q/A, la proximité de ces concepts dans le graphe, et une forte prime en cas de correspondance d'intention (ex : distinguer une DEFINITION d'un TRAITEMENT sur le même concept). Quand plusieurs Q/A obtiennent le score maximal (ex æquo — cas des concepts strictement identiques comme IMC/obésité), `LearningEngine.rank_answers` les départage par similarité cosinus TF-IDF avec la question d'origine, réponses et requête étant tokenisées par le même pipeline NLP pour rester comparables.

Pour les intentions CAUSES et FACTEURS_RISQUE, la proximité dans le graphe est mesurée via `KnowledgeBase.get_predecessors` (relations entrantes, X → entité) plutôt que `get_neighbors` (relations sortantes) : le graphe étant orienté « cause → effet », les relations sortantes d'un concept représentent ses conséquences, pas ses causes ; les compter y faisait remonter des Q/A hors sujet (ex : les complications de l'hypertension quand la question porte sur ses causes).

### Relations typées du graphe

Chaque arête du graphe porte un **type sémantique** (`cause_de`, `associe_a`, `traite_par`, `symptome`, `affecte`, `previent`) en plus de son poids. Ce typage lève l'ambiguïté des relations bidirectionnelles entre concepts comorbides : lorsque deux pathologies sont mutuellement facteurs de risque l'une de l'autre (ex : hypertension ↔ AVC, ou diabète ↔ obésité), le graphe contient une arête dans chaque sens. Sans distinction, `get_predecessors` remontait l'arête inverse comme une « cause » et faisait gagner une Q/A voisine. En marquant ces liens `associe_a` (association) plutôt que `cause_de`, les requêtes CAUSES/FACTEURS_RISQUE (`SearchEngine.find_best_answer` via `get_predecessors(entity, types={'cause_de'})`) ne remontent plus que les vraies causes. Le typage reste optionnel : une relation sans type demeure un simple lien pondéré (rétro-compatibilité), et les algorithmes de recherche (BFS/DFS/A*) continuent d'utiliser le graphe pondéré tel quel.

### Classification de l'intention (V1 + V2)

`NLPEngine.classify_intent` applique d'abord des règles par mots-clés (V1). Si aucune règle ne matche, elle délègue à un classifieur Naïve Bayes multinomial (`LearningEngine.train_naive_bayes` / `predict_intent`, implémentation maison) entraîné au démarrage sur les intentions étiquetées des `qa_pairs` (V2), comme filet de sécurité.

### Feedback loop

1. L'utilisateur note la réponse de 1 à 5
2. La note ajuste **directement le classement des réponses futures** via `LearningEngine.feedback_score` : une note ≥ 4 renforce l'association question/réponse, une note ≤ 2 la pénalise (et l'utilisateur peut enseigner la bonne réponse). L'ajustement est ajouté au score de graphe dans `ChatBot.answer` ; sans aucun feedback il est nul, donc le comportement par défaut est inchangé
3. Tous les 3 retours, `retrain()` est appelé automatiquement : re-entraînement du TF-IDF sur les réponses bien notées et ajustement des poids du graphe (+0.05 / −0.05)
4. Le log est sauvegardé dans `feedback_log.json` à la fin de la session

Ce mécanisme est mesuré par la métrique 5 (`evaluate.py`) : sur un jeu de reformulations inédites, la précision passe de 73,3 % à 93,3 % (+20 %) en 3 cycles.

## Limites identifiées

- Base de connaissances limitée à 79 Q/R et 46 concepts
- NLP optimisé pour le français (stemming par règles de suffixes, pas d'embeddings)
- Pas de prise en compte du contexte conversationnel multi-tour
- Heuristique A* basée sur des bigrammes de caractères — proxy simple, pas de vraie sémantique
- Le graphe distingue causes et conséquences via `get_predecessors`, et le typage des relations (`cause_de` vs `associe_a`) lève désormais l'ambiguïté des relations bidirectionnelles entre concepts comorbides (ex : hypertension ↔ AVC). Le typage reste renseigné manuellement, à maintenir à jour lors de l'ajout de nouvelles relations
- Le mécanisme de feedback réordonne des réponses déjà présentes dans la base : il corrige un mauvais routage (intention/entité) sur une reformulation, mais ne comble pas une lacune de la base (concept absent). Ainsi, une question dont aucune entité n'est reconnue ne renvoie aucun candidat et reste hors de portée du feedback (cas « obèse » ≠ concept `obesite` par la distance de Levenshtein) — d'où 14/15 et non 15/15 sur le jeu de démonstration

## Pistes d'amélioration (M2)

- Remplacer le stemming par des embeddings denses (transformers)
- Heuristique A* basée sur la similarité cosinus entre embeddings denses
- Architecture distribuée pour la base de connaissances
- Inférer automatiquement le type des relations plutôt que de le renseigner à la main

## Usage IA

Conformément aux règles du sujet, voici où j'ai utilisé un assistant IA (Claude, Anthropic) et où je ne l'ai pas fait.

Le cœur du projet, je l'ai écrit moi-même : les trois piliers et leurs algorithmes (tokenisation, stemming, NER par distance de Levenshtein, classification d'intention, graphe de connaissances, parcours BFS/DFS/A* avec heuristique admissible, TF-IDF, similarité cosinus, Naïve Bayes, boucle de feedback). Cela couvre `nlp_engine.py`, `knowledge_base.py`, `search_engine.py`, `learning_engine.py` et `main.py`.

L'IA m'a servi sur le pourtour du projet, sans toucher à la logique des piliers :
- Interface web Flask (`web_app.py`, `templates/`, `static/`)
- Suite de tests `pytest` (dossier `tests/`)
- Configuration et journalisation centralisées (`config.py`)
- Connecteur LLM optionnel de reformulation (`llm_engine.py`)
- Extension des données JSON (`qa_pairs`, `knowledge_graph`) et script de mesure des métriques (`evaluate.py`)
- Débogage (scoring, normalisation des accents), et rédaction brève de ce README et de la documentation

Les portions de code écrites avec l'assistance de l'IA sont encadrées dans les fichiers par un bandeau `# CODE IA (Claude - Anthropic)`. Chaque proposition a été relue, testée puis intégrée à la main ; la validation s'appuie sur l'exécution des tests unitaires et sur les cinq métriques mesurées par `evaluate.py`.
