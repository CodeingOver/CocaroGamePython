### 2026-04-24

- Bổ sung tầng sàng lọc GBFS vào luồng chọn nước đi của AI để ưu tiên các ứng viên tốt trước khi Minimax duyệt sâu.
- Thêm chú thích giải thích các khối logic quan trọng trong `ai.py`, `heuristics.py`, `game.py`, `gui.py` và `cli.py`.
- Cập nhật nhãn hiển thị ở giao diện và terminal để phản ánh đúng chuỗi thuật toán GBFS + Minimax + Alpha-Beta.

- Bổ sung `benchmark.py` để đo độ trễ AI theo các cấu hình GUI/CLI trên bàn cờ 10x10, xuất báo cáo `.md` và `.csv` trong `docs/benchmarks/`.
- Bổ sung `tactical_tests.py` để kiểm thử các tình huống chiến thuật bắt buộc (thắng ngay, chặn ngay, kết thúc đường chéo).
- Hoàn thiện chú thích mã nguồn theo định dạng comment `#` (không dùng docstring) trong các module chính để phù hợp báo cáo môn Trí tuệ nhân tạo.
- Cập nhật tài liệu `README.md` và `docs/architecture.md` để đồng bộ với luồng benchmark/kiểm thử mới.

- Loại bỏ chế độ chạy CLI: xóa `cli.py`, cập nhật `main.py` để chỉ chạy giao diện GUI.
- Nâng `benchmark.py` để hỗ trợ bàn cờ tùy chỉnh qua `--sizes` (ví dụ `10,12,15`) thay vì cố định theo kịch bản 10x10.
- Cập nhật lại tài liệu kiến trúc và hướng dẫn chạy để phản ánh việc bỏ CLI và benchmark đa kích thước bàn cờ.
- Sửa lỗi `TclError` trong GUI khi ô `Spinbox` bị để trống: thêm hàm đọc số an toàn và kiểm tra hợp lệ trước khi áp dụng cấu hình tùy chỉnh, bắt đầu ván mới, hoặc để AI tính nước đi.
- Sửa hành vi AI có xu hướng nối thẳng thiếu phản ứng theo đúng pipeline đề tài GBFS + Minimax: tinh chỉnh chấm điểm GBFS, cải thiện sinh ứng viên và cơ chế ordering/cache theo độ sâu, không tách thêm tầng thuật toán ngoài GBFS/Minimax.
