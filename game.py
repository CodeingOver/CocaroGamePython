from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple

from constants import EMPTY


@dataclass(frozen=True)
class Move:
    # Tọa độ một nước đi trên bàn cờ.
    row: int
    col: int


class CaroGame:
    def __init__(self, size: int = 10, win_len: int = 5) -> None:
        # Khởi tạo trạng thái bàn cờ rỗng với kích thước và luật thắng tùy chỉnh.

        self.size = size
        self.win_len = win_len
        self.board: List[List[str]] = [[EMPTY for _ in range(size)] for _ in range(size)]
        self.occupied_cells: List[Tuple[int, int]] = []

    def is_valid_move(self, move: Move) -> bool:
        # Kiểm tra nước đi có nằm trong bàn và đang ở ô trống hay không.

        return (
            0 <= move.row < self.size
            and 0 <= move.col < self.size
            and self.board[move.row][move.col] == EMPTY
        )

    def make_move(self, move: Move, player: str) -> None:
        # Đánh một quân của player tại vị trí move.

        self.board[move.row][move.col] = player
        self.occupied_cells.append((move.row, move.col))

    def undo_move(self, move: Move) -> None:
        # Hoàn tác một nước đi, trả ô về trạng thái trống.

        self.board[move.row][move.col] = EMPTY
        if self.occupied_cells:
            # remove() sẽ xóa phần tử cuối cùng khớp, vì undo thường là theo LIFO nên pop() hoặc remove() đều ổn.
            # Ở đây dùng remove để đảm bảo đúng tọa độ.
            self.occupied_cells.remove((move.row, move.col))

    def is_full(self) -> bool:
        # Kiểm tra bàn cờ đã kín hoàn toàn hay chưa.

        return len(self.occupied_cells) == self.size * self.size

    def get_candidate_moves(self, radius: int = 1) -> List[Move]:
        # Sinh danh sách ứng viên gần các quân đã có để giảm branching factor.
        # radius nhỏ giúp AI tập trung vào vùng có tương tác chiến thuật, tránh duyệt toàn bàn.

        # Sử dụng danh sách occupied_cells đã được duy trì để tránh quét toàn bàn.
        if not self.occupied_cells:
            center = self.size // 2
            return [Move(center, center)]

        # Giai đoạn đầu ván cần mở rộng bán kính để tránh bị "khóa tầm nhìn" vào một trục thẳng.
        adaptive_radius = radius
        if len(self.occupied_cells) <= max(6, self.win_len):
            adaptive_radius = max(radius, 2)

        candidates = set()
        for r, c in self.occupied_cells:
            for dr in range(-adaptive_radius, adaptive_radius + 1):
                for dc in range(-adaptive_radius, adaptive_radius + 1):
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
        # Trả về người thắng nếu đã có chuỗi thắng, ngược lại trả về None.
        # Nếu có last_move thì chỉ cần kiểm tra quanh nước đi cuối để tăng tốc.

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
        # Kiểm tra một vị trí có tạo đủ chuỗi thắng theo 4 hướng cơ bản không.

        directions = ((1, 0), (0, 1), (1, 1), (1, -1))
        for dr, dc in directions:
            count = 1
            count += self._count_one_side(row, col, dr, dc, player)
            count += self._count_one_side(row, col, -dr, -dc, player)
            if count >= self.win_len:
                return True
        return False

    def _count_one_side(self, row: int, col: int, dr: int, dc: int, player: str) -> int:
        # Đếm liên tiếp số quân cùng loại về một phía theo vector hướng.

        cnt = 0
        r, c = row + dr, col + dc
        while 0 <= r < self.size and 0 <= c < self.size and self.board[r][c] == player:
            cnt += 1
            r += dr
            c += dc
        return cnt

    def serialize(self) -> str:
        # Mã hóa trạng thái bàn cờ thành chuỗi để dùng làm khóa cache.

        return "".join("".join(row) for row in self.board)

    def print_board(self) -> None:
        # In bàn cờ dạng lưới ra terminal để debug nhanh trạng thái game.

        header = "    " + " ".join(f"{i + 1:2d}" for i in range(self.size))
        print(header)
        for idx, row in enumerate(self.board):
            print(f"{idx + 1:2d} | " + " ".join(f"{cell:2s}" for cell in row))
