"""Interface web Flask pour le ChatBot IA (domaine sante).

Expose la meme logique que l'interface CLI (`ui.py`) via une petite
application web : une page de discussion, un point d'entree `/ask` qui
renvoie la reponse du bot en JSON, et `/feedback` pour enregistrer la
note de l'utilisateur (1-5), avec re-entrainement automatique tous les
`FEEDBACK_RETRAIN_EVERY` retours — exactement comme la boucle CLI.

Lancement :
    pip install -r requirements.txt
    python web_app.py
puis ouvrir http://127.0.0.1:5000

Le bot est instancie une seule fois au demarrage (chargement du graphe,
entrainement TF-IDF + Naive Bayes) et partage entre les requetes.
"""
import os

from flask import Flask, jsonify, render_template, request

from main import ChatBot

try:  # config centralisee optionnelle (cf. config.py)
    from config import DATA_DIR, FEEDBACK_LOG, FEEDBACK_RETRAIN_EVERY
except ImportError:  # valeurs par defaut si config.py absent
    DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data') + os.sep
    FEEDBACK_LOG = os.path.join(DATA_DIR, 'feedback_log.json')
    FEEDBACK_RETRAIN_EVERY = 3


app = Flask(__name__)
bot = ChatBot(data_dir=DATA_DIR)
_feedback_count = 0


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json(silent=True) or {}
    question = (data.get('question') or '').strip()
    if not question:
        return jsonify({'error': 'question vide'}), 400
    answer = bot.answer(question)
    return jsonify({'answer': answer})


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
