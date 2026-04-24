from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple

from constants import EMPTY


@dataclass(frozen=True)
class Move:
    row: int
    col: int


class CaroGame:
    def __init__(self, size: int = 10, win_len: int = 5) -> None:
        self.size = size
        self.win_len = win_len
        self.board: List[List[str]] = [[EMPTY for _ in range(size)] for _ in range(size)]

    def is_valid_move(self, move: Move) -> bool:
        return (
            0 <= move.row < self.size
            and 0 <= move.col < self.size
            and self.board[move.row][move.col] == EMPTY
        )

    def make_move(self, move: Move, player: str) -> None:
        self.board[move.row][move.col] = player

    def undo_move(self, move: Move) -> None:
        self.board[move.row][move.col] = EMPTY

    def is_full(self) -> bool:
        return all(cell != EMPTY for row in self.board for cell in row)

    def get_candidate_moves(self, radius: int = 1) -> List[Move]:
        occupied: List[Tuple[int, int]] = []
        for r in range(self.size):
            for c in range(self.size):
                if self.board[r][c] != EMPTY:
                    occupied.append((r, c))

        if not occupied:
            center = self.size // 2
            return [Move(center, center)]

        candidates = set()
        for r, c in occupied:
            for dr in range(-radius, radius + 1):
                for dc in range(-radius, radius + 1):
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < self.size and 0 <= nc < self.size and self.board[nr][nc] == EMPTY:
                        candidates.add((nr, nc))

        if not candidates:
            return [
                Move(r, c)
                for r in range(self.size)
                for c in range(self.size)
                if self.board[r][c] == EMPTY
            ]

        return [Move(r, c) for r, c in candidates]

    def check_winner(self, last_move: Optional[Move] = None) -> Optional[str]:
        if last_move is not None:
            player = self.board[last_move.row][last_move.col]
            if player == EMPTY:
                return None
            if self._is_winning_position(last_move.row, last_move.col, player):
                return player
            return None

        for r in range(self.size):
            for c in range(self.size):
                player = self.board[r][c]
                if player != EMPTY and self._is_winning_position(r, c, player):
                    return player
        return None

    def _is_winning_position(self, row: int, col: int, player: str) -> bool:
        directions = ((1, 0), (0, 1), (1, 1), (1, -1))
        for dr, dc in directions:
            count = 1
            count += self._count_one_side(row, col, dr, dc, player)
            count += self._count_one_side(row, col, -dr, -dc, player)
            if count >= self.win_len:
                return True
        return False

    def _count_one_side(self, row: int, col: int, dr: int, dc: int, player: str) -> int:
        cnt = 0
        r, c = row + dr, col + dc
        while 0 <= r < self.size and 0 <= c < self.size and self.board[r][c] == player:
            cnt += 1
            r += dr
            c += dc
        return cnt

    def serialize(self) -> str:
        return "".join("".join(row) for row in self.board)

    def print_board(self) -> None:
        header = "    " + " ".join(f"{i + 1:2d}" for i in range(self.size))
        print(header)
        for idx, row in enumerate(self.board):
            print(f"{idx + 1:2d} | " + " ".join(f"{cell:2s}" for cell in row))
