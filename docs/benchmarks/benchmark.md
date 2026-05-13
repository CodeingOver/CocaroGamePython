# Báo cáo benchmark AI Cờ Caro - So sánh thuật toán

- Thời gian chạy: 2026-05-13 15:12:24
- Tiêu chí đạt: Thời gian phản hồi <= Budget + 50ms (sai số cho phép)

## Giải thích ý nghĩa các cột

- **Thuật toán**: Chế độ AI (AB+GBFS = mục tiêu chính; AB Only, GBFS Only, Minimax = dùng để so sánh).
- **Bàn cờ**: Kích thước lưới (ví dụ: 10 nghĩa là 10x10).
- **Win_len**: Số quân liên tiếp cần thiết để thắng.
- **Cấu hình**: Mức độ khó của AI (Khó, Cực khó, Địa ngục).
- **Mẫu**: Số lượng lượt đánh AI đã thực hiện để lấy dữ liệu.
- **Budget (ms)**: Ngân sách thời gian tối đa cho phép AI tính toán.
- **Avg (ms)**: Thời gian phản hồi trung bình.
- **Avg Nút**: Trung bình số nút trong cây tìm kiếm đã duyệt qua.
- **Avg Cắt tỉa**: Trung bình số lần Alpha-Beta cắt tỉa thành công (0 nếu AB tắt).
- **Vượt Budget**: Số lần AI tính toán lâu hơn ngân sách cho phép (+50ms buffer).
- **Kết luận**: Đạt (nếu không vượt ngân sách) hoặc Chưa đạt.

## Tổng hợp so sánh thuật toán

| Thuật toán | Bàn cờ | Cấu hình | Mẫu | Budget (ms) | Avg (ms) | P95 | Max | Avg Nút | Avg Cắt tỉa | Vượt Budget | Kết luận |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| AB + GBFS | 10 | Khó | 3 | 1000 | 274.944 | 310.704 | 312.979 | 2768 | 357 | 0 | Đạt |
| AB Only | 10 | Khó | 3 | 1000 | 128.461 | 205.205 | 214.786 | 3769 | 431 | 0 | Đạt |
| GBFS Only | 10 | Khó | 3 | 1000 | 956.036 | 1000.078 | 1000.081 | 19934 | 0 | 0 | Đạt |
| Minimax | 10 | Khó | 3 | 1000 | 1000.12 | 1000.206 | 1000.22 | 22263 | 0 | 0 | Đạt |

## Chi tiết từng lượt

| Thuật toán | Bàn cờ | Cấu hình | Kịch bản | Lần chạy | Thời gian (ms) | Nút | Cắt tỉa | Nước đi | OK |
|---|---:|---|---|---:|---:|---:|---:|---|---|
| AB + GBFS | 10 | Khó | Khai cuộc cân bằng | 1 | 312.979 | 5744 | 582 | (3,4) | True |
| AB + GBFS | 10 | Khó | Trung cuộc tranh chấp | 1 | 290.23 | 2062 | 340 | (4,8) | True |
| AB + GBFS | 10 | Khó | Tải cao gần cuối ván | 1 | 221.622 | 498 | 148 | (4,0) | True |
| AB Only | 10 | Khó | Khai cuộc cân bằng | 1 | 214.786 | 7242 | 687 | (3,4) | True |
| AB Only | 10 | Khó | Trung cuộc tranh chấp | 1 | 118.98 | 3168 | 383 | (4,3) | True |
| AB Only | 10 | Khó | Tải cao gần cuối ván | 1 | 51.617 | 896 | 224 | (4,0) | True |
| GBFS Only | 10 | Khó | Khai cuộc cân bằng | 1 | 1000.053 | 29565 | 0 | (7,6) | True |
| GBFS Only | 10 | Khó | Trung cuộc tranh chấp | 1 | 1000.081 | 22816 | 0 | (4,8) | True |
| GBFS Only | 10 | Khó | Tải cao gần cuối ván | 1 | 867.974 | 7420 | 0 | (4,0) | True |
| Minimax | 10 | Khó | Khai cuộc cân bằng | 1 | 1000.075 | 32837 | 0 | (7,6) | True |
| Minimax | 10 | Khó | Trung cuộc tranh chấp | 1 | 1000.065 | 23963 | 0 | (4,3) | True |
| Minimax | 10 | Khó | Tải cao gần cuối ván | 1 | 1000.22 | 9990 | 0 | (4,0) | True |