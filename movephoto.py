import os
import shutil
from pathlib import Path

SOURCE_DIR = Path("/Users/mac4/Downloads/iPhone_2022/group")
DESTINATION_DIR = SOURCE_DIR.parent  # 直接是 /Users/mac4/Downloads/iPhone_2022

# 確保目的資料夾存在（正常來說已存在，這行只是保險）
DESTINATION_DIR.mkdir(parents=True, exist_ok=True)

for root, dirs, files in os.walk(SOURCE_DIR):
    for file in files:
        src = Path(root) / file
        dst = DESTINATION_DIR / file

        print(f"MOVE: {src} -> {dst}")
        shutil.move(src, dst)
