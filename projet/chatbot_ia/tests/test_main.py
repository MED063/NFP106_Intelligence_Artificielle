import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from main import ChatBot

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data') + os.sep


@pytest.fixture
def bot():
    return ChatBot(data_dir=DATA_DIR)


def test_chatbot_loads_data(bot):
    assert len(bot.kb.graph) >= 30
    assert len(bot.kb.qa_pairs) >= 50


def test_chatbot_salutation(bot):
    assert 'Bonjour' in bot.answer('Bonjour')


def test_chatbot_quitter(bot):
    assert 'revoir' in bot.answer('Au revoir').lower()


def test_chatbot_answers_known_question(bot):
    response = bot.answer("Qu'est-ce que le diabète ?")
    assert 'diabète' in response.lower() or 'diabete' in response.lower()


def test_chatbot_unknown_question_returns_fallback(bot):
    response = bot.answer('Blablabla xyzzy inconnu')
    assert response == "Je n'ai pas trouvé de réponse à votre question."


def test_chatbot_naive_bayes_is_trained(bot):
    # V2 de classify_intent : Naive Bayes entraine sur les intentions
    # etiquetees des qa_pairs (cf. sujet section 4.2).
    assert bot._nb_ready is True
    assert bot.learner._nb_classes
