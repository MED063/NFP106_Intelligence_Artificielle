from collections import deque
from typing import Optional, List
import heapq
import time


# Intentions pour lesquelles la question porte sur les causes/facteurs
# d'un concept (l'effet) plutot que sur ses consequences : le graphe
# oriente ne modelisant que 'cause -> effet', il faut alors remonter les
# relations entrantes (get_predecessors) plutot que les sortantes.
CAUSAL_INTENTS = {'CAUSES', 'FACTEURS_RISQUE'}

# Parmi les relations entrantes, seules les vraies relations causales
# comptent pour une question CAUSES/FACTEURS_RISQUE. On exclut ainsi les
# associations bidirectionnelles ('associe_a', ex : hypertension <-> AVC ou
# diabete <-> obesite, mutuellement facteurs de risque) qui, comptees comme
# des causes, faisaient remonter une Q/A voisine a la place de la bonne.
CAUSAL_RELATION_TYPES = {'cause_de'}


class SearchEngine:
    def __init__(self, kb):
        self.kb = kb
        self.nodes_explored = 0

    def bfs(self, start: str, goal: str) -> Optional[List]:
        self.nodes_explored = 0
        if start not in self.kb.graph:
            return None
        queue = deque([(start, [start])])
        visited = {start}
        while queue:
            node, path = queue.popleft()
            self.nodes_explored += 1
            if node == goal:
                return path
            for neighbor in self.kb.get_neighbors(node):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        return None

    def dfs(self, start: str, goal: str, max_depth: int = 10) -> Optional[List]:
        self.nodes_explored = 0
        if start not in self.kb.graph:
            return None

        def _dfs(node, path, depth):
            self.nodes_explored += 1
            if node == goal:
                return path
            if depth == 0:
                return None
            for neighbor in self.kb.get_neighbors(node):
                if neighbor not in path:
                    result = _dfs(neighbor, path + [neighbor], depth - 1)
                    if result is not None:
                        return result
            return None

        return _dfs(start, [start], max_depth)

    def a_star(self, start: str, goal: str, heuristic) -> Optional[List]:
        self.nodes_explored = 0
        if start not in self.kb.graph:
            return None
        open_set = [(0, start, [start])]
        g_scores = {start: 0}
        while open_set:
            f, node, path = heapq.heappop(open_set)
            self.nodes_explored += 1
            if node == goal:
                return path
            for neighbor, weight in self.kb.get_neighbors(node).items():
                g = g_scores.get(node, float('inf')) + (1.0 - weight)
                if g < g_scores.get(neighbor, float('inf')):
                    g_scores[neighbor] = g
                    h = heuristic(neighbor, goal)
                    heapq.heappush(open_set, (g + h, neighbor, path + [neighbor]))
        return None

    def heuristic_bigram(self, node: str, goal: str) -> float:
        """h(n) = 1 - Jaccard(bigrammes(n), bigrammes(goal)).
        Admissible : Jaccard <= 1 donc h >= 0, et le cout reel d'une arete
        (1 - poids) est aussi >= 0 ; h ne peut donc pas surestimer le cout restant.
        """
        def bigrams(word):
            return {word[i:i + 2] for i in range(len(word) - 1)} or {word}

        b1, b2 = bigrams(node), bigrams(goal)
        return 1.0 - len(b1 & b2) / len(b1 | b2)

    def compare_algorithms(self, start: str, goal: str) -> dict:
        """Compare BFS, DFS et A* sur une requete : chemin, noeuds explores, temps."""
        results = {}
        runs = (
            ('BFS', lambda: self.bfs(start, goal)),
            ('DFS', lambda: self.dfs(start, goal)),
            ('A*', lambda: self.a_star(start, goal, self.heuristic_bigram)),
        )
        for name, run in runs:
            t0 = time.perf_counter()
            path = run()
            elapsed = time.perf_counter() - t0
            results[name] = {
                'path': path,
                'nodes_explored': self.nodes_explored,
                'time': elapsed,
            }
        return results

    def find_best_answer(self, entities: list, intent: str, top_k: int = 5) -> List[tuple]:
        """Explore les Q/A liees aux entites via le graphe et retourne les
        `top_k` plus pertinentes sous forme de tuples (score, reponse),
        tries par score de graphe decroissant (chevauchement d'entites +
        proximite dans le graphe + correspondance d'intention). Les scores
        sont conserves pour permettre au ChatBot de ne departager par
        similarite TF-IDF (LearningEngine.rank_answers) que les reponses
        reellement ex-aequo — ex : IMC et obesite partagent exactement les
        memes concepts et ne peuvent etre distinguees que par le texte de
        la question d'origine."""
        if not entities:
            return []
        entity_set = set(entities)
        candidates = []
        for qa in self.kb.qa_pairs:
            qa_concepts = set(qa.get('concepts', []))
            overlap = entity_set & qa_concepts
            if not overlap:
                continue
            precision = len(overlap) / len(qa_concepts) if qa_concepts else 0.0
            score = 2.0 * len(overlap) * precision
            for entity in entities:
                # Pour une question CAUSES/FACTEURS_RISQUE, seules les
                # relations entrantes (X -> entite, X = cause) sont
                # pertinentes : les relations sortantes de l'entite
                # representent ses consequences, pas ses causes, et les
                # compter ici favorisait des Q/A hors sujet (ex : les
                # complications de l'hypertension quand on demande ses
                # causes).
                related = (
                    self.kb.get_predecessors(entity, types=CAUSAL_RELATION_TYPES)
                    if intent in CAUSAL_INTENTS
                    else self.kb.get_neighbors(entity)
                )
                score += sum(related[c] for c in qa_concepts if c in related)
            if intent == qa.get('intent', ''):
                score += 10.0
            candidates.append((score, qa.get('answer', '')))
        if not candidates:
            return []
        candidates.sort(key=lambda x: x[0], reverse=True)
        return candidates[:top_k]
