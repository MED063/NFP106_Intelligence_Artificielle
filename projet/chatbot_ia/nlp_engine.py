import re
from collections import defaultdict


STOPWORDS_FR = {
    'le', 'la', 'les', 'de', 'du', 'des', 'un', 'une', 'et', 'est', 'en',
    'au', 'aux', 'ce', 'se', 'sa', 'son', 'ses', 'mon', 'ma', 'mes', 'ton',
    'ta', 'tes', 'il', 'elle', 'ils', 'elles', 'nous', 'vous', 'je', 'tu',
    'que', 'qui', 'quoi', 'dont', 'par', 'pour', 'sur', 'sous', 'dans',
    'avec', 'sans', 'mais', 'ou', 'donc', 'or', 'ni', 'car', 'si', 'ne',
    'pas', 'plus', 'bien', 'tres', 'aussi', 'tout', 'meme', 'leur', 'leurs',
    'cet', 'cette', 'ces', 'y', 'a', 'c', 'd', 'j', 'l', 'm', 'n', 's', 't'
}


class NLPEngine:
    def __init__(self):
        self.stopwords = STOPWORDS_FR
        self.stemmer = None

    def tokenize(self, text: str) -> list:
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        return [t for t in text.split() if t]

    def remove_stopwords(self, tokens: list) -> list:
        return [t for t in tokens if t not in self.stopwords]

    def stem(self, tokens: list) -> list:
        result = []
        for token in tokens:
            if token.endswith('tion') and len(token) > 6:
                token = token[:-4]
            elif token.endswith('ment') and len(token) > 6:
                token = token[:-4]
            elif token.endswith('ique') and len(token) > 6:
                token = token[:-4]
            elif token.endswith('eur') and len(token) > 5:
                token = token[:-3]
            elif token.endswith('age') and len(token) > 5:
                token = token[:-3]
            elif token.endswith('ement') and len(token) > 7:
                token = token[:-5]
            result.append(token)
        return result

    def preprocess(self, text: str) -> list:
        tokens = self.tokenize(text)
        tokens = self.remove_stopwords(tokens)
        tokens = self.stem(tokens)
        return tokens

    def classify_intent(self, tokens: list) -> str:
        words = set(tokens)

        def has_root(roots):
            return any(token.startswith(root) for token in tokens for root in roots)

        if any(w in words for w in ['bonjour', 'salut', 'hello', 'bonsoir', 'coucou']):
            return 'SALUTATION'
        if any(w in words for w in ['quitter', 'quit', 'exit', 'aurevoir', 'bye', 'revoir']):
            return 'QUITTER'
        if has_root(['risque', 'facteur', 'danger', 'favorise']):
            return 'FACTEURS_RISQUE'
        if has_root(['cause', 'origine', 'pourquoi', 'raison']):
            return 'CAUSES'
        if has_root(['différence', 'differenc', 'comparer', 'versus', 'lien', 'entre']):
            return 'COMPARAISON'
        if has_root(['sympt', 'signe', 'manifest', 'ressent']):
            return 'SYMPTOMES'
        if has_root(['trait', 'guér', 'guer', 'soign', 'médicament', 'medicament', 'thérap', 'therap', 'gér', 'ger', 'réduir', 'reduir']) or 'faire' in words:
            return 'TRAITEMENT'
        if has_root(['préven', 'preven', 'évite', 'evite', 'protèg', 'proteg', 'amélior', 'amelior']):
            return 'PREVENTION'
        if has_root(['fonction', 'mécanis', 'mecanis', 'processus', 'marche', 'affect']):
            return 'FONCTIONNEMENT'
        if 'qu' in words or has_root(['définition', 'definition', 'définir', 'definir', 'signifie', 'signif']):
            return 'DEFINITION'
        return 'DEFINITION'

    def extract_entities(self, tokens: list, kb) -> list:
        concepts = set(kb.graph.keys())
        entities = []
        for token in tokens:
            if token in concepts:
                entities.append(token)
            else:
                for concept in concepts:
                    if self._levenshtein(token, concept) <= 1 and len(token) > 3:
                        entities.append(concept)
                        break
        return list(set(entities))

    def _levenshtein(self, s1: str, s2: str) -> int:
        if len(s1) < len(s2):
            return self._levenshtein(s2, s1)
        if len(s2) == 0:
            return len(s1)
        prev = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            curr = [i + 1]
            for j, c2 in enumerate(s2):
                curr.append(min(prev[j + 1] + 1, curr[j] + 1, prev[j] + (c1 != c2)))
            prev = curr
        return prev[-1]
