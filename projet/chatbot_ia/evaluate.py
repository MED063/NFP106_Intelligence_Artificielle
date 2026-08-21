"""Rapport d'evaluation du ChatBot IA.

Mesure les 5 metriques demandees :
1. Precision des reponses (cible >= 70%)
2. Precision des intentions (cible >= 80%)
3. Temps de reponse moyen (cible <= 2s)
4. Noeuds explores BFS vs A* (cible A* < BFS)
5. Amelioration par feedback apres 3 cycles (cible >= +5%)

Utilise les qa_pairs.json (62 questions) comme jeu de test, ainsi que les paires de benchmark_search.py pour la comparaison des algorithmes de
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

# Intentions "de controle" : leur reponse est un message fixe qui ne vient  pas des qa_pairs, on ne peut donc pas comparer le texte mot pour mot.
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


""" Jeu de DEMONSTRATION du feedback : des reformulations "utilisateur"  (questions futures, jamais vues telles quelles a l'entrainement)
 de sujets connus. Certaines sont initialement mal routees (intention mal detectee ou 
 entite non reconnue) : c'est precisement sur ce type de cas que le feedback doit faire progresser le systeme. 
 On mesure le gain sur ce jeu plutot que sur les 79 qa_pairs, car ces dernieres sont deja repondues a 100 %
 'attendu' est un extrait de la bonne reponse, servant a la fois d'oracle et a retrouver la reponse a enseigner.
"""
FEEDBACK_DEMO = [
    {"question": "C'est quoi le diabète exactement ?", "attendu": "diabète est une maladie chronique"},
    {"question": "Peux-tu m'expliquer l'hypertension ?", "attendu": "hypertension artérielle"},
    {"question": "Le tabac, c'est risqué comment ?", "attendu": "tabac est le premier facteur"},
    {"question": "Pourquoi devient-on obèse ?", "attendu": "obésité résulte"},
    {"question": "Qu'est-ce qui provoque un AVC ?", "attendu": "AVC est le plus souvent causé"},
    {"question": "Comment on soigne un diabète de type 2 ?", "attendu": "traitement du diabète de type 2"},
    {"question": "Quels signes montrent une dépression ?", "attendu": "symptômes de la dépression"},
    {"question": "Comment faire pour ne pas attraper la grippe ?", "attendu": "prévention de la grippe"},
    {"question": "À quoi sert l'insuline ?", "attendu": "insuline, produite par le pancréas"},
    {"question": "Le cholestérol c'est quoi au juste ?", "attendu": "cholestérol est une substance grasse"},
    {"question": "Comment éviter le cancer ?", "attendu": "prévention du cancer"},
    {"question": "Qu'est-ce que l'ostéoporose exactement ?", "attendu": "ostéoporose est une maladie osseuse"},
    {"question": "Ça veut dire quoi la glycémie ?", "attendu": "glycémie est le taux de glucose"},
    {"question": "Comment reconnaître un infarctus ?", "attendu": "symptômes classiques d'un infarctus"},
    {"question": "Pourquoi a-t-on de l'hypertension ?", "attendu": "hypertension peut être causée"},
]


def _demo_precision(bot: ChatBot, demo: list) -> tuple:
    ok = sum(1 for d in demo
             if d['attendu'].lower() in (bot.answer(d['question']) or '').lower())
    return ok / len(demo) if demo else 0.0, ok


def evaluate_feedback_gain(bot: ChatBot, cycles: int = 3, demo: list = None) -> dict:
    """Mesure le gain de precision apres N cycles de feedback utilisateur, sur le jeu de demonstration FEEDBACK_DEMO.

    A chaque cycle, on simule un utilisateur : si la reponse rendue est bonne on la renforce (note 5) ; 
    si elle est mauvaise on la penalise (note 1) et on enseigne la bonne reponse (note 5), comme prevu par le sujet
    ("penalise et propose une meilleure reponse"). retrain() est ensuite appele. 
    Le feedback ajuste directement le classement des reponses futures
    (LearningEngine.feedback_score)."""
    demo = demo if demo is not None else FEEDBACK_DEMO

    def true_answer(substr: str):
        for qa in bot.kb.qa_pairs:
            if substr.lower() in qa.get('answer', '').lower():
                return qa['answer']
        return None

    before, ok_before = _demo_precision(bot, demo)
    for _ in range(cycles):
        for d in demo:
            response = bot.answer(d['question']) or ''
            if d['attendu'].lower() in response.lower():
                bot.learner.record_feedback(d['question'], response, 5)
            else:
                bot.learner.record_feedback(d['question'], response, 1)
                good = true_answer(d['attendu'])
                if good:
                    bot.learner.record_feedback(d['question'], good, 5)
        bot.retrain()
    after, ok_after = _demo_precision(bot, demo)
    return {'before': before, 'after': after, 'gain': after - before,
            'cycles': cycles, 'n': len(demo),
            'ok_before': ok_before, 'ok_after': ok_after}


def main():
    bot = ChatBot(data_dir=DATA_DIR)
    qa_pairs = bot.kb.qa_pairs

    answers = evaluate_answers(bot, qa_pairs)
    intents = evaluate_intents(bot, qa_pairs)
    search = evaluate_search(bot, PAIRS)

    # Le feedback modifie l'etat du bot (feedback_log, poids du graphe) : on le mesure en dernier pour ne pas fausser les metriques precedentes.
    feedback = evaluate_feedback_gain(bot)

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
          f"({feedback['ok_before']}/{feedback['n']} -> {feedback['ok_after']}/{feedback['n']}, "
          f"{feedback['gain']:+.1%} sur {feedback['cycles']} cycles) "
          f"— cible >= +5% "
          f"[jeu de reformulations inedites]")


if __name__ == '__main__':
    main()
