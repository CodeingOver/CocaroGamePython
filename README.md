# Cờ Caro AI - Hệ thống Trí tuệ Nhân tạo thông minh

## 1. Tên dự án & Giới thiệu
**Cờ Caro AI** là một ứng dụng trò chơi Cờ Caro (Gomoku) được tích hợp trí tuệ nhân tạo hiện đại. Ứng dụng không chỉ là một trò chơi giải trí mà còn là một sản phẩm thực nghiệm các thuật toán tìm kiếm và tối ưu hóa trong AI, bao gồm GBFS (Greedy Best-First Search), Minimax kết hợp cắt tỉa Alpha-Beta và các kỹ thuật Heuristic tiên tiến.

## 2. Tính năng chính
- **Trí tuệ nhân tạo thông minh**: AI sử dụng sự kết hợp giữa GBFS để sàng lọc nước đi và Minimax để duyệt sâu, đảm bảo phản hồi nhanh chóng và nước đi chiến thuật.
- **Tùy chỉnh linh hoạt**: Người chơi có thể tùy chỉnh kích thước bàn cờ (từ 3x3 đến 30x30) và độ dài chuỗi thắng (mặc định là 5).
- **Giao diện trực quan**: Xây dựng bằng thư viện Tkinter, hỗ trợ hiển thị rõ nét, thao tác mượt mà và các mức độ khó khác nhau.
- **Hệ thống Benchmark**: Tích hợp công cụ đo lường hiệu năng, tự động xuất báo cáo dưới dạng Markdown và CSV.
- **Kiểm thử chiến thuật**: Bộ công cụ `tactical_tests.py` giúp xác minh khả năng nhận diện các thế cờ hiểm hóc (bẫy, chặn 4, thắng ngay).

## 3. Yêu cầu hệ thống
- **Ngôn ngữ**: Python 3.8 trở lên.
- **Thư viện**: 
  - `tkinter` (thường đi kèm mặc định với Python).
  - `pathlib`, `shutil` (thư viện chuẩn).
  - Không yêu cầu cài đặt thêm thư viện bên ngoài (Zero Dependencies).

## 4. Hướng dẫn cài đặt
1. **Tải mã nguồn**:
   ```bash
   git clone https://github.com/your-username/Cocaro.git
   cd Cocaro
   ```
2. **Kiểm tra Python**:
   ```bash
   python --version
   ```

## 5. Biến môi trường
Dự án hiện tại chạy cục bộ và không yêu cầu cấu hình biến môi trường phức tạp. Các hằng số hệ thống được quản lý tập trung tại `constants.py`.

## 6. Hướng dẫn chạy & Sử dụng

### Chạy ứng dụng chính (GUI)
```bash
python main.py
```

### Chạy Benchmark hiệu năng
Để kiểm tra tốc độ phản hồi của AI trên nhiều kích thước bàn cờ:
```bash
python benchmark.py --sizes 10,12,15 --win-len 5 --repeats 2
```

### Chạy Kiểm thử chiến thuật
Để kiểm tra độ thông minh của AI trong các tình huống cụ thể:
```bash
python tactical_tests.py
```

---
*Phát triển bởi Đội ngũ dự án Trí tuệ nhân tạo.*
