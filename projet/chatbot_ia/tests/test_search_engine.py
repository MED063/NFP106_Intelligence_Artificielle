import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from knowledge_base import KnowledgeBase
from search_engine import SearchEngine


def make_kb():
    kb = KnowledgeBase()
    kb.add_relation("a", "b", 0.9)
    kb.add_relation("b", "c", 0.8)
    kb.add_relation("a", "c", 0.5)
    return kb


def test_bfs_direct():
    kb = make_kb()
    se = SearchEngine(kb)
    path = se.bfs("a", "b")
    assert path is not None
    assert path[0] == "a" and path[-1] == "b"


def test_bfs_indirect():
    kb = make_kb()
    se = SearchEngine(kb)
    path = se.bfs("a", "c")
    assert path is not None
    assert "c" in path


def test_bfs_not_found():
    kb = make_kb()
    se = SearchEngine(kb)
    path = se.bfs("a", "z")
    assert path is None


def test_dfs():
    kb = make_kb()
    se = SearchEngine(kb)
    path = se.dfs("a", "c")
    assert path is not None
    assert path[-1] == "c"


def test_a_star():
    kb = make_kb()
    se = SearchEngine(kb)
    path = se.a_star("a", "c", heuristic=lambda n, g: 0)
    assert path is not None
    assert path[-1] == "c"


def test_heuristic_bigram_identical_words_is_zero():
    se = SearchEngine(make_kb())
    assert se.heuristic_bigram("python", "python") == 0.0


def test_heuristic_bigram_is_admissible():
    se = SearchEngine(make_kb())
    h = se.heuristic_bigram("algorithme", "arbre")
    assert 0.0 <= h <= 1.0


def test_a_star_with_heuristic_bigram_finds_path():
    kb = make_kb()
    se = SearchEngine(kb)
    path = se.a_star("a", "c", heuristic=se.heuristic_bigram)
    assert path is not None
    assert path[-1] == "c"


def test_compare_algorithms_returns_all_three():
    kb = make_kb()
    se = SearchEngine(kb)
    results = se.compare_algorithms("a", "c")
    assert set(results) == {"BFS", "DFS", "A*"}
    for entry in results.values():
        assert entry["path"] is not None
        assert entry["nodes_explored"] >= 1
        assert entry["time"] >= 0.0


def test_compare_algorithms_no_path():
    kb = make_kb()
    se = SearchEngine(kb)
    results = se.compare_algorithms("a", "z")
    for entry in results.values():
        assert entry["path"] is None


def make_qa_kb():
    kb = KnowledgeBase()
    kb.add_relation("diabete", "insuline", 0.8)
    kb.qa_pairs = [
        {"question": "Qu'est-ce que le diabete ?", "answer": "Definition diabete.",
         "concepts": ["diabete"], "intent": "DEFINITION"},
        {"question": "Comment traiter le diabete ?", "answer": "Traitement diabete.",
         "concepts": ["diabete", "insuline"], "intent": "TRAITEMENT"},
    ]
    return kb


def test_find_best_answer_no_entities_returns_empty():
    se = SearchEngine(make_qa_kb())
    assert se.find_best_answer([], "DEFINITION") == []


def test_find_best_answer_returns_scored_candidates_sorted():
    se = SearchEngine(make_qa_kb())
    candidates = se.find_best_answer(["diabete"], "DEFINITION")
    assert candidates
    scores = [score for score, _ in candidates]
    assert scores == sorted(scores, reverse=True)


def test_find_best_answer_intent_match_ranks_first():
    se = SearchEngine(make_qa_kb())
    candidates = se.find_best_answer(["diabete"], "TRAITEMENT")
    assert candidates[0][1] == "Traitement diabete."
