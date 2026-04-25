from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence, Set, Tuple

from ai import ai_best_move
from constants import AI_MARK, HUMAN_MARK
from game import CaroGame, Move


@dataclass(frozen=True)
class TacticalCase:
    name: str
    size: int
    win_len: int
    moves: Sequence[Tuple[int, int, str]]
    expected: Set[Tuple[int, int]]
    depth: int
    max_candidates: int
    max_time_ms: int


# Các ca kiểm thử tập trung vào bắt buộc thắng/chặn để chứng minh năng lực nhận diện chiến thuật.
TACTICAL_CASES: Tuple[TacticalCase, ...] = (
    TacticalCase(
        name="AI thắng ngay theo hàng",
        size=10,
        win_len=5,
        moves=(
            (5, 2, AI_MARK),
            (5, 3, AI_MARK),
            (5, 4, AI_MARK),
            (5, 5, AI_MARK),
            (4, 4, HUMAN_MARK),
            (4, 5, HUMAN_MARK),
        ),
        expected={(5, 1), (5, 6)},
        depth=4,
        max_candidates=14,
        max_time_ms=450,
    ),
    TacticalCase(
        name="AI phải chặn thua ngay theo cột",
        size=10,
        win_len=5,
        moves=(
            (2, 6, HUMAN_MARK),
            (3, 6, HUMAN_MARK),
            (4, 6, HUMAN_MARK),
            (5, 6, HUMAN_MARK),
            (4, 4, AI_MARK),
            (5, 4, AI_MARK),
        ),
        expected={(1, 6), (6, 6)},
        depth=5,
        max_candidates=16,
        max_time_ms=850,
    ),
    TacticalCase(
        name="AI ưu tiên kết thúc đường chéo",
        size=10,
        win_len=5,
        moves=(
            (2, 2, AI_MARK),
            (3, 3, AI_MARK),
            (4, 4, AI_MARK),
            (5, 5, AI_MARK),
            (1, 2, HUMAN_MARK),
            (1, 3, HUMAN_MARK),
        ),
        expected={(1, 1), (6, 6)},
        depth=6,
        max_candidates=18,
        max_time_ms=1500,
    ),
    TacticalCase(
        name="AI ưu tiên chặn thay vì nối thẳng",
        size=10,
        win_len=5,
        moves=(
            (5, 3, AI_MARK),
            (5, 4, AI_MARK),
            (5, 5, AI_MARK),
            (2, 7, HUMAN_MARK),
            (3, 7, HUMAN_MARK),
            (4, 7, HUMAN_MARK),
            (5, 7, HUMAN_MARK),
        ),
        expected={(1, 7), (6, 7)},
        depth=5,
        max_candidates=16,
        max_time_ms=850,
    ),
    TacticalCase(
        name="AI tạo bẫy 2 nước open-four",
        size=10,
        win_len=5,
        moves=(
            (5, 3, AI_MARK),
            (5, 4, AI_MARK),
            (5, 6, AI_MARK),
            (4, 4, HUMAN_MARK),
            (6, 4, HUMAN_MARK),
            (4, 6, HUMAN_MARK),
        ),
        expected={(5, 5)},
        depth=5,
        max_candidates=16,
        max_time_ms=850,
    ),
)


def setup_case(case: TacticalCase) -> CaroGame:
    # Khởi tạo bàn cờ theo trạng thái chiến thuật mong muốn.
    game = CaroGame(size=case.size, win_len=case.win_len)
    for row, col, player in case.moves:
        game.make_move(Move(row, col), player)
    return game


def run_case(case: TacticalCase) -> bool:
    # Chạy một case và kiểm tra nước đi AI có thuộc tập kỳ vọng hay không.
    game = setup_case(case)
    move = ai_best_move(
        game,
        depth=case.depth,
        max_candidates=case.max_candidates,
        max_time_ms=case.max_time_ms,
    )
    result = (move.row, move.col) in case.expected

    expected_text = ", ".join(str(x) for x in sorted(case.expected))
    print(f"- {case.name}: AI chọn {(move.row, move.col)}, kỳ vọng {{{expected_text}}} -> {'PASS' if result else 'FAIL'}")
    return result


def main() -> None:
    passed = 0
    total = len(TACTICAL_CASES)

    print("=== KIỂM THỬ THẾ CỜ CHIẾN THUẬT ===")
    for case in TACTICAL_CASES:
        if run_case(case):
            passed += 1

    print(f"\nKết quả: {passed}/{total} case PASS")
    if passed != total:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
