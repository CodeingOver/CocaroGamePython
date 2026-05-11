# Nhật ký thay đổi (CHANGELOG)

Tất cả các thay đổi quan trọng đối với dự án này sẽ được ghi lại trong tệp này.

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
