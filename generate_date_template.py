import os
import sys

# 設定
INPUT_FILE = 'files.txt'

# 預設日期 (如果在執行時沒有給參數，就會用這個)
DEFAULT_TARGET_DATE = '20251122'

def get_sort_key(filename):
    """
    排序用的輔助函式：
    將 'Screenshot_20251122...' 暫時視為 '20251122...'
    這樣才能跟一般的相機照片 '20251122...' 依照時間正確穿插排序
    """
    if filename.startswith('Screenshot_'):
        return filename.replace('Screenshot_', '')
    return filename

def main():
    # 1. 決定目標日期
    # 如果執行指令是 python generate_date_template.py 20251122，就用輸入的日期
    if len(sys.argv) > 1:
        target_date = sys.argv[1]
    else:
        target_date = DEFAULT_TARGET_DATE

    output_filename = f"{target_date}_template.txt"
    print(f"正在處理日期: {target_date} ...")

    # 2. 讀取 files.txt
    if not os.path.exists(INPUT_FILE):
        print(f"錯誤：找不到 {INPUT_FILE}")
        return

    found_files = []
    
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            # strip() 會移除前後空白與換行，但不會影響檔名中間的空白
            fname = line.strip()
            if not fname: 
                continue
            
            # 判斷邏輯：
            # 1. 一般照片: "20251122_..."
            # 2. 截圖: "Screenshot_20251122_..."
            is_camera_photo = fname.startswith(target_date)
            is_screenshot = fname.startswith(f"Screenshot_{target_date}")

            if is_camera_photo or is_screenshot:
                found_files.append(fname)

    # 3. 輸出結果
    if not found_files:
        print(f"警告：在 {INPUT_FILE} 中找不到日期為 {target_date} 的檔案。")
        return

    # 關鍵步驟：依照時間排序
    # 使用自定義的 key，忽略 Screenshot_ 前綴來進行比較
    found_files.sort(key=get_sort_key)

    # 寫入 template txt
    with open(output_filename, 'w', encoding='utf-8') as f:
        for fname in found_files:
            # 這裡保留您原本的格式：檔名 + 空格 + 換行
            f.write(fname + ' \n')

    print(f"成功！已生成 {output_filename}，包含 {len(found_files)} 個檔案 (含截圖)。")

if __name__ == "__main__":
    main()