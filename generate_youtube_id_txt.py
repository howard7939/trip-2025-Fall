import os

MEDIA_FOLDER = 'media'
YOUTUBE_ID_FILENAME = 'youtube_id.txt'

def main():
    """
    從檔案列表中篩選出 .mp4，並生成 youtube_id_draft.txt
    格式：檔名 (空格)
    特色：不同日期之間會空一行
    """
    # 1. 篩選影片檔
    video_files = [f for f in os.listdir(MEDIA_FOLDER) if f.lower().endswith('.mp4')]

    video_files.sort()
    
    if not video_files:
        print("沒有找到任何影片檔，略過生成 YouTube 草稿。")
        return

    print(f"--- 正在生成影片清單草稿 (共 {len(video_files)} 個影片) ---")
    
    with open(YOUTUBE_ID_FILENAME, 'w', encoding='utf-8') as f:
        previous_date = ""
        
        for vid in video_files:
            # 假設檔名格式為 YYYYMMDD_...
            # 取出前 8 碼作為日期
            current_date = vid[:8]
            
            # 如果日期改變了 (且不是第一筆)，就插入空行
            if previous_date and current_date != previous_date:
                f.write('\n')
            
            # 寫入檔名 + 一個空格
            f.write(f"{vid} \n") # 這裡預留空格，您可以直接貼上網址
            
            previous_date = current_date

    print(f"已生成影片草稿檔: {YOUTUBE_ID_FILENAME}")
    print("您可以打開它，直接在檔名後面貼上 YouTube 連結。")
    print("--- 任務完成 ---")


if __name__ == "__main__":
    main()