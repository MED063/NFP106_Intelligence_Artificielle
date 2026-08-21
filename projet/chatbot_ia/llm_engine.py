"""Moteur LLM optionnel (reformulation RAG).

Ce module est **facultatif** : le ChatBot fonctionne entierement sans lui. Quand `config.USE_LLM` est actif et qu'une cle d'API est fournie,
il permet deux choses :

1. Reformuler en langage naturel la reponse deja selectionnee par le moteur
   maison (recherche dans le graphe + TF-IDF). C'est une approche RAG : le
   LLM ne s'appuie que sur le contexte fourni et ne doit rien inventer, ce
   qui limite fortement les hallucinations  essentiel en sante.
2. Servir de filet de secours quand le moteur maison ne trouve aucune
   reponse, en repondant de facon prudente.

L'implementation utilise uniquement la bibliotheque standard (`urllib`) et parle a n'importe quelle API "OpenAI-compatible" (Groq ratuit par defaut,
aucune dependance lourde n'est ajoutee, conformement aux contraintes du projet.

Toute erreur (cle absente, reseau indisponible, delai depasse, reponseinattendue) est capturee et renvoie `None` :
l'appelant retombe alors sur la reponse brute du moteur maison. Le LLM ne peut donc jamais casser le pipeline.
"""
import json
import urllib.error
import urllib.request

import config


# ######## CODE IA (Claude - Anthropic) #########
USER_AGENT = 'Mozilla/5.0 (compatible; chatbot-ia/1.0; +https://github.com/MED063)'


def _headers() -> dict:
    return {
        'Authorization': f'Bearer {config.LLM_API_KEY}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'User-Agent': USER_AGENT,
    }

SYSTEM_REFORMULATE = (
    "Tu es un assistant sante francophone. On te donne une QUESTION et une "
    "REPONSE de reference issue d'une base de connaissances verifiee. "
    "Reformule cette reponse de facon claire, naturelle et concise pour "
    "repondre a la question. Ne t'appuie QUE sur la reponse de reference : "
    "n'ajoute aucune information medicale qui n'y figure pas. Reponds en "
    "francais. Termine par un bref rappel que cela ne remplace pas un avis "
    "medical."
)

SYSTEM_FALLBACK = (
    "Tu es un assistant sante francophone. La base de connaissances ne "
    "contient pas de reponse a cette question. Reponds brievement et "
    "prudemment si le sujet releve de la sante generale ; si tu n'es pas sur "
    "ou si la question sort du domaine de la sante, dis-le clairement plutot "
    "que d'inventer. Termine par un rappel que cela ne remplace pas un avis "
    "medical."
)


class LLMEngine:
    """Client minimal vers une API de chat "OpenAI-compatible"."""

    def __init__(self, logger=None):
        self.logger = logger

    def is_available(self) -> bool:
        """Vrai seulement si le LLM est active ET qu'une cle est fournie."""
        return bool(config.USE_LLM and config.LLM_API_KEY)

    def reformulate(self, question: str, reference_answer: str):
        """Reformule `reference_answer` pour repondre a `question`.
        Renvoie le texte reformule, ou None en cas d'echec (l'appelant
        retombe alors sur `reference_answer`)."""
        if not self.is_available() or not reference_answer:
            return None
        messages = [
            {"role": "system", "content": SYSTEM_REFORMULATE},
            {"role": "user",
             "content": f"QUESTION : {question}\n\nREPONSE DE REFERENCE : {reference_answer}"},
        ]
        return self._chat(messages)

    def answer_fallback(self, question: str):
        """Repond a une question pour laquelle le moteur maison n'a rien
        trouve. Renvoie None en cas d'echec."""
        if not self.is_available():
            return None
        messages = [
            {"role": "system", "content": SYSTEM_FALLBACK},
            {"role": "user", "content": question},
        ]
        return self._chat(messages)

    def _chat(self, messages: list):
        """Appelle l'endpoint /chat/completions. Renvoie le contenu texte
        ou None en cas d'erreur (jamais d'exception propagee)."""
        url = config.LLM_API_BASE.rstrip('/') + '/chat/completions'
        payload = json.dumps({
            "model": config.LLM_MODEL,
            "messages": messages,
            "temperature": config.LLM_TEMPERATURE,
            "max_tokens": config.LLM_MAX_TOKENS,
        }).encode('utf-8')
        request = urllib.request.Request(
            url, data=payload, method='POST', headers=_headers())
        try:
            with urllib.request.urlopen(request, timeout=config.LLM_TIMEOUT) as resp:
                data = json.loads(resp.read().decode('utf-8'))
            content = data['choices'][0]['message']['content'].strip()
            return content or None
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError,
                KeyError, IndexError, ValueError) as exc:
            if self.logger:
                self.logger.warning('Appel LLM echoue (%s), repli sur la reponse maison', exc)
            return None


def self_test() -> int:
    """Diagnostic : verifie la config LLM et tente un appel reel, en
    affichant la cause exacte en cas d'echec (statut HTTP + corps de la
    reponse). A lancer avec :  python llm_engine.py"""
    key = config.LLM_API_KEY
    print("--- Diagnostic LLM ---")
    print(f"USE_LLM        : {config.USE_LLM}")
    print(f"Cle presente   : {bool(key)}" + (f" (…{key[-4:]})" if key else ""))
    print(f"Endpoint       : {config.LLM_API_BASE}")
    print(f"Modele         : {config.LLM_MODEL}")
    if not key:
        print("\n=> Aucune cle. Definis-la puis relance :")
        print('   export LLM_API_KEY="ta_cle_groq"')
        return 1
    url = config.LLM_API_BASE.rstrip('/') + '/chat/completions'
    payload = json.dumps({
        "model": config.LLM_MODEL,
        "messages": [{"role": "user", "content": "Reponds juste: OK"}],
        "max_tokens": 5,
    }).encode('utf-8')
    req = urllib.request.Request(url, data=payload, method='POST', headers=_headers())
    try:
        with urllib.request.urlopen(req, timeout=config.LLM_TIMEOUT) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        print("\n=> Appel reussi. Reponse du modele :",
              data['choices'][0]['message']['content'].strip())
        print("Le LLM est fonctionnel.")
        return 0
    except urllib.error.HTTPError as exc:
        body = exc.read().decode('utf-8', 'replace')
        print(f"\n=> Echec HTTP {exc.code}. Reponse de l'API :\n{body}")
        print("(401 = cle invalide ; 404/400 model = changer LLM_MODEL ; "
              "429 = quota/rate limit)")
        return 1
    except Exception as exc:  
        print(f"\n=> Echec : {type(exc).__name__}: {exc}")
        print("(souvent : pas de reseau, ou endpoint LLM_API_BASE incorrect)")
        return 1


# ###############################################
if __name__ == '__main__':
    import sys
    sys.exit(self_test())
