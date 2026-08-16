import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from knowledge_base import KnowledgeBase


def test_add_concept():
    kb = KnowledgeBase()
    kb.add_concept("python")
    assert "python" in kb.graph


def test_add_relation():
    kb = KnowledgeBase()
    kb.add_relation("python", "programmation", 0.9)
    assert "programmation" in kb.graph["python"]
    assert kb.graph["python"]["programmation"] == 0.9


def test_get_neighbors():
    kb = KnowledgeBase()
    kb.add_relation("graphe", "bfs", 0.9)
    kb.add_relation("graphe", "dfs", 0.8)
    neighbors = kb.get_neighbors("graphe")
    assert "bfs" in neighbors
    assert "dfs" in neighbors


def test_get_neighbors_unknown():
    kb = KnowledgeBase()
    assert kb.get_neighbors("inconnu") == {}


def test_get_predecessors():
    kb = KnowledgeBase()
    kb.add_relation("obesite", "hypertension", 0.75)
    kb.add_relation("cholesterol", "hypertension", 0.6)
    kb.add_relation("hypertension", "avc", 0.8)
    predecessors = kb.get_predecessors("hypertension")
    assert predecessors == {"obesite": 0.75, "cholesterol": 0.6}


def test_get_predecessors_unknown():
    kb = KnowledgeBase()
    assert kb.get_predecessors("inconnu") == {}


def test_load_from_json(tmp_path):
    import json
    data = {
        "concepts": ["python", "java"],
        "relations": [{"src": "python", "dst": "java", "weight": 0.5}]
    }
    path = tmp_path / "graph.json"
    path.write_text(json.dumps(data), encoding='utf-8')
    kb = KnowledgeBase()
    kb.load_from_json(str(path))
    assert "python" in kb.graph
    assert "java" in kb.graph["python"]
