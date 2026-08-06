import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from nlp_engine import NLPEngine
from knowledge_base import KnowledgeBase


def test_tokenize():
    nlp = NLPEngine()
    tokens = nlp.tokenize("Bonjour, comment ça va ?")
    assert "bonjour" in tokens
    assert "comment" in tokens


def test_remove_stopwords():
    nlp = NLPEngine()
    tokens = ["le", "python", "est", "un", "langage"]
    filtered = nlp.remove_stopwords(tokens)
    assert "python" in filtered
    assert "le" not in filtered


def test_classify_intent_salutation():
    nlp = NLPEngine()
    tokens = ["bonjour"]
    assert nlp.classify_intent(tokens) == "SALUTATION"


def test_classify_intent_definition():
    nlp = NLPEngine()
    tokens = ["defin", "python"]
    assert nlp.classify_intent(tokens) == "DEFINITION"


def test_classify_intent_comparaison():
    nlp = NLPEngine()
    tokens = ["differenc", "diabete", "hypertension"]
    assert nlp.classify_intent(tokens) == "COMPARAISON"


def test_classify_intent_symptomes():
    nlp = NLPEngine()
    tokens = ["quels", "sympt", "grippe"]
    assert nlp.classify_intent(tokens) == "SYMPTOMES"


def test_classify_intent_prevention():
    nlp = NLPEngine()
    tokens = ["comment", "preven", "diabete"]
    assert nlp.classify_intent(tokens) == "PREVENTION"


def test_extract_entities():
    nlp = NLPEngine()
    kb = KnowledgeBase()
    kb.add_concept("python")
    kb.add_concept("graphe")
    entities = nlp.extract_entities(["python", "graphe", "blabla"], kb)
    assert "python" in entities
    assert "graphe" in entities
