import os

MEDIA_FOLDER = 'media'

def main():
    # 1. 設定要尋找的副檔名
    target_extensions = ('.jpg', '.mp4')

    # 檢查 media 資料夾是否存在
    if not os.path.exists(MEDIA_FOLDER):
        print(f"錯誤：找不到 '{MEDIA_FOLDER}' 資料夾。請確認資料夾名稱是否正確。")
        return

    # 3. 掃描目錄
    files = [
        f for f in os.listdir(MEDIA_FOLDER) 
        if f.lower().endswith(target_extensions)
    ]

    # 4. 依照檔名排序
    files.sort()

    # 5. 印出結果並寫入 files.txt
    print(f"--- 在 {MEDIA_FOLDER} 資料夾中找到 {len(files)} 個檔案 ---")
    with open('files.txt', 'w', encoding='utf-8') as f:
        for file in files:
            f.write(file + '\n')
    print(f"已成功將 {len(files)} 個檔名寫入 files.txt")
    print("")

if __name__ == "__main__":
    main()