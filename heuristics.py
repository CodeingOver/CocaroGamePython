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


def line_score(ai_count: int, human_count: int, win_len: int) -> int:
    # Chấm điểm một cửa sổ win_len ô theo nguyên tắc tấn công/phòng thủ.
    # Nếu hai bên cùng xuất hiện trong cửa sổ thì cửa sổ đó bị khóa, không có giá trị mở rộng.

    if ai_count > 0 and human_count > 0:
        return 0
    if ai_count == 0 and human_count == 0:
        return 0

    # Trọng số tăng theo cấp số mũ để chuỗi dài hơn được ưu tiên vượt trội.
    weights = [0] + [10**i for i in range(1, win_len)] + [10**(win_len + 1)]
    if ai_count > 0:
        return weights[ai_count]
    # Phạt phía đối thủ nhỉnh hơn một chút để AI có xu hướng phòng thủ an toàn.
    return -int(weights[human_count] * 1.15)


def evaluate_board(game: CaroGame) -> int:
    # Đánh giá toàn cục một trạng thái bàn cờ khi chưa chạm điều kiện kết thúc.
    # Hàm quét 4 hướng cơ bản và cộng thêm thiên vị trung tâm để ổn định thế khai cuộc.

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

    # Quét theo hàng ngang.
    for r in range(size):
        for c in range(size - win_len + 1):
            window = [board[r][c + k] for k in range(win_len)]
            score += line_score(window.count(AI_MARK), window.count(HUMAN_MARK), win_len)

    # Quét theo cột dọc.
    for c in range(size):
        for r in range(size - win_len + 1):
            window = [board[r + k][c] for k in range(win_len)]
            score += line_score(window.count(AI_MARK), window.count(HUMAN_MARK), win_len)

    # Quét chéo chính (từ trái trên xuống phải dưới).
    for r in range(size - win_len + 1):
        for c in range(size - win_len + 1):
            window = [board[r + k][c + k] for k in range(win_len)]
            score += line_score(window.count(AI_MARK), window.count(HUMAN_MARK), win_len)

    # Quét chéo phụ (từ phải trên xuống trái dưới).
    for r in range(size - win_len + 1):
        for c in range(win_len - 1, size):
            window = [board[r + k][c - k] for k in range(win_len)]
            score += line_score(window.count(AI_MARK), window.count(HUMAN_MARK), win_len)

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
