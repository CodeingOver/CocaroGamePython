# Nhật ký thay đổi (CHANGELOG)

Tất cả các thay đổi quan trọng đối với dự án này sẽ được ghi lại trong tệp này.

## [1.1.4] - 2026-05-13

### **[Cập nhật]**
- **Đồng bộ hóa cấu hình**:
    - Cập nhật ngân sách thời gian (`time_ms`) trong `tests/benchmark.py` và `tests/tactical_tests.py` để khớp hoàn toàn với các thiết lập mới trong Giao diện (GUI):
        - Mức Khó: 1000ms.
        - Mức Cực khó: 1500ms.
        - Mức Địa ngục: 2000ms.

## [1.1.3] - 2026-05-13

### **[Cập nhật]**
- **Cải tiến công cụ Benchmark**:
    - Bổ sung phần giải thích ý nghĩa chi tiết của từng cột dữ liệu trong báo cáo Markdown.
    - Cố định tên tệp xuất ra là `benchmark.md` và `benchmark.csv` (loại bỏ phần thời gian đằng sau) để dễ dàng quản lý và ghi đè khi chạy lại.

## [1.1.2] - 2026-05-13

### **[Cập nhật]**
- **Tối ưu hóa hiệu năng**:
    - Tối ưu `evaluate_board`: Loại bỏ các lượt quét bàn cờ dư thừa và gộp các vòng lặp tính điểm.
    - Cải tiến `minimax`: Giới hạn việc sắp xếp nước đi (GBFS) chỉ thực hiện ở các tầng nông để giảm độ phức tạp tính toán ở các nút sâu.
    - Nâng cấp `CaroGame`: Duy trì danh sách `occupied_cells` để tìm kiếm ứng viên nhanh hơn, không cần quét toàn bộ bàn cờ.
- **Ổn định hệ thống**:
    - Bổ sung kiểm tra `deadline` trong mọi giai đoạn tìm kiếm (bao gồm cả lúc sắp xếp nước đi) để đảm bảo AI luôn trả về đúng giới hạn thời gian.
    - Thêm nhật ký tiến trình (progress log) trong công cụ benchmark để người dùng dễ dàng theo dõi.

## [1.1.1] - 2026-05-13

### **[Cập nhật]**
- **Cấu trúc thư mục**:
    - Di chuyển các tệp liên quan đến kiểm thử và đo lường hiệu năng (`benchmark.py`, `tactical_tests.py`) vào thư mục mới `tests/` để làm gọn thư mục gốc.
    - Cập nhật cơ chế `sys.path` trong các tệp kiểm thử để đảm bảo khả năng thực thi độc lập từ thư mục `tests/`.
- **Tài liệu**:
    - Cập nhật `README.md` và `docs/architecture.md` để phản ánh đúng cấu trúc thư mục mới và hướng dẫn chạy kiểm thử.

## [1.1.0] - 2026-05-11

### **[Cập nhật]**
- **Tài liệu hệ thống**:
    - Viết lại toàn bộ `README.md` với cấu trúc chuyên nghiệp, đầy đủ hướng dẫn cài đặt và sử dụng.
    - Cập nhật `docs/architecture.md` theo chuẩn 8 phần, bổ sung sơ đồ Mermaid (Flowchart, Sequence Diagram, ER Diagram) để trực quan hóa luồng dữ liệu và cấu trúc AI.
    - Bổ sung `docs/algorithm_details.md` giải thích chi tiết step-by-step các thuật toán GBFS, Minimax, Alpha-Beta, Heuristic, Iterative Deepening kèm code thực tế và bảng phân tích hiệu năng.
- **Tiêu chuẩn hóa**:
    - Chỉnh sửa ngôn ngữ trong toàn bộ tài liệu sang Tiếng Việt có dấu chuẩn ngữ pháp.
    - Đồng bộ hóa các thuật ngữ kỹ thuật (GBFS, Minimax, Alpha-Beta) xuyên suốt các tệp hướng dẫn.

## [1.0.0] - 2026-04-24

### **[Thêm mới]**
- **Lõi AI**:
    - Tích hợp thuật toán GBFS để sàng lọc ứng viên.
    - Triển khai Minimax kết hợp Alpha-Beta Pruning.
- **Công cụ kiểm thử**:
    - Thêm `benchmark.py` để đo hiệu năng đa kích thước bàn cờ.
    - Thêm `tactical_tests.py` để kiểm tra các thế cờ chiến thuật.
- **Giao diện**:
    - Hoàn thiện giao diện Tkinter hỗ trợ tùy chỉnh thông số bàn cờ.

### **[Sửa lỗi]**
- Khắc phục lỗi `TclError` khi ô nhập liệu trong GUI bị trống.
- Tinh chỉnh hàm Heuristic để AI nhận diện tốt hơn các thế cờ "Open Three" và "Open Four".

### **[Xóa bỏ]**
- Loại bỏ hoàn toàn chế độ chạy dòng lệnh (CLI) để tập trung vào trải nghiệm GUI.
