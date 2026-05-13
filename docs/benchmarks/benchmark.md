# Báo cáo benchmark AI Cờ Caro

- Thời gian chạy: 2026-05-13 14:50:52
- Tiêu chí đạt: Thời gian phản hồi <= Budget + 50ms (sai số cho phép)

## Giải thích ý nghĩa các cột

- **Bàn cờ**: Kích thước lưới (ví dụ: 10 nghĩa là 10x10).
- **Win_len**: Số quân liên tiếp cần thiết để thắng.
- **Cấu hình**: Mức độ khó của AI (Khó, Cực khó, Địa ngục).
- **Mẫu**: Số lượng lượt đánh AI đã thực hiện để lấy dữ liệu.
- **Budget (ms)**: Ngân sách thời gian tối đa cho phép AI tính toán.
- **Min / Avg / Max**: Thời gian phản hồi nhỏ nhất, trung bình và lớn nhất (ms).
- **P95**: 95th percentile - 95% số lượt đánh có thời gian phản hồi thấp hơn giá trị này.
- **Vượt Budget**: Số lần AI tính toán lâu hơn ngân sách cho phép (+50ms buffer).
- **Kết luận**: Đạt (nếu không vượt ngân sách) hoặc Chưa đạt.

## Tổng hợp theo cấu hình

| Bàn cờ | Win_len | Cấu hình | Mẫu | Budget (ms) | Min | Avg | P95 | Max | Vượt Budget | Kết luận |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---|
| 10 | 5 | Cực khó | 3 | 1500 | 576.107 | 973.434 | 1381.313 | 1433.617 | 0 | Đạt |
| 10 | 5 | Khó | 3 | 1000 | 223.821 | 275.205 | 308.275 | 310.119 | 0 | Đạt |
| 10 | 5 | Tùy chỉnh A | 3 | 1000 | 221.459 | 272.301 | 303.968 | 305.53 | 0 | Đạt |
| 10 | 5 | Tùy chỉnh B | 3 | 2000 | 1181.051 | 1727.201 | 2000.353 | 2000.372 | 0 | Đạt |
| 10 | 5 | Địa ngục | 3 | 2000 | 1159.042 | 1719.853 | 2000.319 | 2000.334 | 0 | Đạt |
| 12 | 5 | Cực khó | 3 | 1500 | 583.182 | 1009.063 | 1444.629 | 1500.285 | 0 | Đạt |
| 12 | 5 | Khó | 3 | 1000 | 224.605 | 296.71 | 360.06 | 366.884 | 0 | Đạt |
| 12 | 5 | Tùy chỉnh A | 3 | 1000 | 225.764 | 287.563 | 333.754 | 337.577 | 0 | Đạt |
| 12 | 5 | Tùy chỉnh B | 3 | 2000 | 1165.85 | 1722.146 | 2000.363 | 2000.381 | 0 | Đạt |
| 12 | 5 | Địa ngục | 3 | 2000 | 1171.995 | 1724.205 | 2000.344 | 2000.353 | 0 | Đạt |
| 15 | 5 | Cực khó | 3 | 1500 | 591.761 | 1023.666 | 1442.178 | 1492.818 | 0 | Đạt |
| 15 | 5 | Khó | 3 | 1000 | 229.748 | 291.729 | 328.798 | 330.318 | 0 | Đạt |
| 15 | 5 | Tùy chỉnh A | 3 | 1000 | 227.854 | 290.586 | 328.354 | 329.955 | 0 | Đạt |
| 15 | 5 | Tùy chỉnh B | 3 | 2000 | 1235.387 | 1745.329 | 2000.37 | 2000.387 | 0 | Đạt |
| 15 | 5 | Địa ngục | 3 | 2000 | 1193.888 | 1731.539 | 2000.487 | 2000.518 | 0 | Đạt |

## Chi tiết từng lượt

| Bàn cờ | Win_len | Cấu hình | Kịch bản | Lần chạy | Thời gian (ms) | Nước đi | OK |
|---:|---:|---|---|---:|---:|---|---|
| 10 | 5 | Khó | Khai cuộc cân bằng | 1 | 310.119 | (3,4) | True |
| 10 | 5 | Khó | Trung cuộc tranh chấp | 1 | 291.676 | (4,8) | True |
| 10 | 5 | Khó | Tải cao gần cuối ván | 1 | 223.821 | (4,0) | True |
| 10 | 5 | Cực khó | Khai cuộc cân bằng | 1 | 1433.617 | (3,4) | True |
| 10 | 5 | Cực khó | Trung cuộc tranh chấp | 1 | 910.579 | (4,8) | True |
| 10 | 5 | Cực khó | Tải cao gần cuối ván | 1 | 576.107 | (4,0) | True |
| 10 | 5 | Địa ngục | Khai cuộc cân bằng | 1 | 2000.334 | (3,4) | True |
| 10 | 5 | Địa ngục | Trung cuộc tranh chấp | 1 | 2000.184 | (4,8) | True |
| 10 | 5 | Địa ngục | Tải cao gần cuối ván | 1 | 1159.042 | (4,0) | True |
| 10 | 5 | Tùy chỉnh A | Khai cuộc cân bằng | 1 | 305.53 | (3,4) | True |
| 10 | 5 | Tùy chỉnh A | Trung cuộc tranh chấp | 1 | 289.913 | (4,8) | True |
| 10 | 5 | Tùy chỉnh A | Tải cao gần cuối ván | 1 | 221.459 | (4,0) | True |
| 10 | 5 | Tùy chỉnh B | Khai cuộc cân bằng | 1 | 2000.372 | (3,4) | True |
| 10 | 5 | Tùy chỉnh B | Trung cuộc tranh chấp | 1 | 2000.179 | (4,8) | True |
| 10 | 5 | Tùy chỉnh B | Tải cao gần cuối ván | 1 | 1181.051 | (4,0) | True |
| 12 | 5 | Khó | Khai cuộc cân bằng | 1 | 366.884 | (8,7) | True |
| 12 | 5 | Khó | Trung cuộc tranh chấp | 1 | 298.64 | (5,9) | True |
| 12 | 5 | Khó | Tải cao gần cuối ván | 1 | 224.605 | (4,0) | True |
| 12 | 5 | Cực khó | Khai cuộc cân bằng | 1 | 1500.285 | (8,7) | True |
| 12 | 5 | Cực khó | Trung cuộc tranh chấp | 1 | 943.722 | (5,9) | True |
| 12 | 5 | Cực khó | Tải cao gần cuối ván | 1 | 583.182 | (4,0) | True |
| 12 | 5 | Địa ngục | Khai cuộc cân bằng | 1 | 2000.353 | (4,5) | True |
| 12 | 5 | Địa ngục | Trung cuộc tranh chấp | 1 | 2000.266 | (5,9) | True |
| 12 | 5 | Địa ngục | Tải cao gần cuối ván | 1 | 1171.995 | (4,0) | True |
| 12 | 5 | Tùy chỉnh A | Khai cuộc cân bằng | 1 | 337.577 | (8,7) | True |
| 12 | 5 | Tùy chỉnh A | Trung cuộc tranh chấp | 1 | 299.348 | (5,9) | True |
| 12 | 5 | Tùy chỉnh A | Tải cao gần cuối ván | 1 | 225.764 | (4,0) | True |
| 12 | 5 | Tùy chỉnh B | Khai cuộc cân bằng | 1 | 2000.381 | (4,5) | True |
| 12 | 5 | Tùy chỉnh B | Trung cuộc tranh chấp | 1 | 2000.206 | (5,9) | True |
| 12 | 5 | Tùy chỉnh B | Tải cao gần cuối ván | 1 | 1165.85 | (4,0) | True |
| 15 | 5 | Khó | Khai cuộc cân bằng | 1 | 330.318 | (5,6) | True |
| 15 | 5 | Khó | Trung cuộc tranh chấp | 1 | 315.12 | (6,10) | True |
| 15 | 5 | Khó | Tải cao gần cuối ván | 1 | 229.748 | (4,0) | True |
| 15 | 5 | Cực khó | Khai cuộc cân bằng | 1 | 1492.818 | (5,6) | True |
| 15 | 5 | Cực khó | Trung cuộc tranh chấp | 1 | 986.419 | (6,10) | True |
| 15 | 5 | Cực khó | Tải cao gần cuối ván | 1 | 591.761 | (4,0) | True |
| 15 | 5 | Địa ngục | Khai cuộc cân bằng | 1 | 2000.518 | (5,6) | True |
| 15 | 5 | Địa ngục | Trung cuộc tranh chấp | 1 | 2000.211 | (6,10) | True |
| 15 | 5 | Địa ngục | Tải cao gần cuối ván | 1 | 1193.888 | (4,0) | True |
| 15 | 5 | Tùy chỉnh A | Khai cuộc cân bằng | 1 | 329.955 | (5,6) | True |
| 15 | 5 | Tùy chỉnh A | Trung cuộc tranh chấp | 1 | 313.95 | (6,10) | True |
| 15 | 5 | Tùy chỉnh A | Tải cao gần cuối ván | 1 | 227.854 | (4,0) | True |
| 15 | 5 | Tùy chỉnh B | Khai cuộc cân bằng | 1 | 2000.387 | (5,6) | True |
| 15 | 5 | Tùy chỉnh B | Trung cuộc tranh chấp | 1 | 2000.213 | (6,10) | True |
| 15 | 5 | Tùy chỉnh B | Tải cao gần cuối ván | 1 | 1235.387 | (4,0) | True |