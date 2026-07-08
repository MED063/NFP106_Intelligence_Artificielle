import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from knowledge_base import KnowledgeBase
from nlp_engine import NLPEngine
from search_engine import SearchEngine
from learning_engine import LearningEngine


class ChatBot:
    def __init__(self, data_dir: str = 'data/'):
        self.kb = KnowledgeBase()
        self.nlp = NLPEngine()
        self.search = SearchEngine(self.kb)
        self.learner = LearningEngine()
        self._load_data(data_dir)

    def _load_data(self, data_dir: str) -> None:
        kg_path = os.path.join(data_dir, 'knowledge_graph.json')
        qa_path = os.path.join(data_dir, 'qa_pairs.json')
        fb_path = os.path.join(data_dir, 'feedback_log.json')

        if os.path.exists(kg_path):
            self.kb.load_from_json(kg_path)
        if os.path.exists(qa_path):
            self.kb.load_qa_from_json(qa_path)
        if os.path.exists(fb_path):
            self.learner.load_feedback(fb_path)

        documents = [self.nlp.preprocess(qa['answer']) for qa in self.kb.qa_pairs]
        if documents:
            self.learner.build_tfidf(documents)

    def retrain(self) -> None:
        self.learner.retrain(self.kb)

    def answer(self, user_input: str) -> str:
        tokens = self.nlp.preprocess(user_input)
        intent = self.nlp.classify_intent(tokens)

        if intent == 'SALUTATION':
            return 'Bonjour ! Comment puis-je vous aider ?'
        if intent == 'QUITTER':
            return 'Au revoir !'

        entities = self.nlp.extract_entities(tokens, self.kb)
        raw_answer = self.search.find_best_answer(entities, intent)
        ranked = self.learner.rank_answers(tokens, [raw_answer] if raw_answer else [])

        return ranked[0] if ranked else "Je n'ai pas trouvé de réponse à votre question."


if __name__ == '__main__':
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    bot = ChatBot(data_dir=data_dir + os.sep)
    from ui import run_cli
    run_cli(bot)
