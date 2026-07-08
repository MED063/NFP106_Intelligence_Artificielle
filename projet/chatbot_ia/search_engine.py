from collections import deque
from typing import Optional, List
import heapq


class SearchEngine:
    def __init__(self, kb):
        self.kb = kb

    def bfs(self, start: str, goal: str) -> Optional[List]:
        if start not in self.kb.graph:
            return None
        queue = deque([(start, [start])])
        visited = {start}
        while queue:
            node, path = queue.popleft()
            if node == goal:
                return path
            for neighbor in self.kb.get_neighbors(node):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        return None

    def dfs(self, start: str, goal: str, max_depth: int = 10) -> Optional[List]:
        if start not in self.kb.graph:
            return None

        def _dfs(node, path, depth):
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
        if start not in self.kb.graph:
            return None
        open_set = [(0, start, [start])]
        g_scores = {start: 0}
        while open_set:
            f, node, path = heapq.heappop(open_set)
            if node == goal:
                return path
            for neighbor, weight in self.kb.get_neighbors(node).items():
                g = g_scores.get(node, float('inf')) + (1.0 - weight)
                if g < g_scores.get(neighbor, float('inf')):
                    g_scores[neighbor] = g
                    h = heuristic(neighbor, goal)
                    heapq.heappush(open_set, (g + h, neighbor, path + [neighbor]))
        return None

    def find_best_answer(self, entities: list, intent: str) -> Optional[str]:
        if not entities:
            return None
        candidates = []
        for entity in entities:
            neighbors = self.kb.get_neighbors(entity)
            for qa in self.kb.qa_pairs:
                score = 0.0
                qa_concepts = set(qa.get('concepts', []))
                if entity in qa_concepts:
                    score += 2.0
                for concept in qa_concepts:
                    if concept in neighbors:
                        score += neighbors[concept]
                if intent == qa.get('intent', ''):
                    score += 1.0
                if score > 0:
                    candidates.append((score, qa.get('answer', '')))
        if not candidates:
            return None
        candidates.sort(key=lambda x: x[0], reverse=True)
        return candidates[0][1]
