import os
import datetime
from collections import defaultdict

# 設定
INPUT_FILE = 'files.txt'

def parse_files(filename):
    """ 讀取並解析檔案，回傳 { '20251122': [files...], ... } """
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
            dt = datetime.datetime.strptime(f"{date_str}{time_str}", "%Y%m%d%H%M%S")
            files_by_date[date_str].append({
                'filename': fname,
                'datetime': dt,
                'type': 'video' if fname.lower().endswith(('.mp4', '.mov')) else 'image'
            })
        except ValueError:
            continue

    for date_key in files_by_date:
        files_by_date[date_key].sort(key=lambda x: x['datetime'])
    
    return dict(sorted(files_by_date.items()))

def get_common_css():
    """ 回傳所有頁面共用的 CSS """
    return """
    <style>
        :root { --bg-color: #ffffff; --text-color: #333; --accent-color: #007aff; --nav-height: 60px; }
        * { box-sizing: border-box; }
        body {
            margin: 0; padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            color: var(--text-color); padding-top: var(--nav-height);
        }
        /* 導航列 */
        nav {
            position: fixed; top: 0; left: 0; width: 100%; height: var(--nav-height);
            background: rgba(255, 255, 255, 0.98); border-bottom: 1px solid #ddd;
            z-index: 1000; display: flex; align-items: center;
            overflow-x: auto; white-space: nowrap; padding: 0 15px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }
        nav a {
            text-decoration: none; color: #555; font-weight: 600; margin-right: 15px;
            padding: 8px 12px; border-radius: 20px; font-size: 0.9rem;
            transition: 0.2s;
        }
        nav a:hover { background-color: #f0f0f0; color: var(--accent-color); }
        nav a.active { background-color: var(--accent-color); color: white; }

        /* 通用容器 */
        main { width: 100%; max-width: 700px; margin: 0 auto; padding: 40px 20px 100px 20px; }
        
        /* 首頁樣式 */
        .home-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; }
        .day-card { 
            border: 1px solid #eee; border-radius: 8px; padding: 20px; 
            text-decoration: none; color: #333; transition: transform 0.2s; box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }
        .day-card:hover { transform: translateY(-5px); border-color: var(--accent-color); }
        .day-card h3 { margin: 0 0 10px 0; font-size: 1.2rem; }
        .day-card p { margin: 0; color: #777; font-size: 0.9rem; }

        /* 內頁媒體樣式 */
        .media-item { margin-bottom: 50px; animation: fadeIn 0.8s forwards; }
        .media-content { width: 100%; border-radius: 4px; overflow: hidden; background: #f0f0f0; }
        img, video { width: 100%; height: auto; display: block; }
        .caption { padding: 12px 0 0 0; font-size: 0.95rem; color: #555; line-height: 1.5; }
        .filename-ref { font-size: 0.75rem; color: #ccc; margin-top: 4px; font-family: monospace; }
        
        /* 遊記文字區塊 */
        .journal-block {
            background-color: #f8f9fa; border-left: 4px solid var(--accent-color);
            padding: 25px 30px; margin: 60px 0; border-radius: 0 8px 8px 0;
        }
        .page-title { text-align: center; margin-bottom: 40px; }
        
        /* 頁面切換按鈕 */
        .pagination { display: flex; justify-content: space-between; margin-top: 50px; padding-top: 30px; border-top: 1px solid #eee; }
        .btn { padding: 10px 20px; background: #eee; text-decoration: none; color: #333; border-radius: 5px; }
        .btn:hover { background: #ddd; }

        @keyframes fadeIn { to { opacity: 1; } }
        @media (max-width: 600px) { main { padding: 20px 15px; } }
    </style>
    """

def get_navbar_html(all_dates, current_page_key):
    """
    生成導航列 HTML。
    current_page_key: 'home', 'summary', 或日期字串 '20251122'
    """
    links = []
    
    # 1. 首頁連結
    cls = 'class="active"' if current_page_key == 'home' else ''
    links.append(f'<a href="index.html" {cls}>🏠 首頁</a>')
    
    # 2. 每日連結
    for i, date_str in enumerate(all_dates):
        display_date = f"Day {i+1} ({date_str[4:6]}/{date_str[6:]})"
        cls = 'class="active"' if current_page_key == date_str else ''
        links.append(f'<a href="{date_str}.html" {cls}>{display_date}</a>')
        
    # 3. 總結連結
    cls = 'class="active"' if current_page_key == 'summary' else ''
    links.append(f'<a href="summary.html" {cls}>📝 總結</a>')
    
    return f"<nav>{''.join(links)}</nav>"

def create_html_file(filename, content, navbar, title="Travel Journal"):
    """ 組合最終 HTML 檔案 """
    full_html = f"""
    <!DOCTYPE html>
    <html lang="zh-TW">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        {get_common_css()}
    </head>
    <body>
        {navbar}
        <main>
            {content}
        </main>
    </body>
    </html>
    """
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(full_html)
    print(f"已生成: {filename}")

def main():
    print("正在讀取檔案清單...")
    data = parse_files(INPUT_FILE)
    if not data: return
    
    all_dates = list(data.keys()) # 取得所有日期列表 ['20251122', '20251123', ...]

    # --- 1. 生成首頁 (index.html) ---
    home_content = """
    <div class="page-title">
        <h1>我的旅遊日誌</h1>
        <p>點擊下方卡片進入當日行程</p>
    </div>
    <div class="home-grid">
    """
    for i, date_str in enumerate(all_dates):
        # 取得該日第一張照片作為封面 (如果有的話)
        cover_img = ""
        for f in data[date_str]:
            if f['type'] == 'image':
                cover_img = f['filename']
                break
        
        # 如果沒圖片，就不顯示封面，只顯示文字
        img_html = f'<div style="height:150px; overflow:hidden; margin-bottom:10px;"><img src="{cover_img}" style="object-fit:cover; height:100%;"></div>' if cover_img else ''
        
        home_content += f"""
        <a href="{date_str}.html" class="day-card">
            {img_html}
            <h3>Day {i+1} - {date_str[:4]}/{date_str[4:6]}/{date_str[6:]}</h3>
            <p>包含 {len(data[date_str])} 個照片/影片</p>
        </a>
        """
    
    home_content += """
        <a href="summary.html" class="day-card" style="border-left: 5px solid var(--accent-color);">
            <h3>📝 旅程總結</h3>
            <p>心得、後記與精選回憶</p>
        </a>
    </div>
    """
    create_html_file('index.html', home_content, get_navbar_html(all_dates, 'home'), "我的旅遊日誌 - 首頁")

    # --- 2. 生成每一天的頁面 (YYYYMMDD.html) ---
    for i, date_str in enumerate(all_dates):
        files = data[date_str]
        
        # 標題
        day_content = f"""
        <div class="page-title">
            <h1>Day {i+1}: {date_str[:4]}/{date_str[4:6]}/{date_str[6:]}</h1>
        </div>
        """
        
        # 媒體內容
        for idx, file in enumerate(files):
            fname = file['filename']
            
            # 媒體
            if file['type'] == 'video':
                media_html = f'<video controls playsinline preload="metadata"><source src="{fname}" type="video/mp4"></video>'
            else:
                media_html = f'<img src="{fname}" loading="lazy">'
                
            day_content += f"""
            <article class="media-item">
                <div class="media-content">{media_html}</div>
                <div class="caption">
                    <div>這是 {fname} 的圖說...</div>
                    <div class="filename-ref">{fname}</div>
                </div>
            </article>
            """
            
            # 每 10 個檔案插入遊記
            if (idx + 1) % 10 == 0:
                day_content += f"""
                <div class="journal-block">
                    <h3>旅程記錄 (Part {(idx+1)//10})</h3>
                    <p>（請在此處編輯您的文字...）</p>
                </div>
                """
        
        # 底部前後頁按鈕
        prev_link = f'{all_dates[i-1]}.html' if i > 0 else 'index.html'
        prev_text = '← 前一天' if i > 0 else '← 回首頁'
        
        if i < len(all_dates) - 1:
            next_link = f'{all_dates[i+1]}.html'
            next_text = '下一天 →'
        else:
            next_link = 'summary.html'
            next_text = '看總結 →'

        day_content += f"""
        <div class="pagination">
            <a href="{prev_link}" class="btn">{prev_text}</a>
            <a href="{next_link}" class="btn">{next_text}</a>
        </div>
        """
        
        create_html_file(f'{date_str}.html', day_content, get_navbar_html(all_dates, date_str), f"Day {i+1} - {date_str}")

    # --- 3. 生成總結頁 (summary.html) ---
    summary_content = """
    <div class="page-title">
        <h1>旅程總結</h1>
    </div>
    <div class="journal-block" style="margin-top: 0;">
        <h3>後記</h3>
        <p>（請在此處寫下整趟旅程的總結、花費統計、或是最難忘的回憶...）</p>
        <p>這趟旅程共歷時 X 天，拍攝了許多珍貴的照片。</p>
    </div>
    
    <div class="pagination">
        <a href="{}" class="btn">← 回到最後一天</a>
        <a href="index.html" class="btn">回首頁 🏠</a>
    </div>
    """.format(f"{all_dates[-1]}.html" if all_dates else "index.html")
    
    create_html_file('summary.html', summary_content, get_navbar_html(all_dates, 'summary'), "旅程總結")

    print("全部完成！請打開 index.html 開始瀏覽。")

if __name__ == "__main__":
    main()