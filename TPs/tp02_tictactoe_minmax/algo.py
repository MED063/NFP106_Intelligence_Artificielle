"""
algo.py


logique du jeu Tic-Tac-Toe  et implementation de
l'algorithme MinMax avec elagage Alpha-Beta.


Representation du plateau

Le plateau est une liste de 9 cases indexees de 0 a 8 :

Chaque case vaut :
    'X'  -> pion du joueur X
    'O'  -> pion du joueur O
    ' '  -> case vide
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

EMPTY = " "
PLAYER_X = "X"
PLAYER_O = "O"

#les 8 alignements gagnants (3 lignes, 3 colonnes, 2 diagonales).
WIN_LINES = (
    (0, 1, 2), (3, 4, 5), (6, 7, 8),   # lignes
    (0, 3, 6), (1, 4, 7), (2, 5, 8),   # colonnes
    (0, 4, 8), (2, 4, 6),              # diagonales
)


# fonctions utilitaires sur le plateau
def new_board() -> list[str]:
    return [EMPTY] * 9


def available_moves(board: list[str]) -> list[int]:
    return [i for i, cell in enumerate(board) if cell == EMPTY]


def other_player(player: str) -> str:
    return PLAYER_O if player == PLAYER_X else PLAYER_X


def winner(board: list[str]) -> Optional[str]:
    """
    retourne 'X' ou 'O' si un joueur a aligne 3 pions, sinon None.
    """
    for a, b, c in WIN_LINES:
        if board[a] != EMPTY and board[a] == board[b] == board[c]:
            return board[a]
    return None


def winning_line(board: list[str]) -> Optional[tuple[int, int, int]]:
    """retourne le triplet d'indices gagnant ."""
    for line in WIN_LINES:
        a, b, c = line
        if board[a] != EMPTY and board[a] == board[b] == board[c]:
            return line
    return None


def is_full(board: list[str]) -> bool:
    """vrai si le plateau ne contient plus de case vide."""
    return EMPTY not in board


def is_terminal(board: list[str]) -> bool:
    """vrai si la partie est finie (victoire ou match nul)."""
    return winner(board) is not None or is_full(board)


# statistiques d'exploration de l'arbre

@dataclass
class SearchStats:
    """
    compteurs remplis pendant la recherche MinMax. Ils servent a
    VISUALISER le fonctionnement de l'algorithme dans l'interface.
    """
    nodes_explored: int = 0
    branches_pruned: int = 0
    max_depth: int = 0

    def reset(self) -> None:
        self.nodes_explored = 0
        self.branches_pruned = 0
        self.max_depth = 0



# Fonction d'evaluation d'un etat terminal

def evaluate(board: list[str], ai_player: str, depth: int) -> int:
    """
    score d'un etat terminal du point de vue de l'IA (ai_player).

    on soustrait / ajoute la profondeur pour que l'IA prefere gagner
    le PLUS VITE possible et perdre LE PLUS TARD possible 
    """
    win = winner(board)
    if win == ai_player:
        return 10 - depth
    if win == other_player(ai_player):
        return depth - 10
    return 0



# MinMax avec elagage Alpha-Beta
def minimax(
    board: list[str],
    current_player: str,
    ai_player: str,
    depth: int = 0,
    alpha: float = float("-inf"),
    beta: float = float("inf"),
    stats: Optional[SearchStats] = None,
    use_pruning: bool = True,
) -> int:
    """
    Retourne le score MinMax du plateau  poiur ai_player

     noeud MAX quand c'est au tour de l'IA (elle maximise son score),
    et MIN quand c'est au tour de l'adversaire (il minimise le score de l'IA).
    """
    if stats is not None:
        stats.nodes_explored += 1
        stats.max_depth = max(stats.max_depth, depth)

    # cas de base : etat terminal : on retourne son evaluation.
    if is_terminal(board):
        return evaluate(board, ai_player, depth)

    if current_player == ai_player:
        #  Noeud MAX   
        best = float("-inf")
        for move in available_moves(board):
            board[move] = current_player
            score = minimax(
                board, other_player(current_player), ai_player,
                depth + 1, alpha, beta, stats, use_pruning,
            )
            board[move] = EMPTY  # annulation du coup (backtracking)
            best = max(best, score)
            alpha = max(alpha, best)
            if use_pruning and beta <= alpha:
                # Coupure Beta : l'adversaire ne laissera jamais l'IA
                # atteindre cette branche -> inutile de l'explorer.
                if stats is not None:
                    stats.branches_pruned += 1
                break
        return int(best)
    else:
        # Noeud MIN 
        best = float("inf")
        for move in available_moves(board):
            board[move] = current_player
            score = minimax(
                board, other_player(current_player), ai_player,
                depth + 1, alpha, beta, stats, use_pruning,
            )
            board[move] = EMPTY
            best = min(best, score)
            beta = min(beta, best)
            if use_pruning and beta <= alpha:
                # Coupure Alpha : l'IA a deja mieux ailleurs.
                if stats is not None:
                    stats.branches_pruned += 1
                break
        return int(best)


@dataclass
class Decision:
    """resultat complet d'une reflexion de l'IA pour l'affichge."""
    move: int                                   # coup choisi (0..8)
    move_scores: dict[int, int] = field(default_factory=dict)  # score par coup
    stats: SearchStats = field(default_factory=SearchStats)


def best_move(
    board: list[str],
    ai_player: str,
    use_pruning: bool = True,
) -> Decision:
    """
    calcule le meilleur coup pour `ai_player` sur le plateau courant.
    """
    stats = SearchStats()
    move_scores: dict[int, int] = {}
    best_score = float("-inf")
    chosen: Optional[int] = None

    for move in available_moves(board):
        board[move] = ai_player
        score = minimax(
            board, other_player(ai_player), ai_player,
            depth=1, alpha=float("-inf"), beta=float("inf"), stats=stats,
            use_pruning=use_pruning,
        )
        board[move] = EMPTY
        move_scores[move] = score
        if score > best_score:
            best_score = score
            chosen = move

    return Decision(move=chosen, move_scores=move_scores, stats=stats)


def explain_decision(decision: Decision, ai_player: str) -> list[str]:
    """
     petit texte explicatif (liste de lignes) decrivant la
    decision de l'IA 
    """
    best_score = decision.move_scores[decision.move]
    lines = [
        f"L'IA ({ai_player}) a analyse {decision.stats.nodes_explored} etats",
        f"et coupe {decision.stats.branches_pruned} branches (Alpha-Beta).",
        f"Profondeur max exploree : {decision.stats.max_depth} coups.",
        "",
    ]
    if best_score > 0:
        lines.append(f"-> Coup {decision.move} : victoire forcee (score {best_score}).")
    elif best_score == 0:
        lines.append(f"-> Coup {decision.move} : match nul garanti (score 0).")
    else:
        lines.append(f"-> Coup {decision.move} : defaite retardee (score {best_score}).")
    lines.append("Interpretation des scores par case :")
    lines.append("  >0 = l'IA gagne, 0 = nul, <0 = l'IA perd.")
    return lines
