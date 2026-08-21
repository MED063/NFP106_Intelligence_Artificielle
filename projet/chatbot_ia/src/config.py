"""Configuration centralisee du ChatBot IA.
Regroupe en un seul endroit les chemins de donnees, les parametres de comportement (seuil de re-entrainement, distance de Levenshtein pour la
NER) et la configuration de la journalisation, plutot que de les disperser en constantes dans chaque module. Les autres modules importent
ces valeurs (`main.py`, `ui.py`, `web_app.py`).
"""
import logging
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)  # racine du projet (parent de src/)

#  Chemins de donnees 
DATA_DIR = os.path.join(PROJECT_ROOT, 'data') + os.sep
KNOWLEDGE_GRAPH = os.path.join(DATA_DIR, 'knowledge_graph.json')
QA_PAIRS = os.path.join(DATA_DIR, 'qa_pairs.json')
FEEDBACK_LOG = os.path.join(DATA_DIR, 'feedback_log.json')

#  Parametres de comportement 
# Nombre de retours utilisateur avant un re-entrainement automatique.
FEEDBACK_RETRAIN_EVERY = 3
# Distance de Levenshtein maximale toleree pour rattacher un mot a un concept du graphe lors de l'extraction d'entites.
LEVENSHTEIN_MAX_DISTANCE = 1

#  Journalisation 
LOG_FILE = os.path.join(PROJECT_ROOT, 'chatbot.log')
LOG_LEVEL = 'INFO'

# ######## CODE IA (Claude - Anthropic) #########
""" LLM optionnel (reformulation RAG) 
 Desactive par defaut : le systeme fonctionne entierement sans LLM (le coeur maison reste autonome). Active, le LLM ne fait que REFORMULER en
 langage naturel la reponse deja trouvee par le moteur maison (approche RAG : il ne doit rien inventer), et sert de filet de secours quand aucune
reponse n'est trouvee. Compatible avec toute API "OpenAI-compatible"  en changeant simplement les variables d'environnement ci-dessous.
"""
USE_LLM = os.environ.get('USE_LLM', '0') in ('1', 'true', 'True', 'yes')
LLM_API_BASE = os.environ.get('LLM_API_BASE', 'https://api.groq.com/openai/v1')
LLM_MODEL = os.environ.get('LLM_MODEL', 'openai/gpt-oss-20b')
# La cle est lue dans l'environnement (Si voulez tester avec la reformulation, vous pouvez pouvez me sollicitez monsieur et je vous fournirai la cle).
LLM_API_KEY = os.environ.get('LLM_API_KEY', os.environ.get('GROQ_API_KEY', ''))
LLM_TIMEOUT = float(os.environ.get('LLM_TIMEOUT', '15'))
LLM_TEMPERATURE = 0.2
LLM_MAX_TOKENS = 500


def get_logger(name: str = 'chatbot') -> logging.Logger:
    """Retourne un logger configure pour ecrire dans `LOG_FILE`. Idempotent : appele plusieurs fois, il ne rajoute pas de handler en
    double. `propagate=False` evite de polluer le logger racine ."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
        handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
        handler.setFormatter(
            logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
        logger.addHandler(handler)
        logger.propagate = False
    return logger
# ###############################################
