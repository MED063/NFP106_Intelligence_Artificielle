import json
from collections import defaultdict


class KnowledgeBase:
    def __init__(self):
        self.graph = {}
        self.qa_pairs = []

    def add_concept(self, concept: str) -> None:
        if concept not in self.graph:
            self.graph[concept] = {}

    def add_relation(self, src: str, dst: str, weight: float = 1.0) -> None:
        self.add_concept(src)
        self.add_concept(dst)
        self.graph[src][dst] = weight

    def get_neighbors(self, concept: str) -> dict:
        return self.graph.get(concept, {})

    def get_predecessors(self, concept: str) -> dict:
        """Retourne les concepts ayant une relation entrante vers
        `concept` (src -> concept), avec leur poids. Le graphe etant
        oriente (ex : 'obesite -> hypertension' pour modeliser un facteur
        de risque/une cause), get_neighbors seul ne donne que les effets
        d'un concept ; get_predecessors permet de remonter ses causes."""
        return {
            src: weights[concept]
            for src, weights in self.graph.items()
            if concept in weights
        }

    def load_from_json(self, filepath: str) -> None:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for concept in data.get('concepts', []):
            self.add_concept(concept)
        for rel in data.get('relations', []):
            self.add_relation(rel['src'], rel['dst'], rel.get('weight', 1.0))

    def load_qa_from_json(self, filepath: str) -> None:
        with open(filepath, 'r', encoding='utf-8') as f:
            self.qa_pairs = json.load(f)
        for pair in self.qa_pairs:
            for concept in pair.get('concepts', []):
                self.add_concept(concept)

    def save_to_json(self, filepath: str) -> None:
        data = {
            'concepts': list(self.graph.keys()),
            'relations': [
                {'src': src, 'dst': dst, 'weight': w}
                for src, neighbors in self.graph.items()
                for dst, w in neighbors.items()
            ]
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
