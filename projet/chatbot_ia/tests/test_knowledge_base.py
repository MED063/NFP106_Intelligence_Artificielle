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


def test_add_relation_with_type():
    kb = KnowledgeBase()
    kb.add_relation("obesite", "hypertension", 0.75, rel_type="cause_de")
    kb.add_relation("avc", "hypertension", 0.85, rel_type="associe_a")
    assert kb.get_relation_type("obesite", "hypertension") == "cause_de"
    assert kb.get_relation_type("avc", "hypertension") == "associe_a"
    # Une arete non typee retourne None (retro-compatibilite).
    kb.add_relation("cholesterol", "hypertension", 0.6)
    assert kb.get_relation_type("cholesterol", "hypertension") is None


def test_get_predecessors_filtered_by_type():
    kb = KnowledgeBase()
    kb.add_relation("obesite", "hypertension", 0.75, rel_type="cause_de")
    kb.add_relation("cholesterol", "hypertension", 0.6, rel_type="cause_de")
    # AVC est un facteur de risque mutuel (comorbidite), pas une cause : il
    # ne doit pas remonter comme predecesseur causal de l'hypertension.
    kb.add_relation("avc", "hypertension", 0.85, rel_type="associe_a")
    causal = kb.get_predecessors("hypertension", types={"cause_de"})
    assert causal == {"obesite": 0.75, "cholesterol": 0.6}
    # Sans filtre, toutes les relations entrantes sont retournees.
    assert set(kb.get_predecessors("hypertension")) == {"obesite", "cholesterol", "avc"}


def test_get_predecessors_untyped_edges_are_kept_when_filtering():
    # Retro-compatibilite : une arete sans type reste retenue meme quand un
    # filtre de types est applique (le typage est optionnel).
    kb = KnowledgeBase()
    kb.add_relation("obesite", "hypertension", 0.75)
    assert kb.get_predecessors("hypertension", types={"cause_de"}) == {"obesite": 0.75}


def test_save_preserves_relation_type(tmp_path):
    kb = KnowledgeBase()
    kb.add_relation("obesite", "hypertension", 0.75, rel_type="cause_de")
    path = tmp_path / "graph.json"
    kb.save_to_json(str(path))
    kb2 = KnowledgeBase()
    kb2.load_from_json(str(path))
    assert kb2.get_relation_type("obesite", "hypertension") == "cause_de"


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
