"""Configuration centralisee du ChatBot IA.

Regroupe en un seul endroit les chemins de donnees, les parametres de
comportement (seuil de re-entrainement, distance de Levenshtein pour la
NER) et la configuration de la journalisation, plutot que de les
disperser en constantes dans chaque module. Les autres modules importent
ces valeurs (`main.py`, `ui.py`, `web_app.py`).
"""
import logging
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- Chemins de donnees ---
DATA_DIR = os.path.join(BASE_DIR, 'data') + os.sep
KNOWLEDGE_GRAPH = os.path.join(DATA_DIR, 'knowledge_graph.json')
QA_PAIRS = os.path.join(DATA_DIR, 'qa_pairs.json')
FEEDBACK_LOG = os.path.join(DATA_DIR, 'feedback_log.json')

# --- Parametres de comportement ---
# Nombre de retours utilisateur avant un re-entrainement automatique.
FEEDBACK_RETRAIN_EVERY = 3
# Distance de Levenshtein maximale toleree pour rattacher un mot a un
# concept du graphe lors de l'extraction d'entites (NER approximative).
LEVENSHTEIN_MAX_DISTANCE = 1

# --- Journalisation ---
LOG_FILE = os.path.join(BASE_DIR, 'chatbot.log')
LOG_LEVEL = 'INFO'


def get_logger(name: str = 'chatbot') -> logging.Logger:
    """Retourne un logger configure pour ecrire dans `LOG_FILE`.

    Idempotent : appele plusieurs fois, il ne rajoute pas de handler en
    double. `propagate=False` evite de polluer le logger racine (et donc
    la sortie standard des tests)."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
        handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
        handler.setFormatter(
            logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
        logger.addHandler(handler)
        logger.propagate = False
    return logger
