"""
tests Unitaires pour la classe LLMEngine ."""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import config
from llm_engine import LLMEngine


def test_disabled_by_default(monkeypatch):
    # Par defaut le LLM est desactive : aucune tentative d'appel.
    monkeypatch.setattr(config, 'USE_LLM', False)
    monkeypatch.setattr(config, 'LLM_API_KEY', 'peu-importe')
    llm = LLMEngine()
    assert llm.is_available() is False
    assert llm.reformulate('Q', 'Reponse de reference.') is None
    assert llm.answer_fallback('Q') is None


def test_unavailable_without_key(monkeypatch):
    monkeypatch.setattr(config, 'USE_LLM', True)
    monkeypatch.setattr(config, 'LLM_API_KEY', '')
    assert LLMEngine().is_available() is False


def test_reformulate_uses_chat(monkeypatch):
    monkeypatch.setattr(config, 'USE_LLM', True)
    monkeypatch.setattr(config, 'LLM_API_KEY', 'cle-test')
    llm = LLMEngine()
    captured = {}

    def fake_chat(messages):
        captured['messages'] = messages
        return 'Reponse reformulee.'

    monkeypatch.setattr(llm, '_chat', fake_chat)
    out = llm.reformulate("Qu'est-ce que le diabete ?", 'Le diabete est une maladie.')
    assert out == 'Reponse reformulee.'
    # Le contexte (reponse de reference) doit etre transmis au modele.
    assert any('Le diabete est une maladie.' in m['content'] for m in captured['messages'])


def test_reformulate_returns_none_on_api_error(monkeypatch):
    monkeypatch.setattr(config, 'USE_LLM', True)
    monkeypatch.setattr(config, 'LLM_API_KEY', 'cle-test')
    llm = LLMEngine()
    monkeypatch.setattr(llm, '_chat', lambda messages: None)  # simule un echec reseau
    assert llm.reformulate('Q', 'Reponse.') is None


def test_chatbot_answer_unchanged_when_llm_disabled(monkeypatch):
    # Avec le LLM desactive (defaut), la reponse reste la reponse maison exacte.
    monkeypatch.setattr(config, 'USE_LLM', False)
    from main import ChatBot
    bot = ChatBot()
    expected = next(qa['answer'] for qa in bot.kb.qa_pairs
                    if qa['question'] == "Qu'est-ce que le diabète ?")
    assert bot.answer("Qu'est-ce que le diabète ?") == expected


def test_chatbot_reformulates_when_llm_enabled(monkeypatch):
    monkeypatch.setattr(config, 'USE_LLM', True)
    monkeypatch.setattr(config, 'LLM_API_KEY', 'cle-test')
    from main import ChatBot
    bot = ChatBot()
    monkeypatch.setattr(bot.llm, '_chat', lambda messages: 'REFORMULATION LLM')
    assert bot.answer("Qu'est-ce que le diabète ?") == 'REFORMULATION LLM'
