from __future__ import annotations

import sys
from pathlib import Path

# Thêm thư mục gốc vào sys.path để có thể import các module ai, game, ...
root_path = Path(__file__).resolve().parent.parent
if str(root_path) not in sys.path:
    sys.path.append(str(root_path))

from dataclasses import dataclass
from typing import Dict, List, Sequence, Set, Tuple

from ai import ai_best_move
from constants import AI_MARK, HUMAN_MARK
from game import CaroGame, Move

# 4 chế độ thuật toán để so sánh (nhãn, use_ab, use_gbfs)
ALGO_MODES: Tuple[Tuple[str, bool, bool], ...] = (
    ("AB + GBFS", True,  True),
    ("AB Only",   True,  False),
    ("GBFS Only", False, True),
    ("Minimax",   False, False),
)


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
        max_time_ms=1000,
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
        max_time_ms=1500,
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
        max_time_ms=2000,
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
        max_time_ms=1500,
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
        max_time_ms=1500,
    ),
)


def setup_case(case: TacticalCase) -> CaroGame:
    # Khởi tạo bàn cờ theo trạng thái chiến thuật mong muốn.
    game = CaroGame(size=case.size, win_len=case.win_len)
    for row, col, player in case.moves:
        game.make_move(Move(row, col), player)
    return game


def run_case(case: TacticalCase, use_ab: bool = True, use_gbfs: bool = True) -> bool:
    # Chạy một case và kiểm tra nước đi AI có thuộc tập kỳ vọng hay không.
    game = setup_case(case)
    move, _stats = ai_best_move(
        game,
        depth=case.depth,
        max_candidates=case.max_candidates,
        max_time_ms=case.max_time_ms,
        use_ab=use_ab,
        use_gbfs=use_gbfs,
    )
    return (move.row, move.col) in case.expected


def main() -> None:
    total = len(TACTICAL_CASES)
    # Lưu kết quả theo chế độ: {algo_label: [True/False, ...]}
    results: Dict[str, List[bool]] = {}

    for algo_label, use_ab, use_gbfs in ALGO_MODES:
        print(f"\n=== [{algo_label}] KIỂM THỬ THẾ CỜ CHIẾN THUẬT ===")
        case_results: List[bool] = []
        for case in TACTICAL_CASES:
            passed = run_case(case, use_ab=use_ab, use_gbfs=use_gbfs)
            case_results.append(passed)
            status = "PASS" if passed else "FAIL"
            print(f"  - {case.name}: {status}")
        results[algo_label] = case_results
        passed_count = sum(case_results)
        print(f"  Kết quả: {passed_count}/{total} PASS")

    # Bảng tổng hợp so sánh tỷ lệ pass
    print("\n" + "=" * 55)
    print("  BẢNG SO SÁNH TỶ LỆ PASS CHIẾN THUẬT")
    print("=" * 55)
    header = f"  {'Case':<38}" + "".join(f"{'|'+lbl[:8]:^11}" for lbl, _, _ in ALGO_MODES)
    print(header)
    print("-" * 55)
    for i, case in enumerate(TACTICAL_CASES):
        row_str = f"  {case.name[:38]:<38}"
        for algo_label, _, _ in ALGO_MODES:
            cell = " PASS " if results[algo_label][i] else " FAIL "
            row_str += f"|{cell:^10}"
        print(row_str)
    print("-" * 55)
    summary_row = f"  {'TỔNG PASS':<38}"
    for algo_label, _, _ in ALGO_MODES:
        count = sum(results[algo_label])
        summary_row += f"|{count}/{total}    "
    print(summary_row)
    print("=" * 55)

    # Chỉ thoát lỗi nếu chế độ mục tiêu (AB+GBFS) không pass hết
    ab_gbfs_results = results.get("AB + GBFS", [])
    if not all(ab_gbfs_results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()


