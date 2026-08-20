"""Interface web Flask pour le ChatBot IA (domaine sante).

Expose la meme logique que l'interface CLI (`ui.py`) via une petite
application web : une page de discussion, un point d'entree `/ask` qui
renvoie la reponse du bot en JSON, et `/feedback` pour enregistrer la
note de l'utilisateur (1-5), avec re-entrainement automatique tous les
`FEEDBACK_RETRAIN_EVERY` retours — exactement comme la boucle CLI.

Deux points d'entree `/llm/status` et `/llm/toggle` permettent de consulter
et de basculer depuis l'interface la reformulation optionnelle par un LLM
(voir llm_engine.py).

Lancement :
    pip install -r requirements.txt
    python web_app.py
puis ouvrir http://127.0.0.1:5000

Le bot est instancie une seule fois au demarrage (chargement du graphe,
entrainement TF-IDF + Naive Bayes) et partage entre les requetes.
"""
import os

from flask import Flask, jsonify, render_template, request

import config
from main import ChatBot

DATA_DIR = config.DATA_DIR
FEEDBACK_LOG = config.FEEDBACK_LOG
FEEDBACK_RETRAIN_EVERY = config.FEEDBACK_RETRAIN_EVERY


app = Flask(__name__)
bot = ChatBot(data_dir=DATA_DIR)
_feedback_count = 0


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/llm/status')
def llm_status():
    """Etat de la reformulation LLM optionnelle, pour l'interface."""
    return jsonify({
        'enabled': bool(config.USE_LLM),
        'key_present': bool(config.LLM_API_KEY),
        'available': bot.llm.is_available(),
        'model': config.LLM_MODEL,
    })


@app.route('/llm/toggle', methods=['POST'])
def llm_toggle():
    """Active/desactive la reformulation LLM depuis l'interface. N'a d'effet
    que si une cle d'API est configuree (sinon 'available' reste faux)."""
    data = request.get_json(silent=True) or {}
    config.USE_LLM = bool(data.get('enabled'))
    return jsonify({
        'enabled': bool(config.USE_LLM),
        'key_present': bool(config.LLM_API_KEY),
        'available': bot.llm.is_available(),
        'model': config.LLM_MODEL,
    })


def _subgraph(entities: list, max_per_entity: int = 8) -> dict:
    """Construit le sous-graphe autour des entites detectees : chaque entite
    (noeud central) avec ses relations sortantes (get_neighbors) et entrantes
    (get_predecessors), typees et ponderees. Sert a visualiser dans
    l'interface le pilier "recherche sur graphe"."""
    nodes, edges, seen = {}, [], set()

    def add_node(cid, center=False):
        node = nodes.setdefault(cid, {'id': cid, 'center': False})
        if center:
            node['center'] = True

    for entity in entities:
        add_node(entity, center=True)
        outgoing = list(bot.kb.get_neighbors(entity).items())[:max_per_entity]
        for dst, weight in outgoing:
            add_node(dst)
            key = (entity, dst)
            if key not in seen:
                seen.add(key)
                edges.append({'src': entity, 'dst': dst, 'weight': round(weight, 2),
                              'type': bot.kb.get_relation_type(entity, dst)})
        incoming = list(bot.kb.get_predecessors(entity).items())[:max_per_entity]
        for src, weight in incoming:
            add_node(src)
            key = (src, entity)
            if key not in seen:
                seen.add(key)
                edges.append({'src': src, 'dst': entity, 'weight': round(weight, 2),
                              'type': bot.kb.get_relation_type(src, entity)})
    return {'nodes': list(nodes.values()), 'edges': edges}


@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json(silent=True) or {}
    question = (data.get('question') or '').strip()
    if not question:
        return jsonify({'error': 'question vide'}), 400
    # On expose aussi l'intention detectee et les entites extraites (pilier
    # "reconnaissance") ainsi que le sous-graphe explore (pilier "recherche"),
    # pour les rendre visibles dans l'interface.
    tokens = bot.nlp.preprocess(question)
    nb_fallback = bot.learner.predict_intent if bot._nb_ready else None
    intent = bot.nlp.classify_intent(tokens, nb_fallback=nb_fallback)
    entities = bot.nlp.extract_entities(tokens, bot.kb)
    answer = bot.answer(question)
    return jsonify({
        'answer': answer,
        'intent': intent,
        'entities': entities,
        'graph': _subgraph(entities),
    })


@app.route('/feedback', methods=['POST'])
def feedback():
    global _feedback_count
    data = request.get_json(silent=True) or {}
    question = (data.get('question') or '').strip()
    answer = (data.get('answer') or '').strip()
    try:
        score = int(data.get('score'))
    except (TypeError, ValueError):
        return jsonify({'error': 'note invalide'}), 400
    if not 1 <= score <= 5:
        return jsonify({'error': 'note hors bornes (1-5)'}), 400

    bot.learner.record_feedback(question, answer, score)
    _feedback_count += 1
    retrained = False
    if _feedback_count % FEEDBACK_RETRAIN_EVERY == 0:
        bot.retrain()
        retrained = True
    bot.learner.save_feedback(FEEDBACK_LOG)
    return jsonify({'ok': True, 'retrained': retrained})


if __name__ == '__main__':
    app.run(debug=False, host='127.0.0.1', port=5000)
