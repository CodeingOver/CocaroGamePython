from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from statistics import mean
from time import perf_counter
from typing import Dict, Iterable, List, Sequence, Tuple

from ai import STATE_BEST_MOVE_CACHE, ai_best_move
from game import CaroGame, Move


@dataclass(frozen=True)
class DifficultyProfile:
    name: str
    depth: int
    candidates: int
    time_ms: int


@dataclass(frozen=True)
class Scenario:
    name: str
    moves: Sequence[Tuple[int, int, str]]


GUI_PRESETS: Tuple[DifficultyProfile, ...] = (
    DifficultyProfile(name="Khó", depth=4, candidates=14, time_ms=450),
    DifficultyProfile(name="Cực khó", depth=5, candidates=16, time_ms=850),
    DifficultyProfile(name="Địa ngục", depth=6, candidates=18, time_ms=1500),
)

CUSTOM_PRESETS: Tuple[DifficultyProfile, ...] = (
    DifficultyProfile(name="Tùy chỉnh A", depth=4, candidates=14, time_ms=450),
    DifficultyProfile(name="Tùy chỉnh B", depth=6, candidates=18, time_ms=1500),
)

def apply_scenario(game: CaroGame, scenario: Scenario) -> None:
    # Nạp nhanh trạng thái bàn cờ từ danh sách nước đi mẫu.
    for row, col, player in scenario.moves:
        game.make_move(Move(row, col), player)


def parse_sizes(raw: str) -> List[int]:
    # Parse chuỗi kích thước dạng "10,12,15" và loại bỏ phần tử rỗng/trùng.
    values: List[int] = []
    seen = set()

    for item in raw.split(","):
        token = item.strip()
        if not token:
            continue
        size = int(token)
        if size < 3:
            raise ValueError("Kích thước bàn cờ phải >= 3")
        if size in seen:
            continue
        seen.add(size)
        values.append(size)

    if not values:
        raise ValueError("Cần ít nhất một kích thước bàn cờ hợp lệ")

    return values


def _build_scenario_moves(size: int, win_len: int, positions: Sequence[Tuple[int, int]]) -> List[Tuple[int, int, str]]:
    # Xây trạng thái hợp lệ và tránh tạo bàn cờ đã có người thắng trước khi benchmark.
    game = CaroGame(size=size, win_len=win_len)
    moves: List[Tuple[int, int, str]] = []
    ai_turn = True

    for row, col in positions:
        move = Move(row, col)
        if not game.is_valid_move(move):
            continue

        player = "X" if ai_turn else "O"
        game.make_move(move, player)
        if game.check_winner(move) is not None:
            game.undo_move(move)
            continue

        moves.append((row, col, player))
        ai_turn = not ai_turn

    # Bảo đảm đến lượt AI (X) để so đo benchmark nhất quán.
    if len(moves) % 2 == 1:
        moves.pop()

    # Nếu kịch bản quá ngắn thì chèn trạng thái nhỏ quanh trung tâm.
    if not moves:
        center = size // 2
        fallback = [(center, center), (center, max(0, center - 1))]
        return _build_scenario_moves(size, win_len, fallback)

    return moves


def build_dynamic_scenarios(size: int, win_len: int) -> Tuple[Scenario, ...]:
    # Tạo 3 kịch bản động theo kích thước bàn để benchmark không bị khóa cứng 10x10.
    center = size // 2

    def in_board(row: int, col: int) -> bool:
        return 0 <= row < size and 0 <= col < size

    def from_offsets(offsets: Sequence[Tuple[int, int]]) -> List[Tuple[int, int]]:
        coords: List[Tuple[int, int]] = []
        seen = set()
        for dr, dc in offsets:
            row, col = center + dr, center + dc
            if not in_board(row, col):
                continue
            if (row, col) in seen:
                continue
            seen.add((row, col))
            coords.append((row, col))
        return coords

    opening_offsets = [
        (0, 0),
        (0, -1),
        (-1, 0),
        (1, 0),
        (0, 1),
        (-1, -1),
        (1, 1),
        (-1, 1),
        (1, -1),
    ]

    midgame_offsets = [
        (0, 0),
        (0, -1),
        (0, 1),
        (-1, 0),
        (1, 0),
        (-1, -1),
        (1, 1),
        (-1, 1),
        (1, -1),
        (0, -2),
        (0, 2),
        (-2, 0),
        (2, 0),
        (-2, -1),
        (2, 1),
        (-1, 2),
        (1, -2),
    ]

    # Kịch bản tải cao: quét khối vuông ở góc để tăng mật độ bàn cờ.
    block = min(size, 8)
    heavy_positions: List[Tuple[int, int]] = []
    for row in range(block):
        cols = range(block) if row % 2 == 0 else range(block - 1, -1, -1)
        for col in cols:
            heavy_positions.append((row, col))

    opening = Scenario(
        name="Khai cuộc cân bằng",
        moves=_build_scenario_moves(size, win_len, from_offsets(opening_offsets)),
    )
    midgame = Scenario(
        name="Trung cuộc tranh chấp",
        moves=_build_scenario_moves(size, win_len, from_offsets(midgame_offsets)),
    )
    heavy = Scenario(
        name="Tải cao gần cuối ván",
        moves=_build_scenario_moves(size, win_len, heavy_positions),
    )

    return (opening, midgame, heavy)


def percentile(values: Sequence[float], p: float) -> float:
    # Tính percentile đơn giản để không phụ thuộc thư viện ngoài.
    if not values:
        return 0.0
    sorted_values = sorted(values)
    if len(sorted_values) == 1:
        return sorted_values[0]
    index = (len(sorted_values) - 1) * p
    lower = int(index)
    upper = min(lower + 1, len(sorted_values) - 1)
    if lower == upper:
        return sorted_values[lower]
    ratio = index - lower
    return sorted_values[lower] * (1 - ratio) + sorted_values[upper] * ratio


def run_profile(
    profile: DifficultyProfile,
    scenarios: Iterable[Scenario],
    board_size: int,
    win_len: int,
    repeats: int,
) -> List[Dict[str, object]]:
    # Chạy benchmark cho một profile và trả về dữ liệu thô theo từng lượt AI.
    rows: List[Dict[str, object]] = []

    for scenario in scenarios:
        for attempt in range(1, repeats + 1):
            game = CaroGame(size=board_size, win_len=win_len)
            apply_scenario(game, scenario)

            # Xóa cache toàn cục trước mỗi lượt đo để tránh kết quả bị lệch do trả về từ bộ nhớ đệm.
            STATE_BEST_MOVE_CACHE.clear()

            start = perf_counter()
            move = ai_best_move(
                game,
                depth=profile.depth,
                max_candidates=profile.candidates,
                max_time_ms=profile.time_ms,
            )
            elapsed_ms = (perf_counter() - start) * 1000.0

            rows.append(
                {
                    "profile": profile.name,
                    "board_size": board_size,
                    "win_len": win_len,
                    "depth": profile.depth,
                    "candidates": profile.candidates,
                    "time_budget_ms": profile.time_ms,
                    "scenario": scenario.name,
                    "attempt": attempt,
                    "elapsed_ms": round(elapsed_ms, 3),
                    "pass_under_2000ms": elapsed_ms <= 2000.0,
                    "move": f"({move.row},{move.col})",
                }
            )

    return rows


def summarize(rows: Sequence[Dict[str, object]]) -> List[Dict[str, object]]:
    # Tổng hợp theo profile để dùng trong báo cáo nghiệm thu.
    grouped: Dict[Tuple[str, int, int], List[float]] = {}
    budgets: Dict[Tuple[str, int, int], int] = {}

    for row in rows:
        profile = str(row["profile"])
        board_size = int(row["board_size"])
        win_len = int(row["win_len"])
        key = (profile, board_size, win_len)
        grouped.setdefault(key, []).append(float(row["elapsed_ms"]))
        budgets[key] = int(row["time_budget_ms"])

    summary: List[Dict[str, object]] = []
    for (profile, board_size, win_len), values in grouped.items():
        over_2s = sum(1 for value in values if value > 2000.0)
        summary.append(
            {
                "profile": profile,
                "board_size": board_size,
                "win_len": win_len,
                "samples": len(values),
                "time_budget_ms": budgets[(profile, board_size, win_len)],
                "min_ms": round(min(values), 3),
                "avg_ms": round(mean(values), 3),
                "p95_ms": round(percentile(values, 0.95), 3),
                "max_ms": round(max(values), 3),
                "over_2s": over_2s,
                "pass_all_under_2s": over_2s == 0,
            }
        )

    summary.sort(key=lambda item: (int(item["board_size"]), str(item["profile"])))
    return summary


def write_csv(path: Path, rows: Sequence[Dict[str, object]]) -> None:
    # Ghi dữ liệu thô để tiện vẽ biểu đồ hoặc kiểm tra lại.
    if not rows:
        return

    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, summary_rows: Sequence[Dict[str, object]], details_rows: Sequence[Dict[str, object]]) -> None:
    # Xuất báo cáo Markdown để dùng trực tiếp trong hồ sơ đề tài.
    lines: List[str] = []
    lines.append("# Báo cáo benchmark AI Cờ Caro")
    lines.append("")
    lines.append(f"- Thời gian chạy: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("- Tiêu chí đạt: mọi lượt AI <= 2000ms")
    lines.append("")
    lines.append("## Tổng hợp theo cấu hình")
    lines.append("")
    lines.append("| Bàn cờ | Win_len | Cấu hình | Mẫu | Budget (ms) | Min | Avg | P95 | Max | Vượt 2s | Kết luận |")
    lines.append("|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---|")

    for row in summary_rows:
        verdict = "Đạt" if bool(row["pass_all_under_2s"]) else "Chưa đạt"
        lines.append(
            "| {board_size} | {win_len} | {profile} | {samples} | {time_budget_ms} | {min_ms} | {avg_ms} | {p95_ms} | {max_ms} | {over_2s} | {verdict} |".format(
                verdict=verdict,
                **row,
            )
        )

    lines.append("")
    lines.append("## Chi tiết từng lượt")
    lines.append("")
    lines.append("| Bàn cờ | Win_len | Cấu hình | Kịch bản | Lần chạy | Thời gian (ms) | Nước đi | <=2s |")
    lines.append("|---:|---:|---|---|---:|---:|---|---|")
    for row in details_rows:
        lines.append(
            "| {board_size} | {win_len} | {profile} | {scenario} | {attempt} | {elapsed_ms} | {move} | {pass_under_2000ms} |".format(**row)
        )

    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Benchmark độ trễ phản hồi AI Cờ Caro")
    parser.add_argument(
        "--sizes",
        default="10",
        help="Danh sách kích thước bàn cờ, ví dụ: 10,12,15",
    )
    parser.add_argument(
        "--win-len",
        type=int,
        default=5,
        help="Số quân liên tiếp để thắng (sẽ tự hạ xuống nếu lớn hơn size)",
    )
    parser.add_argument("--repeats", type=int, default=3, help="Số lần chạy mỗi kịch bản")
    parser.add_argument(
        "--output-dir",
        default="docs/benchmarks",
        help="Thư mục xuất báo cáo markdown/csv",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    sizes = parse_sizes(args.sizes)

    all_profiles = GUI_PRESETS + CUSTOM_PRESETS
    all_rows: List[Dict[str, object]] = []

    for size in sizes:
        win_len = min(args.win_len, size)
        scenarios = build_dynamic_scenarios(size=size, win_len=win_len)

        for profile in all_profiles:
            all_rows.extend(
                run_profile(
                    profile=profile,
                    scenarios=scenarios,
                    board_size=size,
                    win_len=win_len,
                    repeats=args.repeats,
                )
            )

    summary_rows = summarize(all_rows)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    csv_path = output_dir / f"benchmark_{timestamp}.csv"
    md_path = output_dir / f"benchmark_{timestamp}.md"

    write_csv(csv_path, all_rows)
    write_markdown(md_path, summary_rows, all_rows)

    print("=== KẾT QUẢ BENCHMARK AI ===")
    for row in summary_rows:
        verdict = "ĐẠT" if bool(row["pass_all_under_2s"]) else "CHƯA ĐẠT"
        print(
            f"- Bàn {row['board_size']} (win_len={row['win_len']}) - {row['profile']}: "
            f"avg={row['avg_ms']}ms, p95={row['p95_ms']}ms, max={row['max_ms']}ms, "
            f"vượt_2s={row['over_2s']} -> {verdict}"
        )

    print(f"\nBáo cáo Markdown: {md_path}")
    print(f"Báo cáo CSV: {csv_path}")


if __name__ == "__main__":
    main()
