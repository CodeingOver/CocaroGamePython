from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

# Thêm thư mục gốc vào sys.path để có thể import các module ai, game, ...
root_path = Path(__file__).resolve().parent.parent
if str(root_path) not in sys.path:
    sys.path.append(str(root_path))

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Set, Tuple

from ai import SearchStats, ai_best_move
from constants import AI_MARK, EMPTY, HUMAN_MARK
from game import CaroGame, Move

# 4 chế độ thuật toán để so sánh (nhãn, use_ab, use_gbfs)
ALGO_MODES: Tuple[Tuple[str, bool, bool], ...] = (
    ("AB + GBFS", True,  True),
    ("AB Only",   True,  False),
    ("GBFS Only", False, True),
    ("Minimax",   False, False),
)

LOG_PATH = root_path / "docs" / "benchmarks" / "tactical_report.md"


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


@dataclass
class CaseResult:
    passed: bool
    chosen: Tuple[int, int]
    expected: Set[Tuple[int, int]]
    stats: SearchStats
    board_snapshot: List[List[str]]   # Trạng thái bàn cờ khi AI ra quyết định


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


def render_board_md(board: List[List[str]], chosen: Tuple[int, int], expected: Set[Tuple[int, int]]) -> str:
    # Vẽ bàn cờ dạng Markdown code block, đánh dấu:
    #   [*] = nước AI đã chọn
    #   [?] = các nước kỳ vọng khác chưa được chọn
    size = len(board)
    # Header hàng số cột
    col_header = "     " + "  ".join(f"{c:2d}" for c in range(size))
    lines = [col_header, "    +" + "---" * size + "+"]
    for r in range(size):
        row_cells = []
        for c in range(size):
            cell = board[r][c]
            if (r, c) == chosen:
                row_cells.append("★ ")   # Nước AI đã đánh
            elif (r, c) in expected:
                row_cells.append("· ")   # Nước kỳ vọng (nếu AI chọn sai)
            elif cell == AI_MARK:
                row_cells.append("X ")
            elif cell == HUMAN_MARK:
                row_cells.append("O ")
            else:
                row_cells.append(". ")
        lines.append(f" {r:2d} | " + " ".join(row_cells) + "|")
    lines.append("    +" + "---" * size + "+")
    lines.append("  Ký hiệu: X=AI  O=Người  ★=Nước AI chọn  ·=Nước kỳ vọng")
    return "\n".join(lines)


def run_case(case: TacticalCase, use_ab: bool = True, use_gbfs: bool = True) -> CaseResult:
    # Chạy một case và trả về kết quả chi tiết.
    game = setup_case(case)
    # Chụp trạng thái bàn cờ trước khi AI ra nước
    board_snapshot = [row[:] for row in game.board]
    move, stats = ai_best_move(
        game,
        depth=case.depth,
        max_candidates=case.max_candidates,
        max_time_ms=case.max_time_ms,
        use_ab=use_ab,
        use_gbfs=use_gbfs,
    )
    chosen = (move.row, move.col)
    passed = chosen in case.expected
    return CaseResult(
        passed=passed,
        chosen=chosen,
        expected=case.expected,
        stats=stats,
        board_snapshot=board_snapshot,
    )


def _write_markdown_report(
    results_by_mode: Dict[str, List[CaseResult]],
    output_path: Path,
) -> None:
    # Ghi báo cáo Markdown chi tiết với bàn cờ trực quan cho từng case.
    total = len(TACTICAL_CASES)
    lines: List[str] = []

    lines.append("# Báo cáo Kiểm thử Chiến thuật AI - So sánh 4 chế độ")
    lines.append("")
    lines.append(f"- **Thời gian chạy:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"- **Tổng số ca kiểm thử:** {total}")
    lines.append(f"- **Tiêu chí đạt:** Nước AI chọn phải thuộc tập nước kỳ vọng")
    lines.append("")

    # ---- Bảng tóm tắt ----
    lines.append("## Tóm tắt kết quả")
    lines.append("")
    header_cols = " | ".join(f"**{lbl}**" for lbl, _, _ in ALGO_MODES)
    lines.append(f"| Ca kiểm thử | {header_cols} |")
    lines.append("|---|" + "---|" * len(ALGO_MODES))
    for i, case in enumerate(TACTICAL_CASES):
        cells = []
        for algo_label, _, _ in ALGO_MODES:
            r = results_by_mode[algo_label][i]
            cells.append("✅ PASS" if r.passed else "❌ FAIL")
        lines.append(f"| {case.name} | {' | '.join(cells)} |")
    # Tổng
    totals = []
    for algo_label, _, _ in ALGO_MODES:
        n = sum(1 for r in results_by_mode[algo_label] if r.passed)
        totals.append(f"**{n}/{total}**")
    lines.append(f"| **TỔNG PASS** | {' | '.join(totals)} |")
    lines.append("")

    # ---- Bảng thống kê tốc độ ----
    lines.append("## Thống kê hiệu năng trung bình")
    lines.append("")
    lines.append("| Thuật toán | Avg Thời gian (ms) | Avg Nút duyệt | Avg Cắt tỉa | Avg Độ sâu đạt |")
    lines.append("|---|---:|---:|---:|---:|")
    for algo_label, _, _ in ALGO_MODES:
        mode_results = results_by_mode[algo_label]
        n = len(mode_results)
        avg_ms = sum(r.stats.elapsed_ms for r in mode_results) / n
        avg_nodes = sum(r.stats.nodes_visited for r in mode_results) / n
        avg_cuts = sum(r.stats.cutoffs for r in mode_results) / n
        avg_depth = sum(r.stats.depth_reached for r in mode_results) / n
        lines.append(f"| {algo_label} | {avg_ms:.1f} | {avg_nodes:,.0f} | {avg_cuts:,.0f} | {avg_depth:.1f} |")
    lines.append("")

    # ---- Chi tiết từng case ----
    lines.append("## Chi tiết từng ca kiểm thử")
    lines.append("")

    for i, case in enumerate(TACTICAL_CASES):
        lines.append(f"### {i + 1}. {case.name}")
        lines.append("")
        lines.append(f"- **Cấu hình:** Bàn {case.size}×{case.size}, thắng {case.win_len} quân")
        lines.append(f"- **Tham số AI:** depth={case.depth}, candidates={case.max_candidates}, budget={case.max_time_ms}ms")
        expected_str = ", ".join(str(p) for p in sorted(case.expected))
        lines.append(f"- **Nước kỳ vọng:** `{{{expected_str}}}`")
        lines.append("")

        for algo_label, _, _ in ALGO_MODES:
            r = results_by_mode[algo_label][i]
            verdict = "✅ PASS" if r.passed else "❌ FAIL"
            lines.append(f"#### [{algo_label}] — {verdict}")
            lines.append("")
            lines.append(
                f"- AI chọn: `{r.chosen}` | "
                f"Thời gian: `{r.stats.elapsed_ms:.1f}ms` | "
                f"Nút duyệt: `{r.stats.nodes_visited:,}` | "
                f"Cắt tỉa: `{r.stats.cutoffs:,}` | "
                f"Độ sâu đạt: `{r.stats.depth_reached}`"
            )
            lines.append("")
            lines.append("```")
            lines.append(render_board_md(r.board_snapshot, r.chosen, case.expected))
            lines.append("```")
            lines.append("")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    total = len(TACTICAL_CASES)
    results_by_mode: Dict[str, List[CaseResult]] = {}

    for algo_label, use_ab, use_gbfs in ALGO_MODES:
        print(f"\n=== [{algo_label}] KIỂM THỬ THẾ CỜ CHIẾN THUẬT ===")
        mode_results: List[CaseResult] = []
        for case in TACTICAL_CASES:
            result = run_case(case, use_ab=use_ab, use_gbfs=use_gbfs)
            mode_results.append(result)
            status = "PASS" if result.passed else "FAIL"
            print(
                f"  - {case.name}: {status}"
                f"  [AI→{result.chosen} | {result.stats.elapsed_ms:.0f}ms"
                f" | nút={result.stats.nodes_visited:,} | cắt={result.stats.cutoffs:,}]"
            )
        results_by_mode[algo_label] = mode_results
        passed_count = sum(1 for r in mode_results if r.passed)
        print(f"  Kết quả: {passed_count}/{total} PASS")

    # Bảng tổng hợp so sánh tỷ lệ pass (terminal)
    W = 42
    COL = 12
    print("\n" + "=" * (W + COL * len(ALGO_MODES)))
    print("  BẢNG SO SÁNH TỶ LỆ PASS CHIẾN THUẬT")
    print("=" * (W + COL * len(ALGO_MODES)))
    header = f"  {'Ca kiểm thử':<{W}}" + "".join(f"{'|'+lbl[:9]:^{COL}}" for lbl, _, _ in ALGO_MODES)
    print(header)
    print("-" * (W + COL * len(ALGO_MODES)))
    for i, case in enumerate(TACTICAL_CASES):
        row_str = f"  {case.name[:W]:<{W}}"
        for algo_label, _, _ in ALGO_MODES:
            cell = " PASS " if results_by_mode[algo_label][i].passed else " FAIL "
            row_str += f"|{cell:^{COL-1}}"
        print(row_str)
    print("-" * (W + COL * len(ALGO_MODES)))
    summary_row = f"  {'TỔNG PASS':<{W}}"
    for algo_label, _, _ in ALGO_MODES:
        count = sum(1 for r in results_by_mode[algo_label] if r.passed)
        summary_row += f"|  {count}/{total}     "
    print(summary_row)
    print("=" * (W + COL * len(ALGO_MODES)))

    # Xuất log Markdown
    _write_markdown_report(results_by_mode, LOG_PATH)
    print(f"\nBáo cáo chi tiết: {LOG_PATH}")

    # Chỉ thoát lỗi nếu chế độ mục tiêu (AB+GBFS) không pass hết
    ab_gbfs_results = results_by_mode.get("AB + GBFS", [])
    if not all(r.passed for r in ab_gbfs_results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
