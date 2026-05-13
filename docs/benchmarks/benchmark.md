# Báo cáo benchmark AI Cờ Caro

- Thời gian chạy: 2026-05-13 14:46:38
- Tiêu chí đạt: mọi lượt AI <= 2000ms

## Giải thích ý nghĩa các cột

- **Bàn cờ**: Kích thước lưới (ví dụ: 10 nghĩa là 10x10).
- **Win_len**: Số quân liên tiếp cần thiết để thắng.
- **Cấu hình**: Mức độ khó của AI (Khó, Cực khó, Địa ngục).
- **Mẫu**: Số lượng lượt đánh AI đã thực hiện để lấy dữ liệu.
- **Budget (ms)**: Ngân sách thời gian tối đa cho phép AI tính toán.
- **Min / Avg / Max**: Thời gian phản hồi nhỏ nhất, trung bình và lớn nhất (ms).
- **P95**: 95th percentile - 95% số lượt đánh có thời gian phản hồi thấp hơn giá trị này.
- **Vượt 2s**: Số lần AI tính toán lâu hơn 2000ms.
- **Kết luận**: Đạt (nếu không có lượt nào vượt 2s) hoặc Chưa đạt.

## Tổng hợp theo cấu hình

| Bàn cờ | Win_len | Cấu hình | Mẫu | Budget (ms) | Min | Avg | P95 | Max | Vượt 2s | Kết luận |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---|
| 10 | 5 | Cực khó | 3 | 1500 | 632.222 | 1068.515 | 1457.596 | 1500.33 | 0 | Đạt |
| 10 | 5 | Khó | 3 | 1000 | 238.775 | 278.57 | 305.314 | 307.026 | 0 | Đạt |
| 10 | 5 | Tùy chỉnh A | 3 | 1000 | 223.004 | 273.304 | 304.766 | 306.344 | 0 | Đạt |
| 10 | 5 | Tùy chỉnh B | 3 | 2000 | 1156.895 | 1719.155 | 2000.315 | 2000.322 | 2 | Chưa đạt |
| 10 | 5 | Địa ngục | 3 | 2000 | 1159.326 | 1719.95 | 2000.301 | 2000.311 | 2 | Chưa đạt |
| 12 | 5 | Cực khó | 3 | 1500 | 580.917 | 1005.851 | 1443.847 | 1500.229 | 0 | Đạt |
| 12 | 5 | Khó | 3 | 1000 | 225.361 | 288.16 | 335.085 | 338.967 | 0 | Đạt |
| 12 | 5 | Tùy chỉnh A | 3 | 1000 | 224.279 | 287.146 | 335.38 | 339.58 | 0 | Đạt |
| 12 | 5 | Tùy chỉnh B | 3 | 2000 | 1204.302 | 1735.014 | 2000.492 | 2000.522 | 2 | Chưa đạt |
| 12 | 5 | Địa ngục | 3 | 2000 | 1170.322 | 1723.601 | 2000.299 | 2000.314 | 2 | Chưa đạt |
| 15 | 5 | Cực khó | 3 | 1500 | 589.539 | 1024.293 | 1442.464 | 1492.662 | 0 | Đạt |
| 15 | 5 | Khó | 3 | 1000 | 228.369 | 291.503 | 329.444 | 331.037 | 0 | Đạt |
| 15 | 5 | Tùy chỉnh A | 3 | 1000 | 232.258 | 309.762 | 350.317 | 350.767 | 0 | Đạt |
| 15 | 5 | Tùy chỉnh B | 3 | 2000 | 1193.072 | 1731.262 | 2000.389 | 2000.397 | 2 | Chưa đạt |
| 15 | 5 | Địa ngục | 3 | 2000 | 1250.155 | 1750.249 | 2000.357 | 2000.372 | 2 | Chưa đạt |

## Chi tiết từng lượt

| Bàn cờ | Win_len | Cấu hình | Kịch bản | Lần chạy | Thời gian (ms) | Nước đi | <=2s |
|---:|---:|---|---|---:|---:|---|---|
| 10 | 5 | Khó | Khai cuộc cân bằng | 1 | 307.026 | (3,4) | True |
| 10 | 5 | Khó | Trung cuộc tranh chấp | 1 | 289.908 | (4,8) | True |
| 10 | 5 | Khó | Tải cao gần cuối ván | 1 | 238.775 | (4,0) | True |
| 10 | 5 | Cực khó | Khai cuộc cân bằng | 1 | 1500.33 | (7,4) | True |
| 10 | 5 | Cực khó | Trung cuộc tranh chấp | 1 | 1072.993 | (4,8) | True |
| 10 | 5 | Cực khó | Tải cao gần cuối ván | 1 | 632.222 | (4,0) | True |
| 10 | 5 | Địa ngục | Khai cuộc cân bằng | 1 | 2000.311 | (3,4) | False |
| 10 | 5 | Địa ngục | Trung cuộc tranh chấp | 1 | 2000.213 | (4,8) | False |
| 10 | 5 | Địa ngục | Tải cao gần cuối ván | 1 | 1159.326 | (4,0) | True |
| 10 | 5 | Tùy chỉnh A | Khai cuộc cân bằng | 1 | 306.344 | (3,4) | True |
| 10 | 5 | Tùy chỉnh A | Trung cuộc tranh chấp | 1 | 290.564 | (4,8) | True |
| 10 | 5 | Tùy chỉnh A | Tải cao gần cuối ván | 1 | 223.004 | (4,0) | True |
| 10 | 5 | Tùy chỉnh B | Khai cuộc cân bằng | 1 | 2000.322 | (3,4) | False |
| 10 | 5 | Tùy chỉnh B | Trung cuộc tranh chấp | 1 | 2000.249 | (4,8) | False |
| 10 | 5 | Tùy chỉnh B | Tải cao gần cuối ván | 1 | 1156.895 | (4,0) | True |
| 12 | 5 | Khó | Khai cuộc cân bằng | 1 | 338.967 | (8,7) | True |
| 12 | 5 | Khó | Trung cuộc tranh chấp | 1 | 300.151 | (5,9) | True |
| 12 | 5 | Khó | Tải cao gần cuối ván | 1 | 225.361 | (4,0) | True |
| 12 | 5 | Cực khó | Khai cuộc cân bằng | 1 | 1500.229 | (8,7) | True |
| 12 | 5 | Cực khó | Trung cuộc tranh chấp | 1 | 936.408 | (5,9) | True |
| 12 | 5 | Cực khó | Tải cao gần cuối ván | 1 | 580.917 | (4,0) | True |
| 12 | 5 | Địa ngục | Khai cuộc cân bằng | 1 | 2000.314 | (4,5) | False |
| 12 | 5 | Địa ngục | Trung cuộc tranh chấp | 1 | 2000.166 | (5,9) | False |
| 12 | 5 | Địa ngục | Tải cao gần cuối ván | 1 | 1170.322 | (4,0) | True |
| 12 | 5 | Tùy chỉnh A | Khai cuộc cân bằng | 1 | 339.58 | (8,7) | True |
| 12 | 5 | Tùy chỉnh A | Trung cuộc tranh chấp | 1 | 297.579 | (5,9) | True |
| 12 | 5 | Tùy chỉnh A | Tải cao gần cuối ván | 1 | 224.279 | (4,0) | True |
| 12 | 5 | Tùy chỉnh B | Khai cuộc cân bằng | 1 | 2000.522 | (4,5) | False |
| 12 | 5 | Tùy chỉnh B | Trung cuộc tranh chấp | 1 | 2000.218 | (5,9) | False |
| 12 | 5 | Tùy chỉnh B | Tải cao gần cuối ván | 1 | 1204.302 | (4,0) | True |
| 15 | 5 | Khó | Khai cuộc cân bằng | 1 | 331.037 | (5,6) | True |
| 15 | 5 | Khó | Trung cuộc tranh chấp | 1 | 315.104 | (6,10) | True |
| 15 | 5 | Khó | Tải cao gần cuối ván | 1 | 228.369 | (4,0) | True |
| 15 | 5 | Cực khó | Khai cuộc cân bằng | 1 | 1492.662 | (5,6) | True |
| 15 | 5 | Cực khó | Trung cuộc tranh chấp | 1 | 990.679 | (6,10) | True |
| 15 | 5 | Cực khó | Tải cao gần cuối ván | 1 | 589.539 | (4,0) | True |
| 15 | 5 | Địa ngục | Khai cuộc cân bằng | 1 | 2000.372 | (5,6) | False |
| 15 | 5 | Địa ngục | Trung cuộc tranh chấp | 1 | 2000.22 | (6,10) | False |
| 15 | 5 | Địa ngục | Tải cao gần cuối ván | 1 | 1250.155 | (4,0) | True |
| 15 | 5 | Tùy chỉnh A | Khai cuộc cân bằng | 1 | 350.767 | (5,6) | True |
| 15 | 5 | Tùy chỉnh A | Trung cuộc tranh chấp | 1 | 346.262 | (6,10) | True |
| 15 | 5 | Tùy chỉnh A | Tải cao gần cuối ván | 1 | 232.258 | (4,0) | True |
| 15 | 5 | Tùy chỉnh B | Khai cuộc cân bằng | 1 | 2000.397 | (5,6) | False |
| 15 | 5 | Tùy chỉnh B | Trung cuộc tranh chấp | 1 | 2000.317 | (6,10) | False |
| 15 | 5 | Tùy chỉnh B | Tải cao gần cuối ván | 1 | 1193.072 | (4,0) | True |