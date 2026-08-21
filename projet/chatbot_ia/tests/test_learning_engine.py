"""
tests Unitaires pour la classe LearningEngine ."""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from learning_engine import LearningEngine
from knowledge_base import KnowledgeBase


def test_feedback_score_neutral_without_feedback():
    le = LearningEngine(tokenizer=lambda t: t.lower().split())
    assert le.feedback_score('une question', 'une reponse') == 0.0


def test_feedback_score_reinforces_and_penalizes():
    le = LearningEngine(tokenizer=lambda t: t.lower().split())
    q = 'quelles sont les causes de l obesite'
    le.record_feedback(q, 'bonne reponse', 5)   # renforce
    le.record_feedback(q, 'mauvaise reponse', 1)  # penalise
    assert le.feedback_score(q, 'bonne reponse') > 0
    assert le.feedback_score(q, 'mauvaise reponse') < 0
    # Une question sans rapport ne recoit aucun ajustement.
    assert le.feedback_score('sujet totalement different ici', 'bonne reponse') == 0.0


def make_engine():
    le = LearningEngine()
    docs = [
        ['python', 'langage', 'programmation'],
        ['algorithme', 'complexite', 'tri'],
        ['graphe', 'bfs', 'parcours'],
        ['python', 'objet', 'classe'],
    ]
    le.build_tfidf(docs)
    return le


def test_build_tfidf_populates_idf():
    le = make_engine()
    assert len(le.idf) > 0


def test_build_tfidf_populates_matrix():
    le = make_engine()
    assert le.tfidf_matrix is not None
    assert len(le.tfidf_matrix) == 4


def test_cosine_similarity_identical():
    le = LearningEngine()
    vec = {'python': 0.5, 'graphe': 0.3}
    assert abs(le.cosine_similarity(vec, vec) - 1.0) < 0.001


def test_cosine_similarity_orthogonal():
    le = LearningEngine()
    vec1 = {'python': 1.0}
    vec2 = {'graphe': 1.0}
    assert le.cosine_similarity(vec1, vec2) == 0.0


def test_cosine_similarity_zero_vector():
    le = LearningEngine()
    assert le.cosine_similarity({}, {'python': 1.0}) == 0.0


def test_rank_answers_returns_list():
    le = make_engine()
    ranked = le.rank_answers(['python', 'langage'], ['Python est un langage.', 'BFS est un algo.'])
    assert isinstance(ranked, list)
    assert len(ranked) == 2


def test_rank_answers_prefers_relevant():
    le = make_engine()
    candidates = ['Python est un langage de programmation.', 'BFS parcourt un graphe.']
    ranked = le.rank_answers(['python', 'langage'], candidates)
    assert ranked[0] == candidates[0]


def test_rank_answers_uses_injected_tokenizer():
    le = LearningEngine(tokenizer=lambda text: [t.strip('().,;?!') for t in text.lower().split()])
    le.build_tfidf([['imc'], ['obesite']])
    candidates = ['Indice de masse corporelle (IMC).', "L'obesite est frequente."]
    ranked = le.rank_answers(['imc'], candidates)
    assert ranked[0] == candidates[0]


def test_train_naive_bayes_populates_classes():
    le = LearningEngine()
    X = [['python', 'langage'], ['bfs', 'graphe'], ['python', 'objet']]
    y = ['DEFINITION', 'EXPLICATION', 'DEFINITION']
    le.train_naive_bayes(X, y)
    assert 'DEFINITION' in le._nb_classes
    assert 'EXPLICATION' in le._nb_classes


def test_predict_intent_without_training():
    le = LearningEngine()
    assert le.predict_intent(['python']) == 'QUESTION'


def test_predict_intent_after_training():
    le = LearningEngine()
    X = [['python', 'langage', 'def'], ['bfs', 'graphe', 'parcours'], ['python', 'objet', 'def']]
    y = ['DEFINITION', 'EXPLICATION', 'DEFINITION']
    le.train_naive_bayes(X, y)
    intent = le.predict_intent(['def', 'python'])
    assert intent in ('DEFINITION', 'EXPLICATION')


def test_record_feedback():
    le = LearningEngine()
    le.record_feedback('Qu est ce que Python ?', 'Python est un langage.', 5)
    assert len(le.feedback_log) == 1
    assert le.feedback_log[0]['score'] == 5


def test_save_and_load_feedback(tmp_path):
    le = LearningEngine()
    le.record_feedback('question', 'reponse', 4)
    path = str(tmp_path / 'feedback.json')
    le.save_feedback(path)
    le2 = LearningEngine()
    le2.load_feedback(path)
    assert len(le2.feedback_log) == 1
    assert le2.feedback_log[0]['question'] == 'question'


def test_load_feedback_missing_file(tmp_path):
    le = LearningEngine()
    le.load_feedback(str(tmp_path / 'nonexistent.json'))
    assert le.feedback_log == []


def test_retrain_rebuilds_tfidf():
    le = LearningEngine()
    le.record_feedback('python ?', 'Python est un langage de programmation.', 5)
    le.record_feedback('bfs ?', 'BFS parcourt le graphe en largeur.', 5)
    le.retrain()
    assert len(le.idf) > 0


def test_retrain_updates_graph_weights():
    le = LearningEngine()
    kb = KnowledgeBase()
    kb.add_relation('python', 'programmation', 0.5)
    le.record_feedback('python ?', 'python programmation langage.', 5)
    le.retrain(kb)
    assert kb.graph['python']['programmation'] > 0.5


def test_retrain_penalizes_bad_feedback():
    le = LearningEngine()
    kb = KnowledgeBase()
    kb.add_relation('python', 'programmation', 0.5)
    le.record_feedback('python ?', 'python programmation langage.', 1)
    le.retrain(kb)
    assert kb.graph['python']['programmation'] < 0.5
