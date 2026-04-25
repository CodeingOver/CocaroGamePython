from __future__ import annotations

from typing import Optional

from constants import AI_MARK, EMPTY, HUMAN_MARK, INF
from game import CaroGame, Move


def terminal_utility(game: CaroGame, depth: int, last_move: Optional[Move]) -> Optional[int]:
    # Định giá trạng thái kết thúc để Minimax ưu tiên thắng nhanh, thua chậm.

    winner = game.check_winner(last_move)
    if winner == AI_MARK:
        return INF - (1000 - depth)
    if winner == HUMAN_MARK:
        return -INF + (1000 - depth)
    if game.is_full():
        return 0
    return None


def run_score(length: int, open_ends: int, win_len: int, ai_run: bool) -> int:
    # Chấm điểm một chuỗi liên tiếp có xét số đầu mở (open-end).
    # Mục tiêu: ưu tiên open-four/open-three vì đây là dạng thế cờ tạo áp lực chiến thuật mạnh.

    if length <= 0:
        return 0

    if length >= win_len:
        value = 10 ** (win_len + 2)
    else:
        base = 10**length
        if open_ends == 2:
            value = base * 3
        elif open_ends == 1:
            value = base
        else:
            value = max(1, base // 4)

        # open-four hai đầu mở là thế thắng sau 2 lượt nếu đối thủ không chặn tối ưu.
        if length == win_len - 1 and open_ends == 2:
            value *= 6
        # open-three hai đầu mở là mầm bẫy 2 nước quan trọng.
        elif length == win_len - 2 and open_ends == 2:
            value *= 3
        elif length == win_len - 1 and open_ends == 1:
            value *= 3

    if ai_run:
        return int(value)

    # Trừng phạt chuỗi của đối thủ mạnh hơn một chút để AI giữ phòng thủ chủ động.
    return -int(value * 1.2)


def evaluate_board(game: CaroGame) -> int:
    # Đánh giá toàn cục một trạng thái bàn cờ khi chưa chạm điều kiện kết thúc.
    # Hàm quét cụm liên tiếp theo 4 hướng và chấm điểm dựa trên open-end/open-four.

    # Trạng thái thắng/thua được ưu tiên tuyệt đối để Minimax không cần đọc sâu hơn.
    winner = game.check_winner()
    if winner == AI_MARK:
        return INF // 2
    if winner == HUMAN_MARK:
        return -INF // 2

    size = game.size
    win_len = game.win_len
    board = game.board
    score = 0

    directions = ((1, 0), (0, 1), (1, 1), (1, -1))

    # Quét theo cụm liên tiếp; mỗi cụm chỉ chấm đúng 1 lần bằng cách nhận diện điểm bắt đầu run.
    for r in range(size):
        for c in range(size):
            mark = board[r][c]
            if mark == EMPTY:
                continue

            for dr, dc in directions:
                prev_r, prev_c = r - dr, c - dc
                if 0 <= prev_r < size and 0 <= prev_c < size and board[prev_r][prev_c] == mark:
                    continue

                length = 0
                cur_r, cur_c = r, c
                while 0 <= cur_r < size and 0 <= cur_c < size and board[cur_r][cur_c] == mark:
                    length += 1
                    cur_r += dr
                    cur_c += dc

                open_ends = 0
                if 0 <= prev_r < size and 0 <= prev_c < size and board[prev_r][prev_c] == EMPTY:
                    open_ends += 1
                if 0 <= cur_r < size and 0 <= cur_c < size and board[cur_r][cur_c] == EMPTY:
                    open_ends += 1

                score += run_score(length, open_ends, win_len, ai_run=(mark == AI_MARK))

    # Hơi ưu tiên quân ở gần trung tâm để AI chơi chủ động hơn ở giai đoạn đầu ván.
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
