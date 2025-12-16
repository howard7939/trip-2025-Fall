# Built by Gemini on 2025/12/13

import os
import datetime
from collections import defaultdict

# 設定
INPUT_FILE = './media/files.txt'
MEDIA_FOLDER = 'media/'  # 指定媒體資料夾路徑

def parse_files(filename):
    """ 讀取並解析檔案 """
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
    """ 
    回傳美化後的 CSS 
    設計語言：Clean, Modern, Soft Shadows, Card UI
    """
    return """
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@300;400;500;700&display=swap" rel="stylesheet">
    <style>
        :root { 
            --bg-body: #f4f6f8;       /* 柔和的淺灰背景 */
            --bg-card: #ffffff;       /* 卡片白底 */
            --text-main: #2d3748;     /* 深灰主色，比純黑柔和 */
            --text-light: #718096;    /* 輔助文字顏色 */
            --accent: #3182ce;        /* 質感藍 */
            --accent-light: #ebf8ff;  /* 淺藍背景 */
            --shadow-sm: 0 1px 3px rgba(0,0,0,0.1);
            --shadow-md: 0 4px 6px rgba(0,0,0,0.08);
            --shadow-lg: 0 10px 15px rgba(0,0,0,0.08);
            --radius: 12px;
            --nav-height: 64px;
        }

        * { box-sizing: border-box; }
        
        body {
            margin: 0; padding: 0;
            font-family: 'Noto Sans TC', -apple-system, BlinkMacSystemFont, sans-serif;
            background-color: var(--bg-body);
            color: var(--text-main);
            padding-top: var(--nav-height);
            line-height: 1.6;
            -webkit-font-smoothing: antialiased;
        }

        /* --- 導航列 Glassmorphism --- */
        nav {
            position: fixed; top: 0; left: 0; width: 100%; height: var(--nav-height);
            background: rgba(255, 255, 255, 0.85); 
            backdrop-filter: blur(12px);
            border-bottom: 1px solid rgba(0,0,0,0.05);
            z-index: 1000; display: flex; align-items: center; justify-content: center;
        }
        .nav-inner {
            width: 100%; max-width: 900px; padding: 0 20px;
            display: flex; overflow-x: auto; white-space: nowrap;
            scrollbar-width: none; /* Hide scrollbar Firefox */
        }
        .nav-inner::-webkit-scrollbar { display: none; } /* Hide scrollbar Chrome */
        
        nav a {
            text-decoration: none; color: var(--text-light); font-weight: 500; 
            margin-right: 8px; padding: 8px 16px; border-radius: 20px; font-size: 0.95rem;
            transition: all 0.2s ease;
        }
        nav a:hover { color: var(--accent); background: white; box-shadow: var(--shadow-sm); }
        nav a.active { 
            background-color: var(--text-main); color: white; 
            box-shadow: 0 2px 5px rgba(45, 55, 72, 0.3);
        }

        /* --- 主容器 --- */
        main { 
            width: 100%; max-width: 720px; margin: 0 auto; 
            padding: 40px 20px 100px 20px; 
        }
        
        /* --- 標題區 --- */
        .page-header { text-align: center; margin-bottom: 50px; }
        .page-header h1 { 
            font-size: 2rem; font-weight: 700; color: var(--text-main); margin-bottom: 8px; 
            letter-spacing: -0.02em;
        }
        .page-header p { color: var(--text-light); font-size: 1rem; }

        /* --- 首頁 Grid --- */
        .home-grid { 
            display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); 
            gap: 24px; 
        }
        .day-card { 
            background: var(--bg-card);
            border-radius: var(--radius); 
            overflow: hidden;
            text-decoration: none; color: var(--text-main); 
            box-shadow: var(--shadow-sm);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            display: flex; flex-direction: column;
        }
        .day-card:hover { 
            transform: translateY(-6px); 
            box-shadow: var(--shadow-lg); 
        }
        .card-img-wrap {
            height: 180px; width: 100%; background: #e2e8f0; position: relative; overflow: hidden;
        }
        .card-img-wrap img { 
            width: 100%; height: 100%; object-fit: cover; 
            transition: transform 0.5s ease;
        }
        .day-card:hover .card-img-wrap img { transform: scale(1.05); }
        .card-content { padding: 20px; }
        .card-content h3 { margin: 0 0 6px 0; font-size: 1.25rem; }
        .card-content p { margin: 0; color: var(--text-light); font-size: 0.9rem; }
        
        /* 漸層佔位圖 (當沒有照片時) */
        .placeholder-gradient {
            width: 100%; height: 100%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }

        /* --- 內頁內容串流 (Timeline Stream) --- */
        .timeline-container {
            position: relative;
            padding-left: 20px; /* 預留左側線條空間 */
        }
        /* 左側線條 */
        .timeline-container::before {
            content: ''; position: absolute; left: 0; top: 20px; bottom: 0;
            width: 2px; background: #e2e8f0; border-radius: 2px;
        }

        .media-item { 
            background: var(--bg-card);
            padding: 15px; 
            border-radius: var(--radius);
            box-shadow: var(--shadow-md);
            margin-bottom: 40px; 
            position: relative;
            animation: fadeIn 0.6s ease-out forwards;
        }
        
        /* 連接線條的小圓點 */
        .media-item::before {
            content: ''; position: absolute; left: -25px; top: 30px;
            width: 12px; height: 12px; background: white;
            border: 3px solid var(--accent); border-radius: 50%;
            z-index: 1;
        }

        .media-content { 
            width: 100%; border-radius: 8px; overflow: hidden; 
            background: #edf2f7; 
        }
        img, video { width: 100%; height: auto; display: block; }
        
        .caption { 
            padding: 15px 5px 5px 5px; 
            font-size: 1rem; color: #4a5568; 
        }
        .filename-ref { 
            font-size: 0.75rem; color: #a0aec0; margin-top: 6px; 
            font-family: 'Menlo', monospace; 
        }

        /* --- 遊記文字區塊 (Magazine Quote Look) --- */
        .journal-block {
            position: relative;
            background: linear-gradient(to right, #ffffff, #fcfcfc);
            border: 1px solid #e2e8f0;
            border-left: 5px solid var(--accent);
            padding: 30px 40px;
            margin: 60px 0 60px 20px; /* 稍微向右縮排 */
            border-radius: 8px;
            box-shadow: var(--shadow-md);
        }
        .journal-block h3 { 
            margin-top: 0; color: var(--accent); font-size: 0.9rem; 
            text-transform: uppercase; letter-spacing: 1px; font-weight: 700;
        }
        .journal-block p { 
            font-size: 1.15rem; color: #2d3748; margin-bottom: 0; 
            font-style: italic; font-family: 'Georgia', serif; /* 區隔字體 */
        }
        /* 裝飾性引號 */
        .journal-block::after {
            content: '"'; position: absolute; right: 20px; bottom: -20px;
            font-size: 8rem; color: rgba(0,0,0,0.03); font-family: serif;
            pointer-events: none;
        }

        /* --- 底部導航 --- */
        .pagination { 
            display: flex; justify-content: space-between; align-items: center;
            margin-top: 80px; padding-top: 40px; 
            border-top: 1px dashed #cbd5e0; 
        }
        .btn { 
            display: inline-flex; align-items: center;
            padding: 12px 24px; background: white; 
            text-decoration: none; color: var(--text-main); font-weight: 600;
            border: 1px solid #e2e8f0; border-radius: 30px;
            transition: all 0.2s; box-shadow: var(--shadow-sm);
        }
        .btn:hover { 
            border-color: var(--accent); color: var(--accent); 
            transform: translateY(-2px); box-shadow: var(--shadow-md);
        }

        @keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
        
        @media (max-width: 600px) { 
            main { padding: 30px 15px; } 
            .timeline-container { padding-left: 15px; }
            .timeline-container::before { left: 0; }
            .media-item::before { left: -21px; width: 10px; height: 10px; }
            .journal-block { padding: 20px 25px; margin-left: 0; }
        }
    </style>
    """

def get_navbar_html(all_dates, current_page_key):
    """ 生成導航列 """
    links = []
    
    cls = 'class="active"' if current_page_key == 'home' else ''
    links.append(f'<a href="index.html" {cls}>首頁</a>')
    
    for i, date_str in enumerate(all_dates):
        # 簡短顯示日期，例如 11/22
        display_date = f"{date_str[4:6]}/{date_str[6:]}"
        cls = 'class="active"' if current_page_key == date_str else ''
        links.append(f'<a href="{date_str}.html" {cls}>Day {i+1}</a>')
        
    cls = 'class="active"' if current_page_key == 'summary' else ''
    links.append(f'<a href="summary.html" {cls}>總結</a>')
    
    return f"<nav><div class='nav-inner'>{''.join(links)}</div></nav>"

def create_html_file(filename, content, navbar, title="Travel Journal"):
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
    print(f"✨ 已生成美化版頁面: {filename}")

def main():
    print("正在讀取檔案清單...")
    data = parse_files(INPUT_FILE)
    if not data: return
    
    all_dates = list(data.keys())

    # --- 1. 首頁 (index.html) ---
    home_content = """
    <div class="page-header">
        <h1>我的旅遊日誌</h1>
        <p>收藏美好的時光與回憶</p>
    </div>
    <div class="home-grid">
    """
    for i, date_str in enumerate(all_dates):
        cover_img = ""
        for f in data[date_str]:
            if f['type'] == 'image':
                cover_img = f['filename']
                break
        
        if cover_img:
            img_html = f'<div class="card-img-wrap"><img src="{MEDIA_FOLDER}{cover_img}" loading="lazy"></div>'
        else:
            img_html = '<div class="card-img-wrap"><div class="placeholder-gradient"></div></div>'
        
        home_content += f"""
        <a href="{date_str}.html" class="day-card">
            {img_html}
            <div class="card-content">
                <h3>Day {i+1}</h3>
                <p>{date_str[:4]}.{date_str[4:6]}.{date_str[6:]} • {len(data[date_str])} 個項目</p>
            </div>
        </a>
        """
    
    # 總結卡片
    home_content += """
        <a href="summary.html" class="day-card">
            <div class="card-img-wrap"><div class="placeholder-gradient" style="background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%);"></div></div>
            <div class="card-content">
                <h3>旅程總結</h3>
                <p>心得、後記與精選回憶</p>
            </div>
        </a>
    </div>
    """
    create_html_file('index.html', home_content, get_navbar_html(all_dates, 'home'), "我的旅遊日誌")

    # --- 2. 每日內頁 ---
    for i, date_str in enumerate(all_dates):
        files = data[date_str]
        
        day_content = f"""
        <div class="page-header">
            <h1>Day {i+1}</h1>
            <p>{date_str[:4]} 年 {date_str[4:6]} 月 {date_str[6:]} 日</p>
        </div>
        <div class="timeline-container">
        """
        
        for idx, file in enumerate(files):
            fname = file['filename']
            
            if file['type'] == 'video':
                media_html = f'<video controls playsinline preload="metadata"><source src="{MEDIA_FOLDER}{fname}" type="video/mp4"></video>'
            else:
                media_html = f'<img src="{MEDIA_FOLDER}{fname}" loading="lazy">'
                
            day_content += f"""
            <article class="media-item">
                <div class="media-content">{media_html}</div>
                <div class="caption">
                    <div>這是 {fname} 的圖說...</div>
                    <div class="filename-ref">{fname}</div>
                </div>
            </article>
            """
            
            if (idx + 1) % 10 == 0:
                day_content += f"""
                <div class="journal-block">
                    <h3>Journal</h3>
                    <p>（請在此處編輯您的遊記文字... 記錄下這段旅程中，讓你印象深刻的聲音、味道或心情。）</p>
                </div>
                """
        
        day_content += "</div>" # End timeline-container
        
        # Pagination
        prev_link = f'{all_dates[i-1]}.html' if i > 0 else 'index.html'
        prev_text = '← 前一天' if i > 0 else '← 回目錄'
        next_link = f'{all_dates[i+1]}.html' if i < len(all_dates) - 1 else 'summary.html'
        next_text = '下一天 →' if i < len(all_dates) - 1 else '看總結 →'

        day_content += f"""
        <div class="pagination">
            <a href="{prev_link}" class="btn">{prev_text}</a>
            <a href="{next_link}" class="btn">{next_text}</a>
        </div>
        """
        
        create_html_file(f'{date_str}.html', day_content, get_navbar_html(all_dates, date_str), f"Day {i+1} - {date_str}")

    # --- 3. 總結頁 ---
    summary_content = """
    <div class="page-header">
        <h1>旅程總結</h1>
        <p>The End of the Journey</p>
    </div>
    <div class="journal-block" style="margin-left:0;">
        <h3>後記</h3>
        <p>（請在此處寫下整趟旅程的總結。旅行結束了，但回憶會留下來。）</p>
    </div>
    
    <div class="pagination">
        <a href="{}" class="btn">← 回到最後一天</a>
        <a href="index.html" class="btn">回首頁 🏠</a>
    </div>
    """.format(f"{all_dates[-1]}.html" if all_dates else "index.html")
    
    create_html_file('summary.html', summary_content, get_navbar_html(all_dates, 'summary'), "旅程總結")

    print("\n🎉 全部完成！網頁視覺已升級。請打開 index.html 欣賞。")

if __name__ == "__main__":
    main()