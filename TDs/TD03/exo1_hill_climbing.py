"""
Hill Climbing sur le labyrinthe (TD03 — Exo 1).

Algorithme (steepest ascent) :
  À chaque étape, on choisit le voisin non visité avec le h minimal.
  Si aucun voisin n'améliore h → optimum local → échec.
"""
from labyrinthe_utils import (
    LABYRINTHE, TAILLE_CASE, HAUT_BAR_H, PANNEAU_DROIT_W,
    COL_PANEL, COL_PANEL_BORD, COL_TEXTE_MUET, COL_VISITE,
    voisins_4, heuristique, trouver_case,
    dessiner_overlay_rgba, dessiner_glow,
    COL_DEPART, COL_SORTIE, COL_H, COL_NUM,
    AppliLabyrinthe,
)
import pygame

# Couleurs spécifiques HC
COL_COURANT = (120, 175, 255, 190)
COL_VOISINS = (255, 220, 120, 160)
COL_BLOQUE  = (255, 80, 80, 160)

# ============================================================
# ALGORITHME HILL CLIMBING
# ============================================================

def hc_initialiser(depart, arrivee):
    return {
        "courant":           depart,
        "visite":            {depart},
        "chemin":            [depart],
        "voisins_candidats": [],
        "meilleur_voisin":   None,
        "statut":            "en_cours",
        "arrivee":           arrivee,
        "nb_etapes":         0,
    }

def hc_faire_une_etape(grille, etat):
    if etat["statut"] != "en_cours":
        return

    etat["nb_etapes"] += 1
    courant = etat["courant"]
    arrivee = etat["arrivee"]

    if courant == arrivee:
        etat["statut"] = "succes"
        return

    h_courant  = heuristique(courant, arrivee)
    candidats  = [
        (heuristique((nr, nc), arrivee), (nr, nc))
        for nr, nc, _ in voisins_4(grille, *courant)
        if (nr, nc) not in etat["visite"]
    ]
    etat["voisins_candidats"] = [pos for _, pos in candidats]

    if not candidats:
        etat["statut"] = "echec"
        etat["meilleur_voisin"] = None
        return

    candidats.sort()
    h_best, meilleur = candidats[0]
    etat["meilleur_voisin"] = meilleur

    if h_best >= h_courant:
        etat["statut"] = "echec"
        return

    etat["courant"] = meilleur
    etat["visite"].add(meilleur)
    etat["chemin"].append(meilleur)

    if meilleur == arrivee:
        etat["statut"] = "succes"

# ============================================================
# APPLICATION
# ============================================================

class AppliHC(AppliLabyrinthe):

    EVENT_MS = 300
    PAS_MS   = 80

    def __init__(self, grille):
        super().__init__(grille, "Labyrinthe — Hill Climbing")

    def _titre(self):
        return "Hill Climbing — Prêt (E=auto, ESPACE=pas à pas)"

    def _demarrer_algo(self):
        self.etat_algo = hc_initialiser(self.depart, self.sortie)
        self._sync()

    def _faire_etape(self):
        hc_faire_une_etape(self.grille, self.etat_algo)

    def _statut_termine(self):
        return self.etat_algo is not None and self.etat_algo["statut"] != "en_cours"

    def _sync(self):
        ea = self.etat_algo
        if ea is None:
            return

        courant = ea["courant"]
        statut  = ea["statut"]
        self.vu.add(courant)

        if courant != self.pos_png:
            self._planifier_route(courant)

        h_c = heuristique(courant, self.sortie)

        if statut == "succes":
            self.texte_haut = f"SUCCÈS en {ea['nb_etapes']} étapes."
            self.histo.appendleft("SUCCÈS !")
            self.revele = True
        elif statut == "echec":
            self.texte_haut = f"ÉCHEC — Optimum local en {courant} (h={h_c})"
            self.histo.appendleft(f"Bloqué en {courant}, h={h_c}")
            self.revele = True
        else:
            mv = ea.get("meilleur_voisin")
            info = f"→ {mv} h={heuristique(mv, self.sortie)}" if mv else "aucun voisin libre"
            self.texte_haut = f"Pos: {courant} h={h_c} | {info}"
            self.histo.appendleft(self.texte_haut[:42])

    def dessiner_monde(self):
        ea       = self.etat_algo
        courant  = ea["courant"]           if ea else None
        visite   = set(ea["chemin"])       if ea else set()
        candidats= set(ea["voisins_candidats"]) if ea else set()
        statut   = ea["statut"]            if ea else "idle"

        for r in range(self.lignes):
            for c in range(self.colonnes):
                ch  = self.grille[r][c]
                pos = (r, c)
                self._dessiner_fond_case(r, c, ch)

                if ch != "#":
                    if pos in visite and pos != courant:
                        dessiner_overlay_rgba(self.ecran, self._rect(r, c), COL_VISITE)
                    if pos in candidats and pos != courant:
                        dessiner_overlay_rgba(self.ecran, self._rect(r, c), COL_VOISINS)
                    if pos == courant:
                        col = COL_BLOQUE if statut == "echec" else COL_COURANT
                        dessiner_overlay_rgba(self.ecran, self._rect(r, c), col,
                            outline=(235, 235, 245, 170))
                    self._dessiner_h_case(r, c)

                self._dessiner_marqueurs_SE(r, c, ch)
                self._dessiner_num_ordre(r, c)

        self._dessiner_brouillard()
        self._dessiner_pingouin()

    def dessiner_panneau_droit(self):
        x0, y0 = self.largeur_monde, HAUT_BAR_H
        self._dessiner_panneau_fond()
        self._txt(x0+12, y0+10, "Hill Climbing", self.font_petit)
        self._txt(x0+12, y0+30, "Steepest ascent — greedy sur h", self.font_tiny, COL_TEXTE_MUET)

        legende = [
            (COL_VISITE[:3],   "Déjà visité (chemin HC)"),
            (COL_VOISINS[:3],  "Voisins candidats"),
            (COL_COURANT[:3],  "Position courante"),
            (COL_BLOQUE[:3],   "Optimum local (bloqué)"),
        ]
        y = self._dessiner_legende(x0, y0+62, legende)

        ea = self.etat_algo
        if ea:
            y += 16
            self._txt(x0+12, y, f"Courant   : {ea['courant']}", self.font_tiny, COL_TEXTE_MUET); y += 18
            self._txt(x0+12, y, f"h courant : {heuristique(ea['courant'], self.sortie)}", self.font_tiny, COL_TEXTE_MUET); y += 18
            self._txt(x0+12, y, f"Longueur  : {len(ea['chemin'])}", self.font_tiny, COL_TEXTE_MUET); y += 18
            self._txt(x0+12, y, f"Étapes    : {ea['nb_etapes']}", self.font_tiny, COL_TEXTE_MUET); y += 18

        y += 10
        self._dessiner_histo(x0, y)

    def dessiner_barre_bas(self):
        y = HAUT_BAR_H + self.hauteur_monde
        pygame.draw.rect(self.ecran, COL_PANEL, pygame.Rect(0, y, self.largeur_fen, 72))
        pygame.draw.line(self.ecran, COL_PANEL_BORD, (0, y), (self.largeur_fen, y), 2)

        ea = self.etat_algo
        self._txt(12, y+8,  f"Statut : {ea['statut'] if ea else '—'} | Étapes : {ea['nb_etapes'] if ea else 0}", self.font_petit)
        self._txt(12, y+32, f"Pas pingouin : {self.nb_pas}", self.font_petit)
        self._txt(self.largeur_fen-680, y+8,
            "E=Auto   ESPACE=Pas à pas   R=Reset   F=Brouillard   Q=Quitter",
            self.font_petit, COL_TEXTE_MUET)


if __name__ == "__main__":
    AppliHC(LABYRINTHE).run()
