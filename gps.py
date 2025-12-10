import os
import shutil
from pathlib import Path
from math import radians, sin, cos, sqrt, atan2

from PIL import Image
from PIL.ExifTags import GPSTAGS
from PIL.TiffImagePlugin import IFDRational

# ===== EXIF 取 GPS =====

def get_gps_coords(image_path):
    """從照片EXIF擷取GPS經緯度（適用你目前這張 iPhone 照）"""
    try:
        img = Image.open(image_path)
        exif = img.getexif()

        # 用 get_ifd 取得 GPS IFD (34853)
        try:
            gps_ifd = exif.get_ifd(34853)
        except Exception:
            gps_ifd = None

        if not gps_ifd:
            return None

        gps_info = {}
        for k, v in gps_ifd.items():
            name = GPSTAGS.get(k, k)
            gps_info[name] = v

        def to_deg(v):
            d, m, s = v

            def _r(x):
                if isinstance(x, IFDRational):
                    return float(x)
                if isinstance(x, tuple):
                    return float(x[0]) / float(x[1])
                return float(x)

            return _r(d) + _r(m) / 60.0 + _r(s) / 3600.0

        if "GPSLatitude" not in gps_info or "GPSLongitude" not in gps_info:
            return None

        lat = to_deg(gps_info["GPSLatitude"])
        lon = to_deg(gps_info["GPSLongitude"])

        if gps_info.get("GPSLatitudeRef", "N") == "S":
            lat = -lat
        if gps_info.get("GPSLongitudeRef", "E") == "W":
            lon = -lon

        return lat, lon

    except Exception as e:
        print(f"讀取 {image_path} GPS 發生錯誤: {e}")
        return None

# ===== 距離公式 =====

def haversine_distance(lat1, lon1, lat2, lon2):
    """兩點距離（公尺）"""
    R = 6371000
    phi1, phi2 = radians(lat1), radians(lat2)
    dphi = radians(lat2 - lat1)
    dlambda = radians(lon2 - lon1)
    a = sin(dphi/2)**2 + cos(phi1) * cos(phi2) * sin(dlambda/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c

# ===== 主流程 =====

SOURCE_DIR = Path("/Users/mac4/Downloads/iPhone_2022")
GROUP_DIR = SOURCE_DIR / "group"
GROUP_DIR.mkdir(exist_ok=True)

REFERENCE_IMAGE = SOURCE_DIR / "IMG_1011.JPG"   # ★你要當基準的那張
MAX_DISTANCE = 500  # 公尺，視需要調整

def main():
    ref_coords = get_gps_coords(str(REFERENCE_IMAGE))
    if not ref_coords:
        print(f"❌ 找不到基準圖片 {REFERENCE_IMAGE} 的GPS")
        return

    print(f"📍 基準座標: {ref_coords[0]:.6f}, {ref_coords[1]:.6f}")
    moved = 0

    for path in SOURCE_DIR.iterdir():
        if not path.is_file():
            continue
        if path.suffix.lower() not in {".jpg", ".jpeg", ".heic", ".png"}:
            continue
        if path == REFERENCE_IMAGE:
            continue

        coords = get_gps_coords(str(path))
        if not coords:
            continue

        dist = haversine_distance(ref_coords[0], ref_coords[1], coords[0], coords[1])
        if dist <= MAX_DISTANCE:
            dst = GROUP_DIR / path.name
            print(f"MOVE ({dist:.1f}m): {path.name} -> {dst}")
            shutil.move(str(path), str(dst))
            moved += 1

    print(f"\n完成，總共搬移 {moved} 張到 {GROUP_DIR}")

if __name__ == "__main__":
    main()
