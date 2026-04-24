# Cờ Caro AI

Ứng dụng Cờ Caro cho phép người chơi đấu với AI ở nhiều mức độ khó. AI sử dụng tầng GBFS để ưu tiên các nước đi hứa hẹn nhất, sau đó Minimax kết hợp Alpha-Beta sẽ duyệt sâu để chọn nước đi tối ưu trong giới hạn thời gian.

## Mục tiêu nghiệm thu đề tài

- Kiến trúc: GBFS lọc ứng viên, Minimax + Alpha-Beta duyệt sâu.
- Hiệu năng: kiểm chứng mốc nhỏ hơn hoặc bằng 2 giây/lượt trên bàn 10x10 bằng script benchmark.
- Chiến thuật: kiểm tra các ca bắt buộc thắng/chặn bằng tactical tests.

## Chạy chương trình

```bash
python main.py
```

Chạy chế độ terminal:

```bash
python main.py --cli
```

Chạy benchmark hiệu năng:

```bash
python benchmark.py --size 10 --win-len 5 --repeats 2
```

Chạy kiểm thử chiến thuật:

```bash
python tactical_tests.py
```

Kết quả benchmark sẽ được xuất ra thư mục `docs/benchmarks/` gồm file `.md` và `.csv`.

## Thành phần chính

- `main.py`: điểm khởi động ứng dụng.
- `gui.py`: giao diện đồ họa và các mức độ khó.
- `cli.py`: chế độ chơi trên terminal.
- `ai.py`: tầng GBFS, Minimax, Alpha-Beta và giới hạn thời gian.
- `heuristics.py`: hàm đánh giá bàn cờ.
- `game.py`: logic luật chơi và sinh nước đi ứng viên.
- `benchmark.py`: đo độ trễ phản hồi AI theo nhiều cấu hình và xuất báo cáo.
- `tactical_tests.py`: xác minh các tình huống chiến thuật quan trọng (thắng ngay, chặn ngay).

## Ghi chú

AI được thiết kế để phản hồi nhanh trên bàn cờ lớn bằng cách giới hạn không gian tìm kiếm ở nhóm nước đi gần nhất, sau đó chỉ duyệt sâu vào các nhánh có điểm tốt nhất.
