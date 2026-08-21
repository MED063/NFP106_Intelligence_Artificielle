"""Configuration commune aux tests.

Rend la suite deterministe quel que soit l'environnement du developpeur : si
USE_LLM=1 et une cle API sont definis dans le shell, le LLM reformulerait les
reponses du moteur maison et ferait echouer les assertions de texte. On
desactive donc la reformulation LLM pour tous les tests ; le coeur maison,
lui, est deterministe. Les tests specifiques du toggle LLM reactivent la
configuration eux-memes via monkeypatch.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import config


# ######## CODE IA (Claude - Anthropic) #########
@pytest.fixture(autouse=True)
def _disable_llm(monkeypatch):
    monkeypatch.setattr(config, 'USE_LLM', False)
# ###############################################
