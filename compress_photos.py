import os
import sys
import datetime
from collections import defaultdict

# 嘗試匯入圖片處理庫 Pillow
try:
    from PIL import Image, ImageOps
except ImportError:
    print("錯誤: 尚未安裝 Pillow 套件。")
    print("請在終端機執行: pip install Pillow")
    sys.exit(1)

# --- 設定 ---
INPUT_FILE = 'files.txt'          # 檔案清單
SOURCE_MEDIA_FOLDER = 'media/'            # 原始大檔照片/影片的位置
COMPRESSED_FOLDER = 'photos_compressed/'  # 壓縮後照片要存放的位置

def parse_files(filename):
    """ 讀取檔案清單，為了取得檔名列表 """
    if not os.path.exists(filename):
        print(f"錯誤: 找不到 {filename}")
        return {}

    files_by_date = defaultdict(list)
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    for line in lines:
        fname = line.strip()
        if len(fname) < 15: continue
        try:
            date_str = fname[:8]
            time_str = fname[9:15]
            # 這裡我們只需要檔名來做壓縮，但維持與主程式一樣的解析邏輯
            files_by_date[date_str].append({
                'filename': fname,
                'type': 'video' if fname.lower().endswith(('.mp4', '.mov')) else 'image'
            })
        except ValueError:
            continue
    return files_by_date

def compress_image_task(filename):
    """
    讀取原始圖片，壓縮並縮小，存入 photos_compressed 資料夾
    目標: 長邊 1200px, 品質 60 (約 50-100KB)
    """
    source_path = os.path.join(SOURCE_MEDIA_FOLDER, filename)
    target_path = os.path.join(COMPRESSED_FOLDER, filename)

    # 如果原始檔案不存在
    if not os.path.exists(source_path):
        print(f"  [跳過] 找不到原始檔: {filename}")
        return False

    # 如果目標檔案已經存在，且不需要強制覆寫，就跳過 (節省時間)
    if os.path.exists(target_path):
        print(f"  [已存在] {filename}") 
        return True

    try:
        with Image.open(source_path) as img:
            # 1. 轉為 RGB
            img = img.convert('RGB')
            # 2. 修正手機拍攝的旋轉資訊
            img = ImageOps.exif_transpose(img)
            # 3. 縮圖
            img.thumbnail((1200, 1200))
            # 4. 存檔壓縮
            img.save(target_path, "JPEG", quality=60, optimize=True)
            
            print(f"  [壓縮完成] {filename} -> 尺寸: {img.size}")
            return True
    except Exception as e:
        print(f"  [壓縮失敗] {filename}: {e}")
        return False

def main():
    print("--- 開始執行照片壓縮任務 ---")
    
    # 0. 建立壓縮圖片資料夾
    if not os.path.exists(COMPRESSED_FOLDER):
        os.makedirs(COMPRESSED_FOLDER)
        print(f"建立資料夾: {COMPRESSED_FOLDER}")

    # 1. 讀取清單
    data = parse_files(INPUT_FILE)
    if not data: return

    # 2. 批次壓縮圖片
    print("\n正在掃描並壓縮圖片...")
    count = 0
    for date_str, files in data.items():
        for file in files:
            if file['type'] == 'image':
                if compress_image_task(file['filename']):
                    count += 1
    
    print(f"\n任務完成！已檢查所有圖片。")
    print(f"壓縮後的圖片位於: {COMPRESSED_FOLDER}")

if __name__ == "__main__":
    main()