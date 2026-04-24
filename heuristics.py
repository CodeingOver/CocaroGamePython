from __future__ import annotations

from typing import Optional

from constants import AI_MARK, EMPTY, HUMAN_MARK, INF
from game import CaroGame, Move


def terminal_utility(game: CaroGame, depth: int, last_move: Optional[Move]) -> Optional[int]:
    winner = game.check_winner(last_move)
    if winner == AI_MARK:
        return INF - (1000 - depth)
    if winner == HUMAN_MARK:
        return -INF + (1000 - depth)
    if game.is_full():
        return 0
    return None


def line_score(ai_count: int, human_count: int, win_len: int) -> int:
    if ai_count > 0 and human_count > 0:
        return 0
    if ai_count == 0 and human_count == 0:
        return 0

    weights = [0] + [10**i for i in range(1, win_len)] + [10**(win_len + 1)]
    if ai_count > 0:
        return weights[ai_count]
    return -int(weights[human_count] * 1.15)


def evaluate_board(game: CaroGame) -> int:
    winner = game.check_winner()
    if winner == AI_MARK:
        return INF // 2
    if winner == HUMAN_MARK:
        return -INF // 2

    size = game.size
    win_len = game.win_len
    board = game.board
    score = 0

    for r in range(size):
        for c in range(size - win_len + 1):
            window = [board[r][c + k] for k in range(win_len)]
            score += line_score(window.count(AI_MARK), window.count(HUMAN_MARK), win_len)

    for c in range(size):
        for r in range(size - win_len + 1):
            window = [board[r + k][c] for k in range(win_len)]
            score += line_score(window.count(AI_MARK), window.count(HUMAN_MARK), win_len)

    for r in range(size - win_len + 1):
        for c in range(size - win_len + 1):
            window = [board[r + k][c + k] for k in range(win_len)]
            score += line_score(window.count(AI_MARK), window.count(HUMAN_MARK), win_len)

    for r in range(size - win_len + 1):
        for c in range(win_len - 1, size):
            window = [board[r + k][c - k] for k in range(win_len)]
            score += line_score(window.count(AI_MARK), window.count(HUMAN_MARK), win_len)

    center = (size - 1) / 2.0
    center_bias = 0
    for r in range(size):
        for c in range(size):
            if board[r][c] == EMPTY:
                continue
            value = int(size - (abs(r - center) + abs(c - center)))
            if board[r][c] == AI_MARK:
                center_bias += value
            else:
                center_bias -= value

    return score + center_bias
