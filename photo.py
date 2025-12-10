import difPy
import os
import shutil
from pathlib import Path

SOURCE_DIR = Path("/Users/mac4/Downloads/iPhone_2022")
GROUP_ROOT = SOURCE_DIR / "group" 
SIMILARITY = "similar"
DRY_RUN = False


def main():
    GROUP_ROOT.mkdir(parents=True, exist_ok=True)

    print(f"Building index from: {SOURCE_DIR}")
    dif = difPy.build(
        str(SOURCE_DIR),
        recursive=True,
        px_size=40,          # 可選：加快一點 [web:29]
        show_progress=True,  # 顯示掃描進度 [web:25]
    )

    print("Searching for similar images...")
    search = difPy.search(
        dif,
        similarity=100,
        processes=4,         # 視 CPU 調整 [web:37]
        show_progress=True,  # 顯示比對進度 [web:25]
    )

    result = search.result

    moved_files = set()
    group_index = 1

    for primary, matches in result.items():
        group_files = {primary}

        for m in matches:
            # difPy v4: 每個 match 是 [file_path, mse] [web:25]
            if isinstance(m, (list, tuple)) and m:
                path = m[0]
                group_files.add(path)

        group_files = [f for f in group_files if f not in moved_files]
        if not group_files:
            continue

        group_name = f"group_{group_index:04d}"
        group_dir = GROUP_ROOT / group_name
        group_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n== {group_name} ==")
        for file_path in group_files:
            src = Path(file_path)
            dst = group_dir / src.name

            print(f"{'MOVE' if not DRY_RUN else 'DRY'}: {src} -> {dst}")
            if not DRY_RUN:
                shutil.move(src, dst)

            moved_files.add(str(src))

        group_index += 1

    print("\nDone.")
    print(f"Grouped folders are under: {GROUP_ROOT}")


if __name__ == "__main__":   # ★ 關鍵：一定要有這一段 [web:25]
    main()
