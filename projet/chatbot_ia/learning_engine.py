import math
import json
from collections import defaultdict


class LearningEngine:
    def __init__(self):
        self.tfidf_matrix = None
        self.vocabulary = {}
        self.idf = {}
        self.feedback_log = []
        self._nb_prior = {}
        self._nb_likelihood = {}
        self._nb_classes = []

    def build_tfidf(self, documents: list) -> None:
        N = len(documents)
        df = defaultdict(int)
        for doc in documents:
            for term in set(doc):
                df[term] += 1
        for term, count in df.items():
            self.idf[term] = math.log((N + 1) / (count + 1)) + 1
        self.vocabulary = {term: i for i, term in enumerate(self.idf)}
        self.tfidf_matrix = []
        for doc in documents:
            tf = defaultdict(int)
            for term in doc:
                tf[term] += 1
            vec = {}
            for term, count in tf.items():
                if term in self.idf:
                    vec[term] = (count / max(len(doc), 1)) * self.idf[term]
            self.tfidf_matrix.append(vec)

    def cosine_similarity(self, vec_a: dict, vec_b: dict) -> float:
        common = set(vec_a) & set(vec_b)
        dot = sum(vec_a[t] * vec_b[t] for t in common)
        norm_a = math.sqrt(sum(v ** 2 for v in vec_a.values()))
        norm_b = math.sqrt(sum(v ** 2 for v in vec_b.values()))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    def rank_answers(self, query_tokens: list, candidates: list) -> list:
        if not candidates:
            return candidates
        if not self.idf:
            return [c for c in candidates if c]

        tf = defaultdict(int)
        for token in query_tokens:
            tf[token] += 1
        query_vec = {
            term: (count / max(len(query_tokens), 1)) * self.idf[term]
            for term, count in tf.items()
            if term in self.idf
        }

        scored = []
        for candidate in candidates:
            if not candidate:
                continue
            tokens = candidate.lower().split()
            tf2 = defaultdict(int)
            for t in tokens:
                tf2[t] += 1
            doc_vec = {
                term: (count / max(len(tokens), 1)) * self.idf[term]
                for term, count in tf2.items()
                if term in self.idf
            }
            score = self.cosine_similarity(query_vec, doc_vec)
            scored.append((score, candidate))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [c for _, c in scored]

    def train_naive_bayes(self, X: list, y: list) -> None:
        self._nb_classes = list(set(y))
        total = len(y)
        class_counts = defaultdict(int)
        word_counts = defaultdict(lambda: defaultdict(int))
        class_word_totals = defaultdict(int)

        for tokens, label in zip(X, y):
            class_counts[label] += 1
            for token in tokens:
                word_counts[label][token] += 1
                class_word_totals[label] += 1

        self._nb_prior = {c: class_counts[c] / total for c in self._nb_classes}
        vocab = set(w for counts in word_counts.values() for w in counts)
        vocab_size = len(vocab)
        self._nb_likelihood = {}
        for c in self._nb_classes:
            self._nb_likelihood[c] = {
                w: (word_counts[c][w] + 1) / (class_word_totals[c] + vocab_size)
                for w in vocab
            }

    def predict_intent(self, tokens: list) -> str:
        if not self._nb_classes:
            return 'QUESTION'
        best_class, best_score = None, float('-inf')
        for c in self._nb_classes:
            score = math.log(self._nb_prior.get(c, 1e-10))
            for token in tokens:
                prob = self._nb_likelihood.get(c, {}).get(token, 1e-10)
                score += math.log(prob)
            if score > best_score:
                best_score, best_class = score, c
        return best_class or 'QUESTION'

    def record_feedback(self, question: str, answer: str, score: int) -> None:
        self.feedback_log.append({'question': question, 'answer': answer, 'score': score})

    def retrain(self) -> None:
        pass

    def save_feedback(self, filepath: str) -> None:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.feedback_log, f, ensure_ascii=False, indent=2)

    def load_feedback(self, filepath: str) -> None:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.feedback_log = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.feedback_log = []
