from __future__ import annotations

from typing import Optional

from ai import ai_best_move
from constants import AI_MARK, HUMAN_MARK, MAX_BOARD_SIZE, MIN_BOARD_SIZE
from game import CaroGame, Move


def read_int(prompt: str, default: int, min_value: int, max_value: Optional[int] = None) -> int:
    # Đọc một số nguyên có kiểm tra miền giá trị từ terminal.

    while True:
        raw = input(f"{prompt} [{default}]: ").strip()
        if not raw:
            return default
        try:
            value = int(raw)
            if value < min_value:
                raise ValueError
            if max_value is not None and value > max_value:
                raise ValueError
            return value
        except ValueError:
            if max_value is None:
                print(f"Vui lòng nhập số nguyên >= {min_value}.")
            else:
                print(f"Vui lòng nhập số nguyên trong khoảng [{min_value}, {max_value}].")


def ask_human_move(game: CaroGame) -> Move:
    # Đọc nước đi của người chơi theo định dạng hàng cột (1-based).

    while True:
        raw = input("Nhập nước đi (hàng cột), ví dụ: 3 4: ").strip().split()
        if len(raw) != 2:
            print("Định dạng không hợp lệ. Hãy nhập 2 số: hàng cột.")
            continue

        try:
            row = int(raw[0]) - 1
            col = int(raw[1]) - 1
        except ValueError:
            print("Hàng/cột phải là số nguyên.")
            continue

        move = Move(row, col)
        if not game.is_valid_move(move):
            print("Nước đi không hợp lệ hoặc ô đã được đánh. Thử lại.")
            continue
        return move


def suggested_depth(size: int) -> int:
    # Gợi ý độ sâu mặc định theo kích thước bàn cờ.

    if size <= 3:
        return 9
    if size <= 5:
        return 5
    if size <= 8:
        return 4
    return 3


def suggested_candidate_limit(size: int) -> int:
    # Gợi ý số ứng viên mỗi lớp để cân bằng chất lượng và tốc độ.

    if size <= 5:
        return size * size
    if size <= 8:
        return 14
    return 12


def main() -> None:
    # Điểm vào chế độ CLI: nhận cấu hình, chạy vòng lặp ván đấu và điều phối lượt chơi.

    print("=== AI CỜ CARO (GBFS + MINIMAX + ALPHA-BETA + HEURISTIC) ===")
    size = read_int(
        f"Kích thước bàn cờ (n x n, {MIN_BOARD_SIZE}-{MAX_BOARD_SIZE})",
        default=10,
        min_value=MIN_BOARD_SIZE,
        max_value=MAX_BOARD_SIZE,
    )
    win_len_default = 3 if size <= 3 else 5
    win_len = read_int(
        "Số quân liên tiếp để thắng",
        default=win_len_default,
        min_value=MIN_BOARD_SIZE,
        max_value=size,
    )
    depth = read_int(
        "Độ sâu tìm kiếm cho AI",
        default=suggested_depth(size),
        min_value=1,
        max_value=10,
    )
    max_candidates = read_int(
        "Số nước ứng viên tối đa mỗi lớp",
        default=suggested_candidate_limit(size),
        min_value=4,
        max_value=size * size,
    )
    max_time_ms = read_int(
        "Giới hạn thời gian mỗi nước AI (ms)",
        default=300,
        min_value=50,
        max_value=5000,
    )

    first = input("Bạn muốn đi trước? (y/n) [y]: ").strip().lower()
    human_turn = first != "n"

    game = CaroGame(size=size, win_len=win_len)
    last_move: Optional[Move] = None

    while True:
        print("\nBàn cờ hiện tại:")
        game.print_board()

        winner = game.check_winner(last_move)
        if winner is not None or game.is_full():
            if winner == AI_MARK:
                print("\nAI thắng.")
            elif winner == HUMAN_MARK:
                print("\nBạn thắng.")
            else:
                print("\nHòa.")
            break

        if human_turn:
            move = ask_human_move(game)
            game.make_move(move, HUMAN_MARK)
            last_move = move
        else:
            print("\nAI đang tính toán...")
            move = ai_best_move(
                game,
                depth=depth,
                max_candidates=max_candidates,
                max_time_ms=max_time_ms,
            )
            game.make_move(move, AI_MARK)
            last_move = move
            print(f"AI đánh tại: hàng {move.row + 1}, cột {move.col + 1}")

        human_turn = not human_turn
