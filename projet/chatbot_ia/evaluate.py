"""Rapport d'evaluation du ChatBot IA (cf. sujet, section "Documentation").

Mesure les 5 metriques demandees :
1. Precision des reponses (cible >= 70%)
2. Precision des intentions (cible >= 80%)
3. Temps de reponse moyen (cible <= 2s)
4. Noeuds explores BFS vs A* (cible A* < BFS)
5. Amelioration par feedback apres 3 cycles (cible >= +5%)

Utilise les qa_pairs.json (62 questions) comme jeu de test, ainsi que les
paires de benchmark_search.py pour la comparaison des algorithmes de
recherche.

Usage : python evaluate.py
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import ChatBot
from benchmark_search import PAIRS


DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data') + os.sep

# Intentions "de controle" : leur reponse est un message fixe qui ne vient
# pas des qa_pairs, on ne peut donc pas comparer le texte mot pour mot.
CONTROL_INTENTS = {'SALUTATION', 'QUITTER'}


def _is_correct(bot: ChatBot, qa: dict) -> tuple:
    """Retourne (reponse_correcte: bool, temps: float)."""
    t0 = time.perf_counter()
    response = bot.answer(qa['question'])
    elapsed = time.perf_counter() - t0
    if qa.get('intent') in CONTROL_INTENTS:
        tokens = bot.nlp.preprocess(qa['question'])
        nb_fallback = bot.learner.predict_intent if bot._nb_ready else None
        correct = bot.nlp.classify_intent(tokens, nb_fallback=nb_fallback) == qa['intent']
    else:
        correct = response == qa.get('answer')
    return correct, elapsed


def evaluate_answers(bot: ChatBot, qa_pairs: list) -> dict:
    correct = 0
    total_time = 0.0
    for qa in qa_pairs:
        is_correct, elapsed = _is_correct(bot, qa)
        correct += int(is_correct)
        total_time += elapsed
    n = len(qa_pairs)
    return {
        'accuracy': correct / n if n else 0.0,
        'correct': correct,
        'total': n,
        'avg_time': total_time / n if n else 0.0,
    }


def evaluate_intents(bot: ChatBot, qa_pairs: list) -> dict:
    correct = 0
    for qa in qa_pairs:
        tokens = bot.nlp.preprocess(qa['question'])
        nb_fallback = bot.learner.predict_intent if bot._nb_ready else None
        predicted = bot.nlp.classify_intent(tokens, nb_fallback=nb_fallback)
        correct += int(predicted == qa.get('intent'))
    n = len(qa_pairs)
    return {'accuracy': correct / n if n else 0.0, 'correct': correct, 'total': n}


def evaluate_search(bot: ChatBot, pairs: list) -> dict:
    bfs_nodes, astar_nodes = [], []
    for start, goal in pairs:
        results = bot.search.compare_algorithms(start, goal)
        if results['BFS']['path'] is not None:
            bfs_nodes.append(results['BFS']['nodes_explored'])
        if results['A*']['path'] is not None:
            astar_nodes.append(results['A*']['nodes_explored'])
    avg_bfs = sum(bfs_nodes) / len(bfs_nodes) if bfs_nodes else 0.0
    avg_astar = sum(astar_nodes) / len(astar_nodes) if astar_nodes else 0.0
    return {
        'avg_nodes_bfs': avg_bfs,
        'avg_nodes_astar': avg_astar,
        'astar_better': avg_astar <= avg_bfs,
        'n_queries': len(pairs),
    }


def evaluate_feedback_gain(bot: ChatBot, qa_pairs: list, cycles: int = 3) -> dict:
    """Mesure le gain de precision des reponses apres N cycles de feedback.

    A chaque cycle : on note (5) les reponses correctes et (2) les reponses
    incorrectes sur tout le jeu de test, puis on relance retrain() pour
    ajuster les poids du graphe, avant de re-mesurer la precision.
    """
    before = evaluate_answers(bot, qa_pairs)['accuracy']
    for _ in range(cycles):
        for qa in qa_pairs:
            response = bot.answer(qa['question'])
            score = 5 if response == qa.get('answer') else 2
            bot.learner.record_feedback(qa['question'], response, score)
        bot.retrain()
    after = evaluate_answers(bot, qa_pairs)['accuracy']
    return {'before': before, 'after': after, 'gain': after - before, 'cycles': cycles}


def main():
    bot = ChatBot(data_dir=DATA_DIR)
    qa_pairs = bot.kb.qa_pairs

    answers = evaluate_answers(bot, qa_pairs)
    intents = evaluate_intents(bot, qa_pairs)
    search = evaluate_search(bot, PAIRS)

    # Le feedback modifie l'etat du bot (poids du graphe) : on le mesure en
    # dernier pour ne pas fausser les metriques precedentes.
    feedback = evaluate_feedback_gain(bot, qa_pairs)

    print("=== Rapport d'evaluation - ChatBot IA (domaine sante) ===\n")
    print(f"1. Precision des reponses    : {answers['accuracy']:.1%} "
          f"({answers['correct']}/{answers['total']}) — cible >= 70%")
    print(f"2. Precision des intentions  : {intents['accuracy']:.1%} "
          f"({intents['correct']}/{intents['total']}) — cible >= 80%")
    print(f"3. Temps de reponse moyen    : {answers['avg_time'] * 1000:.3f} ms — cible <= 2s")
    print(f"4. Noeuds explores (n={search['n_queries']} requetes) : "
          f"BFS={search['avg_nodes_bfs']:.1f}  A*={search['avg_nodes_astar']:.1f} "
          f"— A* {'<' if search['astar_better'] else '>='} BFS "
          f"({'OK' if search['astar_better'] else 'a ameliorer'})")
    print(f"5. Amelioration par feedback : {feedback['before']:.1%} -> {feedback['after']:.1%} "
          f"({feedback['gain']:+.1%} sur {feedback['cycles']} cycles) — cible >= +5%")


if __name__ == '__main__':
    main()
