"""
tests Unitaires pour la classe ChatBot .
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from main import ChatBot

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data') + os.sep


# ######## CODE IA (Claude - Anthropic) #########
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


def test_chatbot_answers_glycemie_question(bot):
    response = bot.answer("c'est quoi la glycémie ?")
    assert 'glyc' in response.lower()


def test_chatbot_answers_tabac_and_alcool_questions(bot):
    assert 'tabac' in bot.answer('Quels sont les risques du tabac pour la santé ?').lower()
    assert 'alcool' in bot.answer("Quels sont les effets de l'alcool sur la santé ?").lower()


def test_chatbot_answers_enriched_topics(bot):
    # Concepts ajoutes lors de l'enrichissement de la base sante.
    assert 'stress' in bot.answer("Qu'est-ce que le stress ?").lower()
    assert 'sédentar' in bot.answer("Qu'est-ce que la sédentarité ?").lower()
    assert 'ménopause' in bot.answer("Qu'est-ce que la ménopause ?").lower()
    assert 'antibiot' in bot.answer("Qu'est-ce que les antibiotiques ?").lower()


def test_chatbot_causes_obesite_not_confused_with_diabete(bot):
    response = bot.answer("Quelles sont les causes de l'obésité ?")
    assert 'obésité résulte' in response.lower() or "l'obésité" in response.lower()
    assert 'diabète de type 2 est principalement' not in response.lower()


def test_feedback_improves_future_answer(bot):
    question = "Qu'est-ce qui provoque un AVC ?"
    before = bot.answer(question)
    good = next(qa['answer'] for qa in bot.kb.qa_pairs
                if qa['question'] == "Quelles sont les causes de l'AVC ?")
    assert before != good  
    bot.learner.record_feedback(question, before, 1)
    bot.learner.record_feedback(question, good, 5)
    assert bot.answer(question) == good


def test_chatbot_naive_bayes_is_trained(bot):
    assert bot._nb_ready is True
    assert bot.learner._nb_classes
# ###############################################
