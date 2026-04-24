from __future__ import annotations

from time import perf_counter
from typing import Dict, List, Optional, Sequence, Tuple

from constants import AI_MARK, HUMAN_MARK, INF
from game import CaroGame, Move
from heuristics import evaluate_board, terminal_utility


class SearchTimeout(Exception):
    # Ngoại lệ nội bộ dùng để dừng tìm kiếm khi hết ngân sách thời gian.
    pass


# Bộ nhớ đệm nhanh theo trạng thái bàn cờ hiện tại.
# Mục tiêu là tránh lặp lại một lượt tìm kiếm khi người chơi quay lại cùng trạng thái.
STATE_BEST_MOVE_CACHE: Dict[Tuple[str, int, int], Move] = {}


def _greedy_move_score(
    game: CaroGame,
    move: Move,
    player: str,
    opponent: str,
) -> int:
    # Tính điểm tham lam cục bộ cho một nước đi dùng ở tầng GBFS.
    # Quy tắc chấm điểm ưu tiên:
    # 1) Nước đi thắng ngay luôn được điểm rất cao.
    # 2) Các trạng thái có lợi theo heuristic được ưu tiên hơn.
    # 3) Nếu nước đi đồng thời chặn một mối đe dọa tức thì của đối thủ thì cộng thưởng.

    # GBFS dùng điểm heuristic cục bộ để ưu tiên nhánh hứa hẹn nhất trước.
    game.make_move(move, player)
    try:
        if game.check_winner(move) == player:
            return INF // 4
        score = evaluate_board(game)
        if player == HUMAN_MARK:
            score = -score

        # Ưu tiên thêm nếu nước đi hiện tại đồng thời chặn một nước thắng trực tiếp của đối thủ.
        game.make_move(move, opponent)
        try:
            if game.check_winner(move) == opponent:
                score += INF // 8
        finally:
            game.undo_move(move)
        return score
    finally:
        game.undo_move(move)


def gbfs_rank_moves(
    game: CaroGame,
    moves: Sequence[Move],
    player: str,
    opponent: str,
    maximizing: bool,
) -> List[Move]:
    # Sắp xếp danh sách nước đi theo điểm tham lam để giảm số nhánh cần duyệt sâu.

    scored: List[Tuple[int, Move]] = [(_greedy_move_score(game, move, player, opponent), move) for move in moves]

    scored.sort(key=lambda x: x[0], reverse=maximizing)
    return [mv for _, mv in scored]


def _is_immediate_winning_move(game: CaroGame, move: Move, player: str) -> bool:
    # Kiểm tra nhanh nước đi có thắng ngay trong 1 ply hay không.
    game.make_move(move, player)
    try:
        return game.check_winner(move) == player
    finally:
        game.undo_move(move)


def minimax(
    game: CaroGame,
    depth: int,
    alpha: int,
    beta: int,
    maximizing: bool,
    last_move: Optional[Move],
    transposition: Dict[Tuple[str, bool, int], int],
    max_candidates: int,
    deadline: Optional[float],
) -> int:
    # Minimax có cắt tỉa Alpha-Beta và giới hạn thời gian theo deadline.
    # Hàm dùng thêm transposition table để tái sử dụng kết quả ở các trạng thái lặp lại.

    if deadline is not None and perf_counter() >= deadline:
        raise SearchTimeout()

    # Cắt sớm ở trạng thái kết thúc hoặc khi đã chạm độ sâu giới hạn.
    terminal_value = terminal_utility(game, depth, last_move)
    if terminal_value is not None:
        return terminal_value
    if depth == 0:
        return evaluate_board(game)

    # Bảng chuyển vị cần gắn cả độ sâu để tránh tái dùng kết quả tìm kiếm nông cho ngữ cảnh sâu.
    key = (game.serialize(), maximizing, depth)
    cached = transposition.get(key)
    if cached is not None:
        return cached

    # Phân vai theo lượt đi hiện tại để dùng cùng một thân hàm cho cả hai phía.
    if maximizing:
        value = -INF
        player = AI_MARK
        opponent = HUMAN_MARK
    else:
        value = INF
        player = HUMAN_MARK
        opponent = AI_MARK

    moves = game.get_candidate_moves(radius=1)
    # GBFS chỉ giữ lại và sắp xếp những nước hứa hẹn nhất trước khi Minimax duyệt sâu.
    moves = gbfs_rank_moves(game, moves, player, opponent, maximizing)
    if len(moves) > max_candidates:
        moves = moves[:max_candidates]

    # Gắn biến cục bộ giúp giảm lookup attribute trong vòng lặp sâu.
    make_move = game.make_move
    undo_move = game.undo_move

    if maximizing:
        # Nhánh MAX: AI cố gắng đẩy điểm lên cao nhất.
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
        # Nhánh MIN: giả lập đối thủ luôn chọn phương án bất lợi nhất cho AI.
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

    transposition[key] = value
    return value


def ai_best_move(
    game: CaroGame,
    depth: int,
    max_candidates: int,
    max_time_ms: Optional[int] = None,
) -> Move:
    # Chọn nước đi tốt nhất cho AI bằng chiến lược GBFS + Minimax theo iterative deepening.
    # Quy trình:
    # 1) Lấy danh sách ứng viên gần vùng đã có quân.
    # 2) Dùng GBFS sắp xếp/lọc ứng viên.
    # 3) Duyệt sâu dần từ 1..depth, dừng sớm nếu hết thời gian.
    # 4) Giữ lại phương án tốt nhất đã hoàn thành ở độ sâu gần nhất.

    state_key = (game.serialize(), depth, max_candidates)
    cached_move = STATE_BEST_MOVE_CACHE.get(state_key)
    if cached_move is not None and game.is_valid_move(cached_move):
        # Cache theo trạng thái + tham số tìm kiếm giúp tránh trả về nước cũ của cấu hình khác.
        return cached_move

    candidates = game.get_candidate_moves(radius=1)

    # Tactical pre-check: nếu có nước thắng ngay thì đi luôn, không cần chờ minimax.
    winning_moves = [mv for mv in candidates if _is_immediate_winning_move(game, mv, AI_MARK)]
    if winning_moves:
        best_move = gbfs_rank_moves(game, winning_moves, AI_MARK, HUMAN_MARK, maximizing=True)[0]
        STATE_BEST_MOVE_CACHE[state_key] = best_move
        return best_move

    # Tactical pre-check: nếu đối thủ có nước thắng ngay ở lượt kế, ưu tiên chặn trước khi tìm sâu.
    blocking_moves = [mv for mv in candidates if _is_immediate_winning_move(game, mv, HUMAN_MARK)]
    if blocking_moves:
        best_move = gbfs_rank_moves(game, blocking_moves, AI_MARK, HUMAN_MARK, maximizing=True)[0]
        STATE_BEST_MOVE_CACHE[state_key] = best_move
        return best_move

    # Tầng GBFS: chấm điểm toàn bộ nước ứng viên rồi chỉ đưa nhóm tốt nhất vào vòng Minimax.
    candidates = gbfs_rank_moves(game, candidates, AI_MARK, HUMAN_MARK, maximizing=True)
    if len(candidates) > max_candidates:
        candidates = candidates[:max_candidates]

    best_move = candidates[0]
    deadline = None if max_time_ms is None else perf_counter() + (max_time_ms / 1000.0)
    cache: Dict[Tuple[str, bool, int], int] = {}

    for current_depth in range(1, depth + 1):
        # Re-rank lại theo từng lớp sâu để tránh lock-in vào một hướng từ vòng lặp trước.
        search_candidates = gbfs_rank_moves(game, candidates, AI_MARK, HUMAN_MARK, maximizing=True)
        if len(search_candidates) > max_candidates:
            search_candidates = search_candidates[:max_candidates]

        best_score = -INF
        depth_best_move = best_move

        try:
            for move in search_candidates:
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
            # Khi timeout, giữ kết quả của độ sâu trước đó thay vì trả về ngẫu nhiên.
            break

        best_move = depth_best_move

    STATE_BEST_MOVE_CACHE[state_key] = best_move

    return best_move
