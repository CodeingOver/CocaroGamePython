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

CLI_CUSTOM_PRESETS: Tuple[DifficultyProfile, ...] = (
    DifficultyProfile(name="CLI tùy chỉnh A", depth=4, candidates=14, time_ms=450),
    DifficultyProfile(name="CLI tùy chỉnh B", depth=6, candidates=18, time_ms=1500),
)

# Các trạng thái được chọn để đại diện khai cuộc, trung cuộc và tải cao gần cuối ván.
SCENARIOS: Tuple[Scenario, ...] = (
    Scenario(
        name="Khai cuộc cân bằng",
        moves=(
            (5, 5, "X"),
            (5, 4, "O"),
            (4, 5, "X"),
            (6, 5, "O"),
            (5, 6, "X"),
            (4, 4, "O"),
        ),
    ),
    Scenario(
        name="Trung cuộc tranh chấp",
        moves=(
            (5, 5, "X"),
            (5, 4, "O"),
            (4, 5, "X"),
            (6, 5, "O"),
            (5, 6, "X"),
            (4, 4, "O"),
            (6, 6, "X"),
            (5, 7, "O"),
            (4, 6, "X"),
            (6, 4, "O"),
            (3, 5, "X"),
            (7, 5, "O"),
        ),
    ),
    Scenario(
        name="Tải cao gần cuối ván",
        moves=(
            (0, 0, "X"),
            (0, 1, "O"),
            (0, 2, "X"),
            (0, 3, "O"),
            (0, 4, "X"),
            (0, 5, "O"),
            (1, 0, "O"),
            (1, 1, "X"),
            (1, 2, "O"),
            (1, 3, "X"),
            (1, 4, "O"),
            (1, 5, "X"),
            (2, 0, "X"),
            (2, 1, "O"),
            (2, 2, "X"),
            (2, 3, "O"),
            (2, 4, "X"),
            (2, 5, "O"),
            (3, 0, "O"),
            (3, 1, "X"),
            (3, 2, "O"),
            (3, 3, "X"),
            (3, 4, "O"),
            (3, 5, "X"),
            (4, 0, "X"),
            (4, 1, "O"),
            (4, 2, "X"),
            (4, 3, "O"),
            (4, 4, "X"),
            (4, 6, "O"),
            (5, 0, "O"),
            (5, 1, "X"),
            (5, 2, "O"),
            (5, 3, "X"),
            (5, 4, "O"),
            (5, 5, "X"),
        ),
    ),
)


def apply_scenario(game: CaroGame, scenario: Scenario) -> None:
    # Nạp nhanh trạng thái bàn cờ từ danh sách nước đi mẫu.
    for row, col, player in scenario.moves:
        game.make_move(Move(row, col), player)


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
    grouped: Dict[str, List[float]] = {}
    budgets: Dict[str, int] = {}

    for row in rows:
        profile = str(row["profile"])
        grouped.setdefault(profile, []).append(float(row["elapsed_ms"]))
        budgets[profile] = int(row["time_budget_ms"])

    summary: List[Dict[str, object]] = []
    for profile, values in grouped.items():
        over_2s = sum(1 for value in values if value > 2000.0)
        summary.append(
            {
                "profile": profile,
                "samples": len(values),
                "time_budget_ms": budgets[profile],
                "min_ms": round(min(values), 3),
                "avg_ms": round(mean(values), 3),
                "p95_ms": round(percentile(values, 0.95), 3),
                "max_ms": round(max(values), 3),
                "over_2s": over_2s,
                "pass_all_under_2s": over_2s == 0,
            }
        )

    summary.sort(key=lambda item: str(item["profile"]))
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
    lines.append("| Cấu hình | Mẫu | Budget (ms) | Min | Avg | P95 | Max | Vượt 2s | Kết luận |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---|")

    for row in summary_rows:
        verdict = "Đạt" if bool(row["pass_all_under_2s"]) else "Chưa đạt"
        lines.append(
            "| {profile} | {samples} | {time_budget_ms} | {min_ms} | {avg_ms} | {p95_ms} | {max_ms} | {over_2s} | {verdict} |".format(
                verdict=verdict,
                **row,
            )
        )

    lines.append("")
    lines.append("## Chi tiết từng lượt")
    lines.append("")
    lines.append("| Cấu hình | Kịch bản | Lần chạy | Thời gian (ms) | Nước đi | <=2s |")
    lines.append("|---|---|---:|---:|---|---|")
    for row in details_rows:
        lines.append(
            "| {profile} | {scenario} | {attempt} | {elapsed_ms} | {move} | {pass_under_2000ms} |".format(**row)
        )

    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Benchmark độ trễ phản hồi AI Cờ Caro")
    parser.add_argument("--size", type=int, default=10, help="Kích thước bàn cờ")
    parser.add_argument("--win-len", type=int, default=5, help="Số quân liên tiếp để thắng")
    parser.add_argument("--repeats", type=int, default=3, help="Số lần chạy mỗi kịch bản")
    parser.add_argument(
        "--output-dir",
        default="docs/benchmarks",
        help="Thư mục xuất báo cáo markdown/csv",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    all_profiles = GUI_PRESETS + CLI_CUSTOM_PRESETS
    all_rows: List[Dict[str, object]] = []

    for profile in all_profiles:
        all_rows.extend(
            run_profile(
                profile=profile,
                scenarios=SCENARIOS,
                board_size=args.size,
                win_len=args.win_len,
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
            f"- {row['profile']}: avg={row['avg_ms']}ms, p95={row['p95_ms']}ms, max={row['max_ms']}ms, "
            f"vượt_2s={row['over_2s']} -> {verdict}"
        )

    print(f"\nBáo cáo Markdown: {md_path}")
    print(f"Báo cáo CSV: {csv_path}")


if __name__ == "__main__":
    main()
