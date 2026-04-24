from __future__ import annotations

from time import perf_counter
from typing import Dict, List, Optional, Sequence, Tuple

from constants import AI_MARK, HUMAN_MARK, INF
from game import CaroGame, Move
from heuristics import evaluate_board, terminal_utility


class SearchTimeout(Exception):
    pass


# Lookup table: trang thai -> nuoc di tot nhat da tung tinh truoc do.
STATE_BEST_MOVE_CACHE: Dict[str, Move] = {}


def order_moves(
    game: CaroGame,
    moves: Sequence[Move],
    player: str,
    opponent: str,
    maximizing: bool,
) -> List[Move]:
    scored: List[Tuple[int, Move]] = []
    for move in moves:
        game.make_move(move, player)
        if game.check_winner(move) == player:
            move_score = INF // 4
        else:
            move_score = evaluate_board(game)
        game.undo_move(move)

        if player == HUMAN_MARK:
            move_score = -move_score

        game.make_move(move, opponent)
        if game.check_winner(move) == opponent:
            move_score += INF // 8
        game.undo_move(move)

        scored.append((move_score, move))

    scored.sort(key=lambda x: x[0], reverse=maximizing)
    return [mv for _, mv in scored]


def minimax(
    game: CaroGame,
    depth: int,
    alpha: int,
    beta: int,
    maximizing: bool,
    last_move: Optional[Move],
    transposition: Dict[Tuple[str, bool], Tuple[int, int]],
    max_candidates: int,
    deadline: Optional[float],
) -> int:
    if deadline is not None and perf_counter() >= deadline:
        raise SearchTimeout()

    terminal_value = terminal_utility(game, depth, last_move)
    if terminal_value is not None:
        return terminal_value
    if depth == 0:
        return evaluate_board(game)

    key = (game.serialize(), maximizing)
    cached = transposition.get(key)
    if cached is not None:
        cached_value, cached_depth = cached
        if cached_depth >= depth:
            return cached_value

    if maximizing:
        value = -INF
        player = AI_MARK
        opponent = HUMAN_MARK
    else:
        value = INF
        player = HUMAN_MARK
        opponent = AI_MARK

    moves = game.get_candidate_moves(radius=1)
    moves = order_moves(game, moves, player, opponent, maximizing)
    if len(moves) > max_candidates:
        moves = moves[:max_candidates]

    make_move = game.make_move
    undo_move = game.undo_move

    if maximizing:
        for move in moves:
            make_move(move, player)
            try:
                score = minimax(
                    game,
                    depth - 1,
                    alpha,
                    beta,
                    False,
                    move,
                    transposition,
                    max_candidates,
                    deadline,
                )
            finally:
                undo_move(move)
            value = max(value, score)
            alpha = max(alpha, value)
            if beta <= alpha:
                break
    else:
        for move in moves:
            make_move(move, player)
            try:
                score = minimax(
                    game,
                    depth - 1,
                    alpha,
                    beta,
                    True,
                    move,
                    transposition,
                    max_candidates,
                    deadline,
                )
            finally:
                undo_move(move)
            value = min(value, score)
            beta = min(beta, value)
            if beta <= alpha:
                break

    transposition[key] = (value, depth)
    return value


def ai_best_move(
    game: CaroGame,
    depth: int,
    max_candidates: int,
    max_time_ms: Optional[int] = None,
) -> Move:
    state_key = game.serialize()
    cached_move = STATE_BEST_MOVE_CACHE.get(state_key)
    if cached_move is not None and game.is_valid_move(cached_move):
        return cached_move

    candidates = game.get_candidate_moves(radius=1)
    candidates = order_moves(game, candidates, AI_MARK, HUMAN_MARK, maximizing=True)
    if len(candidates) > max_candidates:
        candidates = candidates[:max_candidates]

    best_move = candidates[0]
    deadline = None if max_time_ms is None else perf_counter() + (max_time_ms / 1000.0)
    cache: Dict[Tuple[str, bool], Tuple[int, int]] = {}

    for current_depth in range(1, depth + 1):
        if best_move in candidates:
            candidates = [best_move] + [mv for mv in candidates if mv != best_move]

        best_score = -INF
        depth_best_move = best_move

        try:
            for move in candidates:
                if deadline is not None and perf_counter() >= deadline:
                    raise SearchTimeout()

                game.make_move(move, AI_MARK)
                try:
                    score = minimax(
                        game,
                        current_depth - 1,
                        -INF,
                        INF,
                        False,
                        move,
                        cache,
                        max_candidates,
                        deadline,
                    )
                finally:
                    game.undo_move(move)

                if score > best_score:
                    best_score = score
                    depth_best_move = move
        except SearchTimeout:
            break

        best_move = depth_best_move

    STATE_BEST_MOVE_CACHE[state_key] = best_move

    return best_move
