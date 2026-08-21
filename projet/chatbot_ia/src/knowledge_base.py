"""
ce fichier contient la classe KnowledgeBase, qui represente le graphe de connaissances et les paires question/reponse.
Il fournit des methodes pour ajouter des concepts, des relations, charger/sauver depuis/vers JSON, et recuperer les voisins et predecesseurs d'un concept.
"""

import json
from collections import defaultdict


class KnowledgeBase:
    def __init__(self):
        self.graph = {}
        """
         Type semantique de chaque arete, indexe par (src, dst). ce qui est  optionnel :  une relation sans type reste un simple lien pondere (retro-compatible).
         Les types permettent de distinguer une causalite ('cause_de') d'une  simple association/comorbidite ('associe_a'), d'un traitement
         ('traite_par'), d'un symptome ('symptome'), d'une atteinte d'organe ('affecte') ou d'une mesure preventive ('previent')."""
        self.relation_types = {}
        self.qa_pairs = []

    def add_concept(self, concept: str) -> None:
        if concept not in self.graph:
            self.graph[concept] = {}

    def add_relation(self, src: str, dst: str, weight: float = 1.0,
                     rel_type: str = None) -> None:
        self.add_concept(src)
        self.add_concept(dst)
        self.graph[src][dst] = weight
        if rel_type:
            self.relation_types[(src, dst)] = rel_type

    def get_neighbors(self, concept: str) -> dict:
        return self.graph.get(concept, {})

    def get_relation_type(self, src: str, dst: str) -> str:
        """Type semantique de l'arete src -> dst (None si non type)."""
        return self.relation_types.get((src, dst))

    def get_predecessors(self, concept: str, types=None) -> dict:
        """Retourne les concepts ayant une relation entrante vers `concept` (src -> concept), avec leur poids. 
        """
        result = {}
        for src, weights in self.graph.items():
            if concept not in weights:
                continue
            if types is not None:
                rel_type = self.relation_types.get((src, concept))
                if rel_type is not None and rel_type not in types:
                    continue
            result[src] = weights[concept]
        return result

    def load_from_json(self, filepath: str) -> None:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for concept in data.get('concepts', []):
            self.add_concept(concept)
        for rel in data.get('relations', []):
            self.add_relation(rel['src'], rel['dst'], rel.get('weight', 1.0),
                              rel.get('type'))

    def load_qa_from_json(self, filepath: str) -> None:
        with open(filepath, 'r', encoding='utf-8') as f:
            self.qa_pairs = json.load(f)
        for pair in self.qa_pairs:
            for concept in pair.get('concepts', []):
                self.add_concept(concept)

    def save_to_json(self, filepath: str) -> None:
        relations = []
        for src, neighbors in self.graph.items():
            for dst, w in neighbors.items():
                rel = {'src': src, 'dst': dst, 'weight': w}
                rel_type = self.relation_types.get((src, dst))
                if rel_type:
                    rel['type'] = rel_type
                relations.append(rel)
        data = {'concepts': list(self.graph.keys()), 'relations': relations}
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
