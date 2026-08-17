import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import config


def test_config_exposes_paths():
    assert config.DATA_DIR.endswith(os.sep)
    assert config.KNOWLEDGE_GRAPH.endswith('knowledge_graph.json')
    assert config.QA_PAIRS.endswith('qa_pairs.json')
    assert config.FEEDBACK_LOG.endswith('feedback_log.json')


def test_config_behaviour_params():
    assert config.FEEDBACK_RETRAIN_EVERY >= 1
    assert config.LEVENSHTEIN_MAX_DISTANCE >= 1


def test_get_logger_is_idempotent():
    logger = config.get_logger('chatbot_test')
    n = len(logger.handlers)
    logger2 = config.get_logger('chatbot_test')
    assert logger is logger2
    # Un second appel ne doit pas rajouter de handler en double.
    assert len(logger2.handlers) == n
    assert n >= 1
