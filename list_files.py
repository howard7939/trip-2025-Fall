import os

def list_media_files():
    # 1. 設定要尋找的副檔名
    target_extensions = ('.jpg', '.mp4')

    # 2. 設定目標資料夾 (修改這裡：指向 'media' 資料夾)
    media_folder = 'media' 

    # 檢查 media 資料夾是否存在，避免報錯
    if not os.path.exists(media_folder):
        print(f"錯誤：找不到 '{media_folder}' 資料夾。請確認資料夾名稱是否正確。")
        return

    # 3. 掃描 'media' 目錄並過濾檔案 (修改這裡：使用 media_folder)
    files = [
        f for f in os.listdir(media_folder) 
        if f.lower().endswith(target_extensions)
    ]

    # 4. 依照檔名排序
    files.sort()

    # 5. 印出結果
    print(f"--- 在 {media_folder} 資料夾中找到 {len(files)} 個檔案 ---")
    print("") 
    
    for file in files:
        print(file)

    print("") 
    print("--- 列表結束 ---")

    # 寫入到 files.txt (這裡不用改，它預設會寫在執行腳本的根目錄)
    with open('files.txt', 'w', encoding='utf-8') as f:
        for file in files:
            f.write(file + '\n')
            
    print(f"已成功將 {len(files)} 個檔名寫入 files.txt (位於根目錄)")

if __name__ == "__main__":
    list_media_files()