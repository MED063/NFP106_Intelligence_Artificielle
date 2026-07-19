"""
main.py

A chaque coup, on affiche :
  * le SCORE MinMax calcule pour CHAQUE case libre (vert = l'IA gagne,
    gris = nul, rouge = l'IA perd), directement sur la grille ;
  * la case choisie par l'IA, mise en evidence ;
  * un PANNEAU lateral avec le nombre de noeuds explores, le nombre de
    branches coupees par l'elagage Alpha-Beta, la profondeur, et une
    explication en francais de la decision ;
  * un bouton pour ACTIVER / DESACTIVER l'elagage et constater en direct
    la difference de noeuds explores (interet de l'Alpha-Beta).

"""

import sys

import pygame

import algo
from algo import (
    EMPTY, PLAYER_X, PLAYER_O,
    new_board, winner, winning_line, is_full, is_terminal,
    available_moves, best_move, explain_decision,
)

# Constantes d'affichage

BOARD_SIZE = 540           
CELL = BOARD_SIZE // 3
PANEL_W = 380              
MARGIN = 20
WIDTH = BOARD_SIZE + PANEL_W
HEIGHT = BOARD_SIZE + 90   
FPS = 60

# Duree (ms) pendant laquelle le raisonnement de l'IA 

THINK_DELAY_MS = 4000 

# Couleurs (R, V, B)
BG = (24, 26, 32)
GRID = (70, 76, 92)
PANEL_BG = (32, 35, 44)
WHITE = (235, 238, 245)
GREY = (150, 156, 170)
X_COLOR = (86, 173, 255)     
O_COLOR = (255, 118, 118)    
WIN_COLOR = (120, 230, 160)  
GOOD = (120, 220, 150)      
NEUTRAL = (190, 190, 120)    
BAD = (230, 120, 120)        
BTN = (52, 58, 74)
BTN_HOVER = (72, 80, 104)
HIGHLIGHT = (98, 210, 150)

HUMAN = PLAYER_X
AI = PLAYER_O


class Button:
    """Petit bouton cliquable pour la barre d'outils."""

    def __init__(self, rect, label):
        self.rect = pygame.Rect(rect)
        self.label = label

    def draw(self, surface, font):
        mouse = pygame.mouse.get_pos()
        color = BTN_HOVER if self.rect.collidepoint(mouse) else BTN
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        txt = font.render(self.label, True, WHITE)
        surface.blit(txt, txt.get_rect(center=self.rect.center))

    def clicked(self, pos):
        return self.rect.collidepoint(pos)


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Tic-Tac-Toe : IA MinMax et elagage Alpha-Beta")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

        self.font_xo = pygame.font.SysFont("Arial", 96, bold=True)
        self.font_score = pygame.font.SysFont("Arial", 26, bold=True)
        self.font = pygame.font.SysFont("Arial", 20)
        self.font_small = pygame.font.SysFont("Arial", 17)
        self.font_title = pygame.font.SysFont("Arial", 22, bold=True)
        self.font_help_title = pygame.font.SysFont("Arial", 30, bold=True)

        # Barre  en bas
        by = BOARD_SIZE + 20
        self.btn_new = Button((20, by, 150, 46), "Nouvelle partie")
        self.btn_scores = Button((180, by, 130, 46), "Scores: ON")
        self.btn_prune = Button((320, by, 150, 46), "Alpha-Beta: ON")
        self.btn_ai_first = Button((480, by, 150, 46), "IA commence")
        self.btn_help = Button((650, by, 150, 46), "Comment jouer ?")
        self.buttons = [self.btn_new, self.btn_scores, self.btn_prune,
                        self.btn_ai_first, self.btn_help]

        # Menu d'aide  
        self.show_help = True
        self.help_card = pygame.Rect((WIDTH - 660) // 2, 35, 660, 560)
        self.btn_help_close = Button(
            (self.help_card.centerx - 100, self.help_card.bottom - 60, 200, 44),
            "Commencer a jouer")

        self.show_scores = True
        self.use_pruning = True
        self.reset(ai_first=False)

    # gestion de l'etat
    def reset(self, ai_first=False):
        self.board = new_board()
        self.current = HUMAN
        self.decision = None       # derniere reflexion de l'IA 
        self.explain = []
        self.game_over = False
        self.win_line = None
        self.status = "A vous de jouer (X)."
        if ai_first:
            self.current = AI
            self.status = "L'IA (O) commence..."

    def play(self, cell, player):
        self.board[cell] = player
        wl = winning_line(self.board)
        if wl is not None:
            self.win_line = wl
            self.game_over = True
            who = "Vous avez gagne !" if player == HUMAN else "L'IA a gagne."
            self.status = who
        elif is_full(self.board):
            self.game_over = True
            self.status = "Match nul."
        else:
            self.current = algo.other_player(player)
            if self.current == HUMAN:
                self.status = "A vous de jouer (X)."
            else:
                self.status = "Tour de l'IA (O)..."

    def ai_turn(self):
        """L'IA reflechit, on affiche son raisonnement, puis elle joue."""
        self.decision = best_move(self.board, AI, use_pruning=self.use_pruning)
        self.explain = explain_decision(self.decision, AI)
        self.render()
        pygame.display.flip()
        pygame.time.wait(THINK_DELAY_MS)
        self.play(self.decision.move, AI)

    # rendu 
        self.screen.fill(BG)
        self._draw_board()
        self._draw_panel()
        self._draw_buttons()

    def _draw_board(self):
        # Lignes de la grille
        for i in range(1, 3):
            pygame.draw.line(self.screen, GRID, (i * CELL, 0),
                             (i * CELL, BOARD_SIZE), 4)
            pygame.draw.line(self.screen, GRID, (0, i * CELL),
                             (BOARD_SIZE, i * CELL), 4)

        scores = self.decision.move_scores if self.decision else {}
        chosen = self.decision.move if self.decision else None

        for idx in range(9):
            row, col = divmod(idx, 3)
            x, y = col * CELL, row * CELL
            cell = self.board[idx]

            # case choisie par l'IA
            if (not self.game_over and chosen == idx and cell == EMPTY
                    and self.current == AI):
                pygame.draw.rect(self.screen, (40, 60, 50),
                                 (x + 3, y + 3, CELL - 6, CELL - 6),
                                 border_radius=10)
                pygame.draw.rect(self.screen, HIGHLIGHT,
                                 (x + 3, y + 3, CELL - 6, CELL - 6),
                                 3, border_radius=10)

            if cell != EMPTY:
                color = X_COLOR if cell == PLAYER_X else O_COLOR
                if self.win_line and idx in self.win_line:
                    color = WIN_COLOR
                txt = self.font_xo.render(cell, True, color)
                self.screen.blit(txt, txt.get_rect(center=(x + CELL // 2,
                                                           y + CELL // 2)))
            elif (self.show_scores and idx in scores and not self.game_over
                  and self.current == AI):
                # score MinMax du coup pour l'IA
                s = scores[idx]
                col_score = GOOD if s > 0 else (BAD if s < 0 else NEUTRAL)
                label = f"{s:+d}"
                txt = self.font_score.render(label, True, col_score)
                self.screen.blit(txt, txt.get_rect(center=(x + CELL // 2,
                                                           y + CELL // 2)))

    def _draw_panel(self):
        px = BOARD_SIZE
        pygame.draw.rect(self.screen, PANEL_BG, (px, 0, PANEL_W, BOARD_SIZE))
        x = px + MARGIN
        y = MARGIN

        title = self.font_title.render("Jeu du Morpion ", True, WHITE)
        self.screen.blit(title, (x, y))
        y += 38

        # statut de la partie
        for line in self._wrap(self.status, PANEL_W - 2 * MARGIN, self.font):
            self.screen.blit(self.font.render(line, True, WHITE), (x, y))
            y += 26
        y += 8

        # stats d'exploration
        if self.decision:
            st = self.decision.stats
            pygame.draw.line(self.screen, GRID, (x, y), (px + PANEL_W - MARGIN, y))
            y += 12
            stats_lines = [
                ("Noeuds explores", str(st.nodes_explored), X_COLOR),
                ("Branches elaguees", str(st.branches_pruned), O_COLOR),
                ("Profondeur max", str(st.max_depth), WHITE),
            ]
            for label, val, col in stats_lines:
                self.screen.blit(self.font.render(label, True, GREY), (x, y))
                v = self.font.render(val, True, col)
                self.screen.blit(v, (px + PANEL_W - MARGIN - v.get_width(), y))
                y += 28
            y += 8

            pygame.draw.line(self.screen, GRID, (x, y), (px + PANEL_W - MARGIN, y))
            y += 12
            for line in self.explain:
                if line == "":
                    y += 8
                    continue
                for sub in self._wrap(line, PANEL_W - 2 * MARGIN, self.font_small):
                    self.screen.blit(self.font_small.render(sub, True, WHITE),
                                     (x, y))
                    y += 21

        # legende des scores
        y = BOARD_SIZE - 96
        pygame.draw.line(self.screen, GRID, (x, y), (px + PANEL_W - MARGIN, y))
        y += 10
        self.screen.blit(self.font_small.render("Legende des scores (vue IA) :",
                                                True, GREY), (x, y))
        y += 24
        legend = [("+  l'IA gagne", GOOD), ("0  match nul", NEUTRAL),
                  ("-  l'IA perd", BAD)]
        for text, col in legend:
            pygame.draw.rect(self.screen, col, (x, y + 2, 14, 14), border_radius=3)
            self.screen.blit(self.font_small.render(text, True, WHITE),
                             (x + 22, y))
            y += 22

    def _draw_buttons(self):
        self.btn_scores.label = f"Scores: {'ON' if self.show_scores else 'OFF'}"
        self.btn_prune.label = f"Alpha-Beta: {'ON' if self.use_pruning else 'OFF'}"
        for b in self.buttons:
            b.draw(self.screen, self.font_small)

    def _draw_help(self):
        """Ecran 'Comment jouer' : regles + explication de la visualisation."""
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((8, 10, 14, 225))
        self.screen.blit(overlay, (0, 0))

        card = self.help_card
        pygame.draw.rect(self.screen, PANEL_BG, card, border_radius=14)
        pygame.draw.rect(self.screen, GRID, card, 2, border_radius=14)

        x = card.x + 32
        y = card.y + 22
        self.screen.blit(self.font_help_title.render("Comment jouer ?", True,
                                                     WHITE), (x, y))
        y += 48

        lines = [
            (WHITE, "But : aligner 3 symboles avant l'IA. Vous etes X, l'IA est O."),
            (GREY,  "Cliquez sur une case vide pour jouer. L'IA (O) repond seule"),
            (GREY,  "et elle est imbattable : au mieux, vous faites match nul."),
            (None,  ""),
            (GOOD,  "Comprendre le raisonnement de l'IA"),
            (GREY,  "A son tour, l'IA ecrit sur chaque case le score du coup :"),
        ]
        for color, text in lines:
            if text:
                self.screen.blit(self.font_small.render(text, True, color), (x, y))
            y += 24

        # legende des couleurs 
        legend = [(GOOD, "+  ce coup fait gagner l'IA"),
                  (NEUTRAL, "0  ce coup mene au match nul"),
                  (BAD, "-  ce coup fait perdre l'IA")]
        for col, text in legend:
            pygame.draw.rect(self.screen, col, (x + 6, y + 3, 14, 14),
                             border_radius=3)
            self.screen.blit(self.font_small.render(text, True, WHITE),
                             (x + 30, y))
            y += 24
        y += 4

        more = [
            (GREY, "Le panneau de droite compte les etats explores et les"),
            (GREY, "branches coupees par l'elagage Alpha-Beta."),
            (None, ""),
            (GOOD, "Boutons"),
            (GREY, "Nouvelle partie / IA commence : (re)lancer une partie."),
            (GREY, "Scores ON-OFF : afficher les scores. Alpha-Beta ON-OFF :"),
            (GREY, "activer/desactiver l'elagage (comparez les etats explores)."),
        ]
        for color, text in more:
            if text:
                self.screen.blit(self.font_small.render(text, True, color), (x, y))
            y += 24

        #  libelle 
        started = any(c != EMPTY for c in self.board) or self.game_over
        self.btn_help_close.label = "Fermer" if started else "Commencer a jouer"
        self.btn_help_close.draw(self.screen, self.font)

    # ######## CODE IA (Claude - Anthropic) #########
    def _wrap(self, text, max_w, font):
        """Coupe une chaine en plusieurs lignes selon la largeur dispo.

        Fonction utilitaire d'affichage (retour a la ligne du texte du
        panneau lateral) generée avec l'aide de l'IA. 
        """
        words = text.split(" ")
        lines, cur = [], ""
        for w in words:
            test = (cur + " " + w).strip()
            if font.size(test)[0] <= max_w:
                cur = test
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        return lines or [""]
    # ###############################################

    #  boucle principale 
    def handle_click(self, pos):
        # Menu d'aide ouvert 
        if self.show_help:
            if self.btn_help_close.clicked(pos):
                self.show_help = False
            return
        if self.btn_help.clicked(pos):
            self.show_help = True
            return
        if self.btn_new.clicked(pos):
            self.reset(ai_first=False)
            return
        if self.btn_scores.clicked(pos):
            self.show_scores = not self.show_scores
            return
        if self.btn_prune.clicked(pos):
            self.use_pruning = not self.use_pruning
            return
        if self.btn_ai_first.clicked(pos):
            self.reset(ai_first=True)
            return
        # clic sur la grille 
        if (not self.game_over and self.current == HUMAN
                and pos[0] < BOARD_SIZE and pos[1] < BOARD_SIZE):
            col = pos[0] // CELL
            row = pos[1] // CELL
            idx = row * 3 + col
            if self.board[idx] == EMPTY:
                self.decision = None   
                self.play(idx, HUMAN)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.handle_click(event.pos)

            if not self.show_help and not self.game_over and self.current == AI:
                self.render()
                pygame.display.flip()
                pygame.time.wait(250)
                self.ai_turn()

            self.render()
            if self.show_help:
                self._draw_help()
            pygame.display.flip()
            self.clock.tick(FPS)


if __name__ == "__main__":
    Game().run()
