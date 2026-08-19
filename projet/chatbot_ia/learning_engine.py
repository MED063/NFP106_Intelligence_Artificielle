import math
import json
from collections import defaultdict


class LearningEngine:
    def __init__(self, tokenizer=None):
        self.tfidf_matrix = None
        self.vocabulary = {}
        self.idf = {}
        self.feedback_log = []
        self._nb_prior = {}
        self._nb_likelihood = {}
        self._nb_classes = []
        # Tokenizer applique aux reponses candidates dans rank_answers.
        # Par defaut un simple split (retro-compatible) ; en pratique on y
        # injecte NLPEngine.preprocess pour que les candidats soient
        # normalises (accents, ponctuation, stemming) exactement comme le
        # vocabulaire TF-IDF construit par build_tfidf, sans quoi des
        # reponses correctes sont mal classees a cause d'un simple accent
        # ou d'une parenthese collee au mot.
        self._tokenize_candidate = tokenizer or (lambda text: text.lower().split())

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
            tokens = self._tokenize_candidate(candidate)
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

    # Poids applique a l'ajustement par feedback dans feedback_score.
    FEEDBACK_GAIN = 3.0

    def record_feedback(self, question: str, answer: str, score: int) -> None:
        """Enregistre le retour utilisateur (1-5).
        score >= 4 : renforce l'association ; score <= 2 : pénalise.
        """
        self.feedback_log.append({'question': question, 'answer': answer, 'score': score})

    def feedback_score(self, question: str, candidate_answer: str) -> float:
        """Ajustement de pertinence issu du feedback pour une reponse
        candidate face a une question donnee. Conformement au sujet, une
        note >= 4 renforce l'association question/reponse et une note <= 2
        la penalise. La contribution de chaque retour est (note - 3), agregee
        sur les questions quasi identiques (Jaccard des tokens >= 0.8) et
        ponderee par FEEDBACK_GAIN.

        Neutre (0.0) tant qu'aucun feedback pertinent n'existe : le
        comportement par defaut du ChatBot est donc strictement inchange, et
        le feedback ne fait qu'ameliorer le classement des reponses futures."""
        if not self.feedback_log:
            return 0.0
        q_tokens = set(self._tokenize_candidate(question))
        if not q_tokens:
            return 0.0
        total = 0.0
        for entry in self.feedback_log:
            if entry.get('answer') != candidate_answer:
                continue
            e_tokens = set(self._tokenize_candidate(entry.get('question', '')))
            if not e_tokens:
                continue
            jaccard = len(q_tokens & e_tokens) / len(q_tokens | e_tokens)
            if jaccard >= 0.8:
                total += entry.get('score', 3) - 3
        return total * self.FEEDBACK_GAIN

    def retrain(self, kb=None) -> None:
        """Re-entraîne TF-IDF sur les réponses bien notées et met à jour les poids du graphe."""
        import re
        positive = [e for e in self.feedback_log if e.get('score', 0) >= 4]
        if positive:
            positive_docs = [
                [t for t in re.sub(r'[^\w\s]', ' ', e['answer'].lower()).split() if t]
                for e in positive
            ]
            self.build_tfidf(positive_docs)

        if kb is None:
            return
        delta_map = {1: -0.05, 2: -0.05, 4: 0.05, 5: 0.05}
        for entry in self.feedback_log:
            delta = delta_map.get(entry.get('score', 3), 0.0)
            if delta == 0.0:
                continue
            tokens = [t for t in re.sub(r'[^\w\s]', ' ', entry.get('answer', '').lower()).split() if t]
            concepts = [t for t in tokens if t in kb.graph]
            for i, c1 in enumerate(concepts):
                for c2 in concepts[i + 1:]:
                    if c2 in kb.graph.get(c1, {}):
                        kb.graph[c1][c2] = min(1.0, max(0.01, kb.graph[c1][c2] + delta))

    def save_feedback(self, filepath: str) -> None:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.feedback_log, f, ensure_ascii=False, indent=2)

    def load_feedback(self, filepath: str) -> None:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.feedback_log = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.feedback_log = []
