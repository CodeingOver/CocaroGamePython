from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from typing import List, Optional

from ai import ai_best_move
from constants import AI_MARK, EMPTY, HUMAN_MARK, MAX_BOARD_SIZE, MIN_BOARD_SIZE
from game import CaroGame, Move


DIFFICULTY_ORDER = ["de", "binh_thuong", "kho", "cuc_kho", "dia_nguc"]
# Preset độ khó chuẩn để kiểm soát trade-off giữa chất lượng nước đi và thời gian phản hồi.
DIFFICULTY_PRESETS = {
    "de": {
        "name": "Dễ",
        "depth": 2,
        "candidates": 8,
        "time_ms": 250,
        "description": "AI phản hồi nhanh, phù hợp để làm quen.",
    },
    "binh_thuong": {
        "name": "Bình thường",
        "depth": 3,
        "candidates": 12,
        "time_ms": 500,
        "description": "Cân bằng giữa tốc độ và độ khó.",
    },
    "kho": {
        "name": "Khó",
        "depth": 4,
        "candidates": 14,
        "time_ms": 1000,
        "description": "AI nhìn xa hơn và phòng thủ tốt hơn.",
    },
    "cuc_kho": {
        "name": "Cực khó",
        "depth": 5,
        "candidates": 16,
        "time_ms": 1500,
        "description": "Độ chính xác cao, có thể tính chậm trên bàn lớn.",
    },
    "dia_nguc": {
        "name": "Địa ngục",
        "depth": 6,
        "candidates": 18,
        "time_ms": 2000,
        "description": "Rất mạnh, phù hợp để thử thách. Có thể mất thời gian suy nghĩ.",
    },
}


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
    # Gợi ý số ứng viên trên mỗi lớp Minimax để tránh nổ số nhánh.
    if size <= 5:
        return size * size
    if size <= 8:
        return 14
    return 12


class CaroGUI:
    def __init__(self, root: tk.Tk) -> None:
        # Khởi tạo cửa sổ, trạng thái ván đấu và toàn bộ biến điều khiển UI.
        self.root = root
        self.root.title("Cờ Caro AI - GBFS + Minimax")
        self.root.minsize(760, 680)

        self.palette = {
            "bg": "#eef2ff",
            "surface": "#ffffff",
            "surface_alt": "#f8faff",
            "text": "#1f2937",
            "muted": "#5b6475",
            "accent": "#2563eb",
            "accent_active": "#1d4ed8",
            "border": "#d6deef",
            "cell_bg": "#ffffff",
            "cell_hover": "#eef4ff",
            "cell_border": "#cfd8ea",
            "last_move_bg": "#fff7d6",
        }

        self.game: Optional[CaroGame] = None
        self.buttons: List[List[tk.Button]] = []
        self.last_move: Optional[Move] = None
        self.highlighted_move: Optional[Move] = None
        self.human_turn = True
        self.game_over = False
        self.ai_thinking = False

        self.human_base_color = "#1f4e79"
        self.ai_base_color = "#8a1c1c"
        self.human_last_color = "#2f6fee"
        self.ai_last_color = "#d62839"

        self.size_var = tk.IntVar(value=10)
        self.win_len_var = tk.IntVar(value=5)
        self.depth_var = tk.IntVar(value=3)
        self.candidate_var = tk.IntVar(value=12)
        self.time_budget_var = tk.IntVar(value=250)
        self.difficulty_var = tk.StringVar(value="binh_thuong")
        self.difficulty_desc_var = tk.StringVar(value="")
        self.human_first_var = tk.BooleanVar(value=True)
        self.status_var = tk.StringVar(value="Chào mừng bạn đến với Cờ Caro AI")
        self.game_info_var = tk.StringVar(value="")

        self.root.configure(bg=self.palette["bg"])
        self.style = ttk.Style(self.root)
        self._configure_styles()

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.container = ttk.Frame(self.root, padding=16, style="App.TFrame")
        self.container.grid(row=0, column=0, sticky="nsew")
        self.container.columnconfigure(0, weight=1)
        self.container.rowconfigure(0, weight=1)

        self.menu_frame = ttk.Frame(self.container, style="App.TFrame")
        self.settings_frame = ttk.Frame(self.container, style="App.TFrame")
        self.game_frame = ttk.Frame(self.container, style="App.TFrame")

        self.board_frame = tk.Frame(self.game_frame, bg=self.palette["surface"], bd=0, highlightthickness=0)

        self._build_menu_screen()
        self._build_settings_screen()
        self._build_game_screen()
        self._apply_difficulty_profile(self.difficulty_var.get(), update_status=False)
        self._show_screen(self.menu_frame)

    def _configure_styles(self) -> None:
        # Cấu hình theme cho toàn bộ widget để giao diện nhất quán.
        self.style.theme_use("clam")
        self.style.configure("App.TFrame", background=self.palette["bg"])
        self.style.configure(
            "Card.TFrame",
            background=self.palette["surface"],
            borderwidth=1,
            relief="solid",
        )
        self.style.configure("Header.TLabel", background=self.palette["bg"], foreground=self.palette["text"])
        self.style.configure(
            "Title.TLabel",
            background=self.palette["bg"],
            foreground=self.palette["text"],
            font=("Segoe UI", 26, "bold"),
        )
        self.style.configure(
            "Subtitle.TLabel",
            background=self.palette["bg"],
            foreground=self.palette["muted"],
            font=("Segoe UI", 11),
        )
        self.style.configure(
            "SectionTitle.TLabel",
            background=self.palette["bg"],
            foreground=self.palette["text"],
            font=("Segoe UI", 16, "bold"),
        )
        self.style.configure(
            "Status.TLabel",
            background=self.palette["surface_alt"],
            foreground=self.palette["text"],
            font=("Segoe UI", 11, "bold"),
            padding=(10, 8),
        )
        self.style.configure(
            "Muted.TLabel",
            background=self.palette["surface_alt"],
            foreground=self.palette["muted"],
            font=("Segoe UI", 10),
            padding=(10, 0, 10, 8),
        )
        self.style.configure(
            "TLabelFrame",
            background=self.palette["surface"],
            bordercolor=self.palette["border"],
            borderwidth=1,
            relief="solid",
            padding=12,
        )
        self.style.configure("TLabelFrame.Label", background=self.palette["surface"], foreground=self.palette["text"])
        self.style.configure(
            "Primary.TButton",
            background=self.palette["accent"],
            foreground="#ffffff",
            borderwidth=0,
            focusthickness=0,
            focuscolor=self.palette["accent"],
            padding=(14, 8),
            font=("Segoe UI", 10, "bold"),
        )
        self.style.map(
            "Primary.TButton",
            background=[("active", self.palette["accent_active"]), ("pressed", self.palette["accent_active"])],
            foreground=[("disabled", "#e5e7eb")],
        )
        self.style.configure(
            "Soft.TButton",
            background=self.palette["surface_alt"],
            foreground=self.palette["text"],
            bordercolor=self.palette["border"],
            padding=(12, 7),
            font=("Segoe UI", 10),
        )
        self.style.map("Soft.TButton", background=[("active", "#e9efff")])

    def _show_screen(self, frame: ttk.Frame) -> None:
        # Chuyển giữa menu, màn cài đặt và màn chơi.
        self.menu_frame.grid_forget()
        self.settings_frame.grid_forget()
        self.game_frame.grid_forget()
        frame.grid(row=0, column=0, sticky="nsew")

    def _build_menu_screen(self) -> None:
        # Dựng màn hình menu chính.
        self.menu_frame.columnconfigure(0, weight=1)

        title = ttk.Label(
            self.menu_frame,
            text="CỜ CARO AI",
            style="Title.TLabel",
            anchor="center",
        )
        title.grid(row=0, column=0, pady=(60, 10), sticky="ew")

        subtitle = ttk.Label(
            self.menu_frame,
            text="GBFS + Minimax Alpha-Beta",
            style="Subtitle.TLabel",
            anchor="center",
        )
        subtitle.grid(row=1, column=0, pady=(0, 24), sticky="ew")

        menu_box = ttk.LabelFrame(self.menu_frame, text="Menu chính", padding=18)
        menu_box.grid(row=2, column=0, padx=170, sticky="ew")
        menu_box.columnconfigure(0, weight=1)

        ttk.Button(menu_box, text="Bắt đầu", style="Primary.TButton", command=self.start_game_from_menu).grid(
            row=0, column=0, sticky="ew", pady=(0, 8)
        )
        ttk.Button(
            menu_box,
            text="Cài đặt",
            style="Soft.TButton",
            command=lambda: self._show_screen(self.settings_frame),
        ).grid(
            row=1, column=0, sticky="ew", pady=(0, 8)
        )
        ttk.Button(menu_box, text="Hướng dẫn", style="Soft.TButton", command=self.show_help).grid(
            row=2, column=0, sticky="ew", pady=(0, 8)
        )
        ttk.Button(menu_box, text="Thoát", style="Soft.TButton", command=self.root.destroy).grid(row=3, column=0, sticky="ew")

        tagline = ttk.Label(
            self.menu_frame,
            text="Mẹo: mở Cài đặt để chọn độ khó phù hợp trước khi chơi.",
            style="Subtitle.TLabel",
            anchor="center",
        )
        tagline.grid(row=3, column=0, pady=(14, 0), sticky="ew")

    def _build_settings_screen(self) -> None:
        # Dựng màn hình cài đặt gồm luật chơi, độ khó preset và tùy chỉnh nâng cao.
        self.settings_frame.columnconfigure(0, weight=1)

        title = ttk.Label(self.settings_frame, text="Cài đặt trò chơi", style="SectionTitle.TLabel")
        title.grid(row=0, column=0, sticky="w", pady=(0, 10))

        control = ttk.LabelFrame(self.settings_frame, text="Thông số bàn cờ", padding=12)
        control.grid(row=1, column=0, sticky="ew")

        ttk.Label(control, text="Kích thước bàn:").grid(row=0, column=0, sticky="w")
        ttk.Spinbox(control, from_=MIN_BOARD_SIZE, to=MAX_BOARD_SIZE, width=8, textvariable=self.size_var).grid(
            row=0, column=1, padx=(8, 18)
        )

        ttk.Label(control, text="Thắng với:").grid(row=0, column=2, sticky="w")
        ttk.Spinbox(control, from_=MIN_BOARD_SIZE, to=MAX_BOARD_SIZE, width=8, textvariable=self.win_len_var).grid(
            row=0, column=3, padx=(8, 0)
        )

        first_frame = ttk.Frame(control)
        first_frame.grid(row=1, column=0, columnspan=4, sticky="w", pady=(12, 0))
        ttk.Radiobutton(first_frame, text="Bạn đi trước", variable=self.human_first_var, value=True).grid(row=0, column=0)
        ttk.Radiobutton(first_frame, text="AI đi trước", variable=self.human_first_var, value=False).grid(
            row=0, column=1, padx=(12, 0)
        )

        difficulty_frame = ttk.LabelFrame(self.settings_frame, text="Độ khó AI", padding=12)
        difficulty_frame.grid(row=2, column=0, sticky="ew", pady=(12, 0))
        difficulty_frame.columnconfigure(0, weight=1)

        ttk.Label(
            difficulty_frame,
            text="Chọn mức có sẵn để dễ thiết lập:",
            style="Header.TLabel",
        ).grid(row=0, column=0, sticky="w")

        for idx, key in enumerate(DIFFICULTY_ORDER, start=1):
            preset = DIFFICULTY_PRESETS[key]
            text = (
                f"{preset['name']} (độ sâu {preset['depth']}, ứng viên {preset['candidates']}, "
                f"{preset['time_ms']}ms/nước)"
            )
            ttk.Radiobutton(
                difficulty_frame,
                text=text,
                variable=self.difficulty_var,
                value=key,
                command=self._on_difficulty_selected,
            ).grid(row=idx, column=0, sticky="w", pady=(4, 0))

        ttk.Label(
            difficulty_frame,
            textvariable=self.difficulty_desc_var,
            style="Header.TLabel",
            wraplength=640,
        ).grid(row=idx + 1, column=0, sticky="w", pady=(10, 0))

        advanced_frame = ttk.LabelFrame(self.settings_frame, text="Tùy chỉnh nâng cao", padding=12)
        advanced_frame.grid(row=3, column=0, sticky="ew", pady=(12, 0))
        ttk.Label(advanced_frame, text="Độ sâu AI:").grid(row=0, column=0, sticky="w")
        ttk.Spinbox(advanced_frame, from_=1, to=10, width=8, textvariable=self.depth_var).grid(
            row=0,
            column=1,
            padx=(8, 18),
        )
        ttk.Label(advanced_frame, text="Ứng viên mỗi lớp:").grid(row=0, column=2, sticky="w")
        ttk.Spinbox(advanced_frame, from_=4, to=MAX_BOARD_SIZE * MAX_BOARD_SIZE, width=8, textvariable=self.candidate_var).grid(
            row=0,
            column=3,
            padx=(8, 0),
        )
        ttk.Label(advanced_frame, text="Giới hạn thời gian/nước (ms):").grid(row=1, column=0, sticky="w", pady=(10, 0))
        ttk.Spinbox(advanced_frame, from_=50, to=5000, width=8, textvariable=self.time_budget_var).grid(
            row=1,
            column=1,
            padx=(8, 18),
            pady=(10, 0),
        )
        ttk.Button(
            advanced_frame,
            text="Dùng cấu hình tùy chỉnh",
            style="Soft.TButton",
            command=self.apply_custom_difficulty,
        ).grid(row=2, column=0, columnspan=4, sticky="w", pady=(10, 0))

        action = ttk.Frame(self.settings_frame)
        action.grid(row=4, column=0, sticky="w", pady=(12, 0))
        ttk.Button(
            action,
            text="Quay lại menu",
            style="Soft.TButton",
            command=lambda: self._show_screen(self.menu_frame),
        ).grid(
            row=0, column=0
        )
        ttk.Button(action, text="Vào chơi", style="Primary.TButton", command=self.start_game_from_menu).grid(
            row=0,
            column=1,
            padx=(8, 0),
        )

    def _build_game_screen(self) -> None:
        # Dựng màn hình ván đấu: thanh điều khiển, trạng thái và khu vực bàn cờ.
        self.game_frame.columnconfigure(0, weight=1)
        self.game_frame.rowconfigure(2, weight=1)

        top = ttk.Frame(self.game_frame)
        top.grid(row=0, column=0, sticky="ew")
        ttk.Button(top, text="Ván mới", style="Primary.TButton", command=self.start_new_game).grid(row=0, column=0)
        ttk.Button(top, text="Menu chính", style="Soft.TButton", command=self.back_to_menu).grid(row=0, column=1, padx=(8, 0))
        ttk.Button(top, text="Thoát", style="Soft.TButton", command=self.root.destroy).grid(row=0, column=2, padx=(8, 0))

        info_card = ttk.Frame(self.game_frame, style="Card.TFrame")
        info_card.grid(row=1, column=0, sticky="ew", pady=(12, 10))
        info_card.columnconfigure(0, weight=1)
        status = ttk.Label(info_card, textvariable=self.status_var, style="Status.TLabel")
        status.grid(row=0, column=0, sticky="ew")
        game_info = ttk.Label(info_card, textvariable=self.game_info_var, style="Muted.TLabel")
        game_info.grid(row=1, column=0, sticky="ew")

        self.board_frame.grid(row=2, column=0, sticky="nsew")

    def _on_difficulty_selected(self) -> None:
        # Đồng bộ tham số khi người dùng đổi preset độ khó.
        self._apply_difficulty_profile(self.difficulty_var.get(), update_status=True)

    def _apply_difficulty_profile(self, key: str, update_status: bool = True) -> None:
        # Áp preset vào các biến AI: depth, candidate limit và time budget.
        preset = DIFFICULTY_PRESETS.get(key)
        if preset is None:
            return

        self.depth_var.set(preset["depth"])
        self.candidate_var.set(preset["candidates"])
        self.time_budget_var.set(preset["time_ms"])
        self.difficulty_desc_var.set(
            f"{preset['name']}: {preset['description']}"
        )

        if update_status:
            self.status_var.set(
                (
                    f"Đã chọn độ khó {preset['name']} (độ sâu {preset['depth']}, ứng viên {preset['candidates']}, "
                    f"{preset['time_ms']}ms/nước)"
                )
            )

    def _read_int_var(
        self,
        var: tk.IntVar,
        field_name: str,
        min_value: Optional[int] = None,
        max_value: Optional[int] = None,
    ) -> Optional[int]:
        # Đọc IntVar an toàn để tránh lỗi TclError khi người dùng để trống Spinbox.
        try:
            value = var.get()
        except tk.TclError:
            messagebox.showerror("Lỗi nhập liệu", f"{field_name} phải là số nguyên hợp lệ.")
            return None

        if min_value is not None and value < min_value:
            messagebox.showerror("Lỗi nhập liệu", f"{field_name} phải >= {min_value}.")
            return None

        if max_value is not None and value > max_value:
            messagebox.showerror("Lỗi nhập liệu", f"{field_name} phải <= {max_value}.")
            return None

        return value
    
    def apply_custom_difficulty(self) -> None:
        # Chuyển sang chế độ tùy chỉnh nhưng vẫn giữ luồng xử lý giống preset.
        depth = self._read_int_var(self.depth_var, "Độ sâu AI", min_value=1, max_value=50)
        if depth is None:
            return

        candidates = self._read_int_var(
            self.candidate_var,
            "Số ứng viên mỗi lớp",
            min_value=4,
            max_value=MAX_BOARD_SIZE * MAX_BOARD_SIZE,
        )
        if candidates is None:
            return

        time_ms = self._read_int_var(self.time_budget_var, "Giới hạn thời gian mỗi nước AI", min_value=50, max_value=5000)
        if time_ms is None:
            return

        self.difficulty_var.set("tuy_chinh")
        self.difficulty_desc_var.set(
            f"Tùy chỉnh: độ sâu {depth}, ứng viên {candidates}, {time_ms}ms/nước."
        )
        self.status_var.set("Đã áp dụng cấu hình tùy chỉnh")

    def _difficulty_name_for_info(self) -> str:
        # Lấy tên độ khó để hiển thị trong khung thông tin trận.
        key = self.difficulty_var.get()
        preset = DIFFICULTY_PRESETS.get(key)
        if preset is None:
            return "Tùy chỉnh"
        return preset["name"]

    def show_help(self) -> None:
        # Hiển thị luật chơi và gợi ý chọn tham số cơ bản.
        help_text = (
            "Luật chơi:\n"
            "- Bạn đánh O, AI đánh X.\n"
            "- Mỗi lượt chọn 1 ô trống.\n"
            "- Tạo đủ số quân liên tiếp theo cài đặt để thắng.\n\n"
            "Gợi ý:\n"
            "- Bàn lớn nên để độ sâu 3-4 để AI phản hồi nhanh hơn."
        )
        messagebox.showinfo("Hướng dẫn", help_text)

    def start_game_from_menu(self) -> None:
        # Vào màn chơi và khởi tạo ván mới ngay từ menu.
        self._show_screen(self.game_frame)
        self.start_new_game()

    def back_to_menu(self) -> None:
        # Hủy trạng thái ván hiện tại và quay lại menu chính.
        self.game_over = True
        self.ai_thinking = False
        self.highlighted_move = None
        self.status_var.set("Chào mừng bạn đến với Cờ Caro AI")
        self._show_screen(self.menu_frame)

    def start_new_game(self) -> None:
        # Khởi tạo ván mới với bộ tham số hiện tại từ màn cài đặt.
        size = self._read_int_var(self.size_var, "Kích thước bàn cờ", min_value=MIN_BOARD_SIZE, max_value=MAX_BOARD_SIZE)
        if size is None:
            return

        win_len = self._read_int_var(self.win_len_var, "Số quân để thắng", min_value=MIN_BOARD_SIZE, max_value=size)
        if win_len is None:
            return

        depth = self._read_int_var(self.depth_var, "Độ sâu AI", min_value=1, max_value=10)
        if depth is None:
            return

        candidates = self._read_int_var(
            self.candidate_var,
            "Số ứng viên mỗi lớp",
            min_value=4,
            max_value=size * size,
        )
        if candidates is None:
            return

        time_budget = self._read_int_var(self.time_budget_var, "Giới hạn thời gian mỗi nước AI", min_value=50, max_value=5000)
        if time_budget is None:
            return

        if size < MIN_BOARD_SIZE or size > MAX_BOARD_SIZE:
            messagebox.showerror(
                "Lỗi",
                f"Kích thước bàn cờ phải trong khoảng {MIN_BOARD_SIZE}-{MAX_BOARD_SIZE}",
            )
            return

        if win_len < MIN_BOARD_SIZE:
            messagebox.showerror("Lỗi", f"Số quân để thắng phải >= {MIN_BOARD_SIZE}")
            return

        if win_len > size:
            messagebox.showerror("Lỗi", "Số quân để thắng không được lớn hơn kích thước bàn cờ")
            return

        self.game = CaroGame(size=size, win_len=win_len)
        self.last_move = None
        self.highlighted_move = None
        self.human_turn = self.human_first_var.get()
        self.game_over = False
        self.ai_thinking = False
        self.game_info_var.set(
            (
                f"Bàn {size}x{size} | Thắng với {win_len} | Độ khó {self._difficulty_name_for_info()} | "
                f"Độ sâu {depth} | Ứng viên {candidates} | {time_budget}ms/nước"
            )
        )

        self._build_board(size)

        if self.human_turn:
            self.status_var.set("Lượt của bạn")
            self._set_board_enabled(True)
        else:
            self.status_var.set("AI đang tính nước đầu tiên")
            self._set_board_enabled(False)
            self.root.after(80, self.perform_ai_move)

    def _build_board(self, size: int) -> None:
        # Tạo lưới nút theo kích thước bàn cờ; tự điều chỉnh font theo size.
        for child in self.board_frame.winfo_children():
            child.destroy()

        for r in range(size):
            self.board_frame.rowconfigure(r, weight=1)
            self.board_frame.columnconfigure(r, weight=1)

        if size <= 8:
            font_size = 18
            cell_width = 3
        elif size <= 12:
            font_size = 14
            cell_width = 2
        else:
            font_size = 11
            cell_width = 2

        self.buttons = []
        for r in range(size):
            row_buttons: List[tk.Button] = []
            for c in range(size):
                btn = tk.Button(
                    self.board_frame,
                    text=EMPTY,
                    width=cell_width,
                    height=1,
                    font=("Segoe UI", font_size, "bold"),
                    relief="flat",
                    bd=0,
                    bg=self.palette["cell_bg"],
                    fg="#6b7280",
                    activebackground=self.palette["cell_hover"],
                    activeforeground="#6b7280",
                    disabledforeground="#6b7280",
                    highlightthickness=1,
                    highlightbackground=self.palette["cell_border"],
                    cursor="hand2",
                    command=lambda rr=r, cc=c: self.on_cell_click(rr, cc),
                )
                btn.grid(row=r, column=c, sticky="nsew", padx=2, pady=2)
                btn.bind("<Enter>", lambda _e, rr=r, cc=c: self._on_cell_hover(rr, cc, enter=True))
                btn.bind("<Leave>", lambda _e, rr=r, cc=c: self._on_cell_hover(rr, cc, enter=False))
                row_buttons.append(btn)
            self.buttons.append(row_buttons)

    def _on_cell_hover(self, row: int, col: int, enter: bool) -> None:
        # Hiệu ứng hover chỉ bật ở lượt người chơi và trên ô trống.
        if self.game is None or self.ai_thinking or self.game_over or not self.human_turn:
            return
        if self.game.board[row][col] != EMPTY:
            return

        btn = self.buttons[row][col]
        btn.configure(bg=self.palette["cell_hover"] if enter else self.palette["cell_bg"])

    def on_cell_click(self, row: int, col: int) -> None:
        # Xử lý lượt đánh của người chơi, sau đó chuyển lượt cho AI.
        if self.game is None or self.game_over or self.ai_thinking or not self.human_turn:
            return

        move = Move(row, col)
        if not self.game.is_valid_move(move):
            return

        self.game.make_move(move, HUMAN_MARK)
        self.last_move = move
        self._render_move(move)

        if self._finish_if_terminal():
            return

        self.human_turn = False
        self.status_var.set("AI đang tính...")
        self.root.after(50, self.perform_ai_move)

    def perform_ai_move(self) -> None:
        # Gọi bộ chọn nước đi AI với cấu hình hiện hành và cập nhật bàn cờ.
        if self.game is None or self.game_over:
            return

        self.ai_thinking = True
        self._set_board_enabled(False)

        try:
            depth = self._read_int_var(self.depth_var, "Độ sâu AI", min_value=1, max_value=10)
            max_candidates = self._read_int_var(
                self.candidate_var,
                "Số ứng viên mỗi lớp",
                min_value=4,
                max_value=self.game.size * self.game.size,
            )
            time_budget = self._read_int_var(self.time_budget_var, "Giới hạn thời gian mỗi nước AI", min_value=50, max_value=5000)

            if depth is None or max_candidates is None or time_budget is None:
                self.status_var.set("Cấu hình AI không hợp lệ. Vui lòng kiểm tra cài đặt.")
                return

            move = ai_best_move(
                self.game,
                depth=depth,
                max_candidates=max_candidates,
                max_time_ms=time_budget,
            )
        finally:
            self.ai_thinking = False

        self.game.make_move(move, AI_MARK)
        self.last_move = move
        self._render_move(move)

        if self._finish_if_terminal():
            return

        self.human_turn = True
        self._set_board_enabled(True)
        self.status_var.set("Lượt của bạn")

    def _render_move(self, move: Move) -> None:
        # Vẽ nước đi mới và cập nhật highlight cho nước đi gần nhất.
        if self.game is None:
            return

        if self.highlighted_move is not None:
            prev = self.highlighted_move
            prev_mark = self.game.board[prev.row][prev.col]
            prev_btn = self.buttons[prev.row][prev.col]
            if prev_mark == HUMAN_MARK:
                prev_btn.configure(
                    fg=self.human_base_color,
                    disabledforeground=self.human_base_color,
                    bg=self.palette["cell_bg"],
                )
            elif prev_mark == AI_MARK:
                prev_btn.configure(
                    fg=self.ai_base_color,
                    disabledforeground=self.ai_base_color,
                    bg=self.palette["cell_bg"],
                )

        mark = self.game.board[move.row][move.col]
        btn = self.buttons[move.row][move.col]
        btn.configure(text=mark, state=tk.DISABLED)

        if mark == HUMAN_MARK:
            btn.configure(
                fg=self.human_last_color,
                disabledforeground=self.human_last_color,
                bg=self.palette["last_move_bg"],
            )
        elif mark == AI_MARK:
            btn.configure(
                fg=self.ai_last_color,
                disabledforeground=self.ai_last_color,
                bg=self.palette["last_move_bg"],
            )

        self.highlighted_move = move

    def _finish_if_terminal(self) -> bool:
        # Kiểm tra điều kiện kết thúc sau mỗi lượt; trả True nếu ván đã dừng.
        if self.game is None:
            return True

        winner = self.game.check_winner(self.last_move)
        if winner == HUMAN_MARK:
            self.game_over = True
            self._set_board_enabled(False)
            self.status_var.set("Bạn đã thắng")
            messagebox.showinfo("Kết quả", "Bạn đã thắng")
            return True

        if winner == AI_MARK:
            self.game_over = True
            self._set_board_enabled(False)
            self.status_var.set("AI thắng")
            messagebox.showinfo("Kết quả", "AI thắng")
            return True

        if self.game.is_full():
            self.game_over = True
            self._set_board_enabled(False)
            self.status_var.set("Hòa")
            messagebox.showinfo("Kết quả", "Trận đấu hòa")
            return True

        return False

    def _set_board_enabled(self, enabled: bool) -> None:
        # Khóa/mở thao tác click trên toàn bộ ô trống của bàn cờ.
        if self.game is None:
            return

        desired_state = tk.NORMAL if enabled else tk.DISABLED
        for r in range(self.game.size):
            for c in range(self.game.size):
                if self.game.board[r][c] == EMPTY:
                    self.buttons[r][c].configure(state=desired_state)


def main() -> None:
    # Điểm vào GUI.
    root = tk.Tk()
    CaroGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
