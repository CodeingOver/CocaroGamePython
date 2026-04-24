from __future__ import annotations
import shutil
from gui import main as gui_main
from pathlib import Path

    
def main() -> None:
    # Ứng dụng chạy trực tiếp bằng giao diện đồ họa.
    gui_main()

def clean_pycache():
    # Tìm và xóa thư mục __pycache__ trong project
    for path in Path(".").rglob("__pycache__"):
        if path.is_dir():
            shutil.rmtree(path)
   

if __name__ == "__main__":
    clean_pycache()
    main()
