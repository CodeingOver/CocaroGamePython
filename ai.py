from __future__ import annotations

from dataclasses import dataclass, field
from time import perf_counter
from typing import Dict, List, Optional, Sequence, Tuple

from constants import AI_MARK, HUMAN_MARK, INF
from game import CaroGame, Move
from heuristics import evaluate_board, terminal_utility


class SearchTimeout(Exception):
    # Ngoại lệ nội bộ dùng để dừng tìm kiếm khi hết ngân sách thời gian.
    pass


@dataclass
class SearchStats:
    # Lưu trữ thống kê một lượt tìm kiếm để so sánh hiệu quả giữa các chế độ thuật toán.
    nodes_visited: int = 0
    cutoffs: int = 0        # Số lần Alpha-Beta cắt tỉa thành công
    depth_reached: int = 0  # Độ sâu tìm kiếm thực sự đạt được (Iterative Deepening)
    elapsed_ms: float = 0.0


# Bộ nhớ đệm nhanh theo trạng thái bàn cờ hiện tại.
# Mục tiêu là tránh lặp lại một lượt tìm kiếm khi người chơi quay lại cùng trạng thái.
STATE_BEST_MOVE_CACHE: Dict[Tuple[str, int, int, int, bool, bool], Move] = {}


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
            # Cùng một sự kiện thắng ngay nhưng dấu điểm phải phụ thuộc phía đang xét.
            return INF // 4 if player == AI_MARK else -(INF // 4)

        # score luôn được giữ theo góc nhìn AI để ordering MIN/MAX nhất quán.
        score = evaluate_board(game)

        # Ưu tiên thêm nếu nước đi hiện tại đồng thời chặn một nước thắng trực tiếp của đối thủ.
        game.make_move(move, opponent)
        try:
            if game.check_winner(move) == opponent:
                # Chặn thắng ngay là tín hiệu chiến thuật rất mạnh trong GBFS local scoring.
                if player == AI_MARK:
                    score += INF // 8
                else:
                    score -= INF // 8
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
    deadline: Optional[float] = None,
) -> List[Move]:
    # Sắp xếp danh sách nước đi theo điểm tham lam để giảm số nhánh cần duyệt sâu.
    # Deadline check để tránh bị kẹt trong giai đoạn sắp xếp ở bàn cờ lớn.

    scored: List[Tuple[int, Move]] = []
    for move in moves:
        if deadline is not None and perf_counter() >= deadline:
            raise SearchTimeout()
        scored.append((_greedy_move_score(game, move, player, opponent), move))

    scored.sort(key=lambda x: x[0], reverse=maximizing)
    return [mv for _, mv in scored]


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
    stats: SearchStats,
    use_ab: bool = True,
    use_gbfs: bool = True,
) -> int:
    # Minimax có cắt tỉa Alpha-Beta và giới hạn thời gian theo deadline.
    # Hàm dùng thêm transposition table để tái sử dụng kết quả ở các trạng thái lặp lại.
    # use_ab: bật/tắt cắt tỉa Alpha-Beta.
    # use_gbfs: bật/tắt sắp xếp nước đi bằng GBFS.

    stats.nodes_visited += 1

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
    # GBFS: chỉ sắp xếp ở các tầng nông (depth >= 2) để tối ưu Alpha-Beta.
    if use_gbfs and depth >= 2:
        moves = gbfs_rank_moves(game, moves, player, opponent, maximizing, deadline)

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
                    stats,
                    use_ab,
                    use_gbfs,
                )
            finally:
                undo_move(move)
            value = max(value, score)
            if use_ab:
                alpha = max(alpha, value)
                if beta <= alpha:
                    stats.cutoffs += 1
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
                    stats,
                    use_ab,
                    use_gbfs,
                )
            finally:
                undo_move(move)
            value = min(value, score)
            if use_ab:
                beta = min(beta, value)
                if beta <= alpha:
                    stats.cutoffs += 1
                    break

    transposition[key] = value
    return value


def ai_best_move(
    game: CaroGame,
    depth: int,
    max_candidates: int,
    max_time_ms: Optional[int] = None,
    use_ab: bool = True,
    use_gbfs: bool = True,
) -> Tuple[Move, SearchStats]:
    # Chọn nước đi tốt nhất cho AI bằng chiến lược GBFS + Minimax theo iterative deepening.
    # use_ab: bật/tắt cắt tỉa Alpha-Beta.
    # use_gbfs: bật/tắt sắp xếp nước đi bằng GBFS.
    # Trả về: (nước đi tốt nhất, thống kê tìm kiếm).

    start_time = perf_counter()

    # Khóa cache gắn thêm các cờ để tránh dùng lại kết quả của cấu hình khác.
    state_key = (game.serialize(), depth, max_candidates, max_time_ms or -1, use_ab, use_gbfs)
    cached_move = STATE_BEST_MOVE_CACHE.get(state_key)
    if cached_move is not None and game.is_valid_move(cached_move):
        dummy_stats = SearchStats(elapsed_ms=(perf_counter() - start_time) * 1000.0)
        return cached_move, dummy_stats

    stats = SearchStats()
    candidates = game.get_candidate_moves(radius=1)
    deadline = None if max_time_ms is None else perf_counter() + (max_time_ms / 1000.0)

    # Tầng GBFS: chấm điểm toàn bộ nước ứng viên rồi chỉ đưa nhóm tốt nhất vào vòng Minimax.
    if use_gbfs:
        try:
            candidates = gbfs_rank_moves(game, candidates, AI_MARK, HUMAN_MARK, maximizing=True, deadline=deadline)
        except SearchTimeout:
            candidates = list(candidates)
    if len(candidates) > max_candidates:
        candidates = candidates[:max_candidates]

    best_move = candidates[0]
    cache: Dict[Tuple[str, bool, int], int] = {}

    for current_depth in range(1, depth + 1):
        # Re-rank lại theo từng lớp sâu để tránh lock-in vào một hướng từ vòng lặp trước.
        if use_gbfs:
            try:
                search_candidates = gbfs_rank_moves(game, candidates, AI_MARK, HUMAN_MARK, maximizing=True, deadline=deadline)
            except SearchTimeout:
                break
        else:
            search_candidates = list(candidates)

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
                        stats,
                        use_ab,
                        use_gbfs,
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
        stats.depth_reached = current_depth

    stats.elapsed_ms = (perf_counter() - start_time) * 1000.0
    STATE_BEST_MOVE_CACHE[state_key] = best_move

    return best_move, stats
