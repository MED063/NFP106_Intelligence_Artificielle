import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

flask = pytest.importorskip("flask")  # l'interface web est optionnelle

import web_app


@pytest.fixture
def client(tmp_path, monkeypatch):
    # Rediriger le log de feedback vers un fichier temporaire pour ne pas
    # polluer data/feedback_log.json pendant les tests.
    monkeypatch.setattr(web_app, 'FEEDBACK_LOG', str(tmp_path / 'fb.json'))
    monkeypatch.setattr(web_app, '_feedback_count', 0)
    web_app.app.config['TESTING'] = True
    with web_app.app.test_client() as c:
        yield c


def test_index_page_loads(client):
    resp = client.get('/')
    assert resp.status_code == 200
    assert b'ChatBot IA' in resp.data


def test_ask_returns_answer(client):
    resp = client.post('/ask', json={'question': "Qu'est-ce que le diabète ?"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'diab' in data['answer'].lower()


def test_ask_rejects_empty_question(client):
    resp = client.post('/ask', json={'question': '   '})
    assert resp.status_code == 400


def test_feedback_accepts_valid_score(client):
    resp = client.post('/feedback', json={
        'question': 'Q', 'answer': 'A', 'score': 5})
    assert resp.status_code == 200
    assert resp.get_json()['ok'] is True


def test_feedback_rejects_out_of_range_score(client):
    resp = client.post('/feedback', json={
        'question': 'Q', 'answer': 'A', 'score': 9})
    assert resp.status_code == 400
