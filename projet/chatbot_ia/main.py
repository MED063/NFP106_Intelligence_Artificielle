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
        self.learner = LearningEngine(tokenizer=self.nlp.preprocess)
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

        # V2 de classify_intent : Naive Bayes entraine sur les intentions
        # etiquetees des qa_pairs, utilise comme filet de securite quand
        # aucune regle (V1) ne s'applique.
        labeled = [
            (self.nlp.preprocess(qa['question']), qa['intent'])
            for qa in self.kb.qa_pairs
            if qa.get('question') and qa.get('intent')
        ]
        if labeled:
            X, y = zip(*labeled)
            self.learner.train_naive_bayes(list(X), list(y))
            self._nb_ready = True
        else:
            self._nb_ready = False

    def retrain(self) -> None:
        self.learner.retrain(self.kb)

    def answer(self, user_input: str) -> str:
        tokens = self.nlp.preprocess(user_input)
        nb_fallback = self.learner.predict_intent if self._nb_ready else None
        intent = self.nlp.classify_intent(tokens, nb_fallback=nb_fallback)

        if intent == 'SALUTATION':
            return 'Bonjour ! Comment puis-je vous aider ?'
        if intent == 'QUITTER':
            return 'Au revoir !'

        entities = self.nlp.extract_entities(tokens, self.kb)
        candidates = self.search.find_best_answer(entities, intent)
        if not candidates:
            return "Je n'ai pas trouvé de réponse à votre question."

        # Le score du graphe (chevauchement d'entites + intention) fait
        # foi ; le TF-IDF ne sert qu'a departager les reponses ex-aequo
        # (ex : deux Q/A partageant exactement les memes concepts).
        top_score = candidates[0][0]
        tied = [answer for score, answer in candidates if score == top_score]
        if len(tied) == 1:
            return tied[0]
        ranked = self.learner.rank_answers(tokens, tied)
        return ranked[0] if ranked else tied[0]


if __name__ == '__main__':
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    bot = ChatBot(data_dir=data_dir + os.sep)
    from ui import run_cli
    run_cli(bot)
