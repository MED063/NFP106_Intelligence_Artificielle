"""
test_algo.py


Tests unitaires  de l'algo du jeu et de l'algorithme MinMax
avec elagage Alpha-Beta.

lancement :
    pytest -v
"""

import algo
from algo import (
    EMPTY, PLAYER_X, PLAYER_O,
    new_board, winner, winning_line, is_full, is_terminal,
    available_moves, other_player, minimax, best_move, SearchStats,
)



# Logique de base du plateau

def test_new_board_is_empty():
    board = new_board()
    assert board == [EMPTY] * 9
    assert available_moves(board) == list(range(9))


def test_winner_detects_row():
    board = [
        "X", "X", "X",
        " ", "O", " ",
        "O", " ", " ",
    ]
    assert winner(board) == PLAYER_X
    assert winning_line(board) == (0, 1, 2)


# ######## CODE IA (Claude - Anthropic) #########
# Ces DEUX tests de routine (detection d'une victoire en colonne et en
# diagonale, puis cas du match nul sur plateau plein) ont ete generes avec
# l'aide de l'IA. Ils portent sur des fonctions utilitaires simples, sans
# rapport avec l'algorithme MinMax lui-meme. J'ai relu chaque assertion et
# verifie les plateaux de test a la main.
# Les tests de MinMax / Alpha-Beta (sections suivantes) sont mon travail.
def test_winner_detects_column_and_diagonal():
    col = [
        "O", "X", " ",
        "O", "X", " ",
        "O", " ", " ",
    ]
    assert winner(col) == PLAYER_O
    diag = [
        "X", "O", " ",
        "O", "X", " ",
        " ", " ", "X",
    ]
    assert winner(diag) == PLAYER_X
    assert winning_line(diag) == (0, 4, 8)


def test_no_winner_returns_none():
    board = [
        "X", "O", "X",
        "X", "O", "O",
        "O", "X", "X",
    ]
    assert winner(board) is None
    assert is_full(board) is True
    assert is_terminal(board) is True
# ###############################################


def test_other_player():
    assert other_player(PLAYER_X) == PLAYER_O
    assert other_player(PLAYER_O) == PLAYER_X



# MinMax : coups optimaux

def test_ai_takes_immediate_win():
    # O peut gagner en jouant en case 2 (ligne 0-1-2).
    board = [
        "O", "O", " ",
        "X", "X", " ",
        " ", " ", " ",
    ]
    decision = best_move(board, PLAYER_O)
    assert decision.move == 2
    assert decision.move_scores[2] > 0


def test_ai_blocks_opponent_win():
    # X menace de gagner en case 2 ; O doit bloquer en 2.
    board = [
        "X", "X", " ",
        "O", " ", " ",
        " ", " ", " ",
    ]
    decision = best_move(board, PLAYER_O)
    assert decision.move == 2


def test_ai_prefers_faster_win():
    # O gagne immediatement en 6 (colonne 0-3-6) plutot que differer.
    board = [
        "O", "X", "X",
        "O", "X", " ",
        " ", " ", " ",
    ]
    decision = best_move(board, PLAYER_O)
    assert decision.move == 6
    assert decision.move_scores[6] > 0


def test_optimal_first_move_never_loses():
    # Depuis un plateau vide, l'IA optimale ne peut, au pire, que faire nul.
    board = new_board()
    decision = best_move(board, PLAYER_X)
    assert decision.move_scores[decision.move] >= 0



# Equivalence MinMax pur vs Alpha-Beta + efficacite de l'elagage
def test_pruning_gives_same_value_as_plain_minmax():

    positions = [
        new_board(),
        ["X", " ", " ", " ", "O", " ", " ", " ", " "],
        ["X", "O", "X", " ", "O", " ", " ", " ", " "],
        ["O", " ", " ", " ", "X", " ", " ", " ", " "],
    ]
    for board in positions:
        to_move = PLAYER_X if board.count("X") == board.count("O") else PLAYER_O
        v_plain = minimax(list(board), to_move, to_move,
                          use_pruning=False)
        v_prune = minimax(list(board), to_move, to_move,
                          use_pruning=True)
        assert v_plain == v_prune


def test_pruning_explores_fewer_nodes():
    board = new_board()
    plain = SearchStats()
    minimax(list(board), PLAYER_X, PLAYER_X, stats=plain, use_pruning=False)
    pruned = SearchStats()
    minimax(list(board), PLAYER_X, PLAYER_X, stats=pruned, use_pruning=True)
    # L'elagage doit  reduire le nombre de noeuds explores
    assert pruned.nodes_explored < plain.nodes_explored
    assert pruned.branches_pruned > 0


#
# L'ia  ne perd jamais contre un jeu parfait
# 
def test_ai_never_loses_against_itself():
    board = new_board()
    player = PLAYER_X
    while not is_terminal(board):
        move = best_move(board, player).move
        board[move] = player
        player = other_player(player)
    assert winner(board) is None  # nul


def test_displayed_scores_are_exact_with_pruning():
    """Les scores AFFICHES doivent etre exacts, pas de simples bornes.

    C'est essentiel pour la visualisation : un coup perdant doit afficher sa
    vraie valeur negative, meme lorsque l'elagage Alpha-Beta est actif.
    """
    positions = [
        (["X", " ", " ", " ", "O", " ", " ", " ", "X"], PLAYER_O),
        (["X", " ", " ", " ", "O", " ", " ", " ", " "], PLAYER_O),
        (new_board(), PLAYER_X),
    ]
    for board, player in positions:
        avec = best_move(list(board), player, use_pruning=True)
        sans = best_move(list(board), player, use_pruning=False)
        assert avec.move_scores == sans.move_scores
        assert avec.move == sans.move


def test_scores_cover_all_available_moves():
    board = [
        "X", " ", " ",
        " ", "O", " ",
        " ", " ", " ",
    ]
    decision = best_move(board, PLAYER_X)
    assert set(decision.move_scores.keys()) == set(available_moves(board))
