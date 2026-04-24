from __future__ import annotations

from typing import Optional

from ai import ai_best_move
from constants import AI_MARK, HUMAN_MARK, MAX_BOARD_SIZE, MIN_BOARD_SIZE
from game import CaroGame, Move


def read_int(prompt: str, default: int, min_value: int, max_value: Optional[int] = None) -> int:
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
                print(f"Vui long nhap so nguyen >= {min_value}.")
            else:
                print(f"Vui long nhap so nguyen trong khoang [{min_value}, {max_value}].")


def ask_human_move(game: CaroGame) -> Move:
    while True:
        raw = input("Nhap nuoc di (hang cot), vi du: 3 4: ").strip().split()
        if len(raw) != 2:
            print("Dinh dang khong hop le. Hay nhap 2 so: hang cot.")
            continue

        try:
            row = int(raw[0]) - 1
            col = int(raw[1]) - 1
        except ValueError:
            print("Hang/cot phai la so nguyen.")
            continue

        move = Move(row, col)
        if not game.is_valid_move(move):
            print("Nuoc di khong hop le hoac o da duoc danh. Thu lai.")
            continue
        return move


def suggested_depth(size: int) -> int:
    if size <= 3:
        return 9
    if size <= 5:
        return 5
    if size <= 8:
        return 4
    return 3


def suggested_candidate_limit(size: int) -> int:
    if size <= 5:
        return size * size
    if size <= 8:
        return 14
    return 12


def main() -> None:
    print("=== AI CO CARO (MINIMAX + ALPHA-BETA + HEURISTIC) ===")
    size = read_int(
        f"Kich thuoc ban co (n x n, {MIN_BOARD_SIZE}-{MAX_BOARD_SIZE})",
        default=10,
        min_value=MIN_BOARD_SIZE,
        max_value=MAX_BOARD_SIZE,
    )
    win_len_default = 3 if size <= 3 else 5
    win_len = read_int(
        "So quan lien tiep de thang",
        default=win_len_default,
        min_value=MIN_BOARD_SIZE,
        max_value=size,
    )
    depth = read_int(
        "Do sau tim kiem cho AI",
        default=suggested_depth(size),
        min_value=1,
        max_value=10,
    )
    max_candidates = read_int(
        "So nuoc ung vien toi da moi lop",
        default=suggested_candidate_limit(size),
        min_value=4,
        max_value=size * size,
    )
    max_time_ms = read_int(
        "Gioi han thoi gian moi nuoc AI (ms)",
        default=300,
        min_value=50,
        max_value=5000,
    )

    first = input("Ban muon di truoc? (y/n) [y]: ").strip().lower()
    human_turn = first != "n"

    game = CaroGame(size=size, win_len=win_len)
    last_move: Optional[Move] = None

    while True:
        print("\nBan co hien tai:")
        game.print_board()

        winner = game.check_winner(last_move)
        if winner is not None or game.is_full():
            if winner == AI_MARK:
                print("\nAI thang.")
            elif winner == HUMAN_MARK:
                print("\nBan thang.")
            else:
                print("\nHoa.")
            break

        if human_turn:
            move = ask_human_move(game)
            game.make_move(move, HUMAN_MARK)
            last_move = move
        else:
            print("\nAI dang tinh toan...")
            move = ai_best_move(
                game,
                depth=depth,
                max_candidates=max_candidates,
                max_time_ms=max_time_ms,
            )
            game.make_move(move, AI_MARK)
            last_move = move
            print(f"AI danh tai: hang {move.row + 1}, cot {move.col + 1}")

        human_turn = not human_turn
