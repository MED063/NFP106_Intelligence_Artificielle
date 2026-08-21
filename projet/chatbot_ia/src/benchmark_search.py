"""
Benchmark pour évaluer les performances des algorithmes de recherche
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from knowledge_base import KnowledgeBase
from search_engine import SearchEngine

PAIRS = [
    ("diabete", "insuline"),
    ("diabete", "avc"),
    ("obesite", "imc"),
    ("hypertension", "statines"),
    ("cholesterol", "infarctus"),
    ("grippe", "vaccin"),
    ("depression", "antidepresseurs"),
    ("asthme", "poumons"),
    ("regime_mediterraneen", "avc"),
    ("obesite", "hypertension"),
    ("diabete", "coeur"),
    ("osteoporose", "imc"),
]


# ######## CODE IA (Claude - Anthropic) #########
def main():
    data_dir = config.DATA_DIR
    kb = KnowledgeBase()
    kb.load_from_json(os.path.join(data_dir, 'knowledge_graph.json'))
    se = SearchEngine(kb)

    row = f"{'Requete':<32}{'Algo':<6}{'Longueur':<10}{'Noeuds':<8}{'Temps (ms)':<10}"
    print(row)
    print("-" * len(row))
    for start, goal in PAIRS:
        results = se.compare_algorithms(start, goal)
        for algo, r in results.items():
            length = len(r['path']) if r['path'] else 0
            print(
                f"{start + ' -> ' + goal:<32}{algo:<6}{length:<10}"
                f"{r['nodes_explored']:<8}{r['time'] * 1000:<10.3f}"
            )


# ###############################################
if __name__ == '__main__':
    main()
