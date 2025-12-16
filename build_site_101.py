import os
import datetime
from collections import defaultdict

# --- 設定 ---
INPUT_FILE = 'files.txt'                   # 檔案清單
CSS_FILE = 'style.css'                     # 樣式表名稱
OUTPUT_HTML_IMG_PATH = 'photos_compressed/' # HTML 裡面圖片的連結路徑

# --- YouTube 影片對應表 ---
YOUTUBE_ID_MAP = {
    '20251122_092504.mp4': 'dQw4w9WgXcQ', 
}

# --- [新增] 每日行程區塊設定 (時間 HHMM, 標題) ---
# 程式會自動比對照片時間，將照片歸類到最近的區塊
DAILY_SCHEDULE = {
    '20251122': [
        ('0900', '🌞 早安出發'),
        ('1000', '🏯 參觀神社'),
        ('1200', '🍜 午餐時光'),
        ('1400', '🌳 漫步公園'),
        ('1630', '☕ 下午茶'),
        ('1800', '🌆 城市夜景'),
        ('1930', '🍽️ 晚餐：居酒屋'),
        ('2100', '🛏️ 回飯店休息'),
    ],
    '20251123': [
        ('0830', '🍳 飯店早餐'),
        ('1000', '⛰️ 登山健行'),
        ('1500', '🍦 休息一下'),
        ('1800', '🍖 燒肉大餐'),
    ],
    # 您可以依此類推增加其他日期的行程...
}

def get_css_content():
    """ 定義 CSS 樣式內容 (新增 Sub-Nav 與 Section 樣式) """
    return """
/* Reset & Base */
:root { 
    --bg-body: #f4f6f8; --bg-card: #ffffff;
    --text-main: #2d3748; --text-light: #718096;
    --accent: #3182ce; --accent-light: #ebf8ff;
    --shadow-sm: 0 1px 3px rgba(0,0,0,0.1);
    --shadow-md: 0 4px 6px rgba(0,0,0,0.08);
    --radius: 12px; 
    --nav-height: 64px;
    --sub-nav-height: 50px; /* 次級導航高度 */
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; } /* 平滑捲動 */
body {
    margin: 0; padding: 0;
    font-family: 'Noto Sans TC', sans-serif;
    background-color: var(--bg-body); color: var(--text-main);
    padding-top: var(--nav-height); /* 只保留主導航的高度，次導航會另外處理 */
    line-height: 1.6;
}

/* --- 主導航列 (Level 1) --- */
nav.main-nav {
    position: fixed; top: 0; left: 0; width: 100%; height: var(--nav-height);
    background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px);
    border-bottom: 1px solid rgba(0,0,0,0.05); z-index: 1000;
    display: flex; align-items: center; justify-content: center;
}
.nav-inner { width: 100%; max-width: 900px; padding: 0 20px; display: flex; overflow-x: auto; white-space: nowrap; }
.nav-inner::-webkit-scrollbar { display: none; }
nav.main-nav a {
    text-decoration: none; color: var(--text-light); font-weight: 500; 
    margin-right: 8px; padding: 8px 16px; border-radius: 20px; font-size: 0.95rem; transition: all 0.2s;
}
nav.main-nav a:hover { color: var(--accent); background: white; box-shadow: var(--shadow-sm); }
nav.main-nav a.active { background-color: var(--text-main); color: white; box-shadow: 0 2px 5px rgba(45, 55, 72, 0.3); }

/* --- [新增] 次級導航列 (Level 2: 行程區塊) --- */
nav.sub-nav {
    position: sticky; top: var(--nav-height); /* 黏在主導航下方 */
    left: 0; width: 100%; height: var(--sub-nav-height);
    background: rgba(255, 255, 255, 0.9); backdrop-filter: blur(8px);
    border-bottom: 1px solid rgba(0,0,0,0.05); z-index: 900;
    display: flex; align-items: center; justify-content: center;
    transition: top 0.3s;
}
.sub-nav-inner { 
    width: 100%; max-width: 720px; padding: 0 20px; 
    display: flex; overflow-x: auto; white-space: nowrap; gap: 10px;
}
.sub-nav-inner::-webkit-scrollbar { display: none; }
nav.sub-nav a {
    text-decoration: none; color: var(--text-light); font-size: 0.85rem; font-weight: 500;
    padding: 6px 14px; border-radius: 15px; background: rgba(0,0,0,0.03);
    transition: all 0.2s; border: 1px solid transparent;
}
nav.sub-nav a:hover { color: var(--accent); background: white; border-color: var(--accent); }
nav.sub-nav a.active { 
    background-color: var(--accent); color: white; 
    box-shadow: 0 2px 4px rgba(49, 130, 206, 0.3);
}

/* --- 內容區塊 --- */
main { width: 100%; max-width: 720px; margin: 0 auto; padding: 40px 20px 100px 20px; }
.page-header { text-align: center; margin-bottom: 50px; }
.page-header h1 { font-size: 2rem; font-weight: 700; margin-bottom: 8px; letter-spacing: -0.02em; }

/* --- [新增] 分段標題 --- */
.section-anchor { scroll-margin-top: 130px; /* 修正點擊跳轉時被導航列遮住的問題 */ }
.section-header {
    margin: 60px 0 30px 0; padding-bottom: 10px;
    border-bottom: 2px solid #edf2f7;
    color: var(--text-main); display: flex; align-items: center;
}
.section-header h2 { margin: 0; font-size: 1.5rem; color: var(--accent); }
.section-dot { 
    width: 12px; height: 12px; background: var(--accent); 
    border-radius: 50%; margin-right: 15px; display: inline-block;
}

/* Home Grid */
.home-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 24px; }
.day-card { 
    background: var(--bg-card); border-radius: var(--radius); overflow: hidden;
    text-decoration: none; color: var(--text-main); box-shadow: var(--shadow-sm);
    transition: transform 0.3s ease, box-shadow 0.3s ease; display: flex; flex-direction: column;
}
.day-card:hover { transform: translateY(-6px); box-shadow: 0 10px 15px rgba(0,0,0,0.08); }
.card-img-wrap { height: 180px; width: 100%; background: #e2e8f0; position: relative; overflow: hidden; }
.card-img-wrap img { width: 100%; height: 100%; object-fit: cover; transition: transform 0.5s ease; }
.day-card:hover .card-img-wrap img { transform: scale(1.05); }
.card-content { padding: 20px; }

/* Timeline */
.timeline-container { position: relative; padding-left: 20px; }
.timeline-container::before { content: ''; position: absolute; left: 0; top: 20px; bottom: 0; width: 2px; background: #e2e8f0; }
.media-item { 
    background: var(--bg-card); padding: 15px; border-radius: var(--radius);
    box-shadow: var(--shadow-md); margin-bottom: 40px; position: relative; animation: fadeIn 0.6s ease-out forwards;
}
.media-item::before {
    content: ''; position: absolute; left: -25px; top: 30px; width: 12px; height: 12px; background: white;
    border: 3px solid var(--accent); border-radius: 50%; z-index: 1;
}
.media-content { width: 100%; border-radius: 8px; overflow: hidden; background: #edf2f7; }
img, iframe { width: 100%; height: auto; display: block; }
iframe { aspect-ratio: 16 / 9; border: none; } 
.caption { padding: 15px 5px 5px 5px; font-size: 1rem; color: #4a5568; }
.filename-ref { font-size: 0.75rem; color: #a0aec0; margin-top: 6px; font-family: monospace; }
.journal-block {
    position: relative; background: linear-gradient(to right, #ffffff, #fcfcfc);
    border: 1px solid #e2e8f0; border-left: 5px solid var(--accent);
    padding: 30px 40px; margin: 60px 0 60px 20px; border-radius: 8px; box-shadow: var(--shadow-md);
}
.pagination { display: flex; justify-content: space-between; margin-top: 80px; padding-top: 40px; border-top: 1px dashed #cbd5e0; }
.btn { 
    padding: 12px 24px; background: white; text-decoration: none; color: var(--text-main); 
    border: 1px solid #e2e8f0; border-radius: 30px; font-weight: 600; box-shadow: var(--shadow-sm);
}
@keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
@media (max-width: 600px) { main { padding: 30px 15px; } .timeline-container::before { left: 0; } .media-item::before { left: -21px; } .journal-block { padding: 20px; margin-left: 0; } }
"""

def get_js_content():
    """ [新增] JavaScript 用於 ScrollSpy (滾動偵測) """
    return """
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        // 1. 取得所有區塊與導航連結
        const sections = document.querySelectorAll('.section-anchor');
        const navLinks = document.querySelectorAll('.sub-nav-inner a');
        
        // 如果沒有次導航，就不用執行
        if(navLinks.length === 0) return;

        // 2. 設定 IntersectionObserver
        const observerOptions = {
            root: null,
            rootMargin: '-20% 0px -60% 0px', // 視窗中間偏上的位置視為"啟用"區域
            threshold: 0
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    // 移除所有 active
                    navLinks.forEach(link => link.classList.remove('active'));
                    
                    // 找到對應的 id 並加上 active
                    const id = entry.target.getAttribute('id');
                    const activeLink = document.querySelector(`.sub-nav-inner a[href="#${id}"]`);
                    if (activeLink) {
                        activeLink.classList.add('active');
                        // 自動捲動導航列，讓 active 按鈕保持在視野內
                        activeLink.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' });
                    }
                }
            });
        }, observerOptions);

        sections.forEach(section => {
            observer.observe(section);
        });
    });
    </script>
    """

def write_css_file():
    print(f"正在建立/更新樣式表: {CSS_FILE} ...")
    with open(CSS_FILE, 'w', encoding='utf-8') as f:
        f.write(get_css_content())

def parse_files(filename):
    if not os.path.exists(filename):
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
            files_by_date[date_str].append({'filename': fname, 'datetime': dt, 'time_str': time_str[:4], # HHMM
                                            'type': 'video' if fname.lower().endswith(('.mp4', '.mov')) else 'image'})
        except ValueError: continue
    for date_key in files_by_date:
        files_by_date[date_key].sort(key=lambda x: x['datetime'])
    return dict(sorted(files_by_date.items()))

def get_navbar_html(all_dates, current_page_key):
    links = []
    cls = 'class="active"' if current_page_key == 'home' else ''
    links.append(f'<a href="index.html" {cls}>首頁</a>')
    for i, date_str in enumerate(all_dates):
        display_date = f"{date_str[4:6]}/{date_str[6:]}"
        cls = 'class="active"' if current_page_key == date_str else ''
        links.append(f'<a href="{date_str}.html" {cls}>Day {i+1}</a>')
    cls = 'class="active"' if current_page_key == 'summary' else ''
    links.append(f'<a href="summary.html" {cls}>總結</a>')
    return f"<nav class='main-nav'><div class='nav-inner'>{''.join(links)}</div></nav>"

def create_html_file(filename, content, navbar, sub_navbar, title):
    full_html = f"""
    <!DOCTYPE html>
    <html lang="zh-TW">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@300;400;500;700&display=swap" rel="stylesheet">
        <link rel="stylesheet" href="{CSS_FILE}">
    </head>
    <body>
        {navbar}
        {sub_navbar} 
        <main>{content}</main>
        {get_js_content()}
    </body>
    </html>
    """
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(full_html)
    print(f"已生成: {filename}")

def main():
    print("--- 開始建立網站 (含行程區塊功能) ---")
    if not os.path.exists(OUTPUT_HTML_IMG_PATH):
        print(f"警告: 找不到 '{OUTPUT_HTML_IMG_PATH}' 資料夾。")
    
    write_css_file()
    data = parse_files(INPUT_FILE)
    if not data: return
    all_dates = list(data.keys())

    # --- 生成首頁 ---
    home_content = """<div class="page-header"><h1>我的旅遊日誌</h1><p>收藏美好的時光與回憶</p></div><div class="home-grid">"""
    for i, date_str in enumerate(all_dates):
        cover_img = ""
        for f in data[date_str]:
            if f['type'] == 'image':
                cover_img = f['filename']
                break
        img_html = f'<div class="card-img-wrap"><img src="{OUTPUT_HTML_IMG_PATH}{cover_img}" loading="lazy"></div>' if cover_img else '<div class="card-img-wrap"><div class="placeholder-gradient"></div></div>'
        home_content += f"""<a href="{date_str}.html" class="day-card">{img_html}<div class="card-content"><h3>Day {i+1}</h3><p>{date_str[:4]}.{date_str[4:6]}.{date_str[6:]} • {len(data[date_str])} 個項目</p></div></a>"""
    home_content += """<a href="summary.html" class="day-card"><div class="card-img-wrap"><div style="width:100%;height:100%;background:#4a5568;"></div></div><div class="card-content"><h3>旅程總結</h3><p>心得、後記與精選回憶</p></div></a></div>"""
    create_html_file('index.html', home_content, get_navbar_html(all_dates, 'home'), "", "我的旅遊日誌")

    # --- 生成每日內頁 ---
    for i, date_str in enumerate(all_dates):
        files = data[date_str]
        
        # 1. 準備行程區塊
        schedule = DAILY_SCHEDULE.get(date_str, [])
        schedule.sort(key=lambda x: x[0]) # 確保按時間排序
        
        toc_links = []  # 儲存 (id, title) 用於生成次級導航
        current_schedule_idx = 0
        
        day_content = f"""<div class="page-header"><h1>Day {i+1}</h1><p>{date_str[:4]} 年 {date_str[4:6]} 月 {date_str[6:]} 日</p></div><div class="timeline-container">"""
        
        for idx, file in enumerate(files):
            # --- 檢查是否進入新時段 ---
            if current_schedule_idx < len(schedule):
                next_time, next_title = schedule[current_schedule_idx]
                file_time = file['time_str'] # HHMM
                
                # 如果目前檔案時間 >= 行程表設定的時間，插入標題
                if file_time >= next_time:
                    section_id = f"sec-{next_time}"
                    day_content += f"""
                    <div id="{section_id}" class="section-anchor"></div>
                    <div class="section-header">
                        <span class="section-dot"></span>
                        <h2>{next_title}</h2>
                    </div>
                    """
                    toc_links.append((section_id, next_title))
                    current_schedule_idx += 1

            fname = file['filename']
            if file['type'] == 'video':
                yt_id = YOUTUBE_ID_MAP.get(fname)
                if yt_id:
                    media_html = f"""<iframe src="https://www.youtube.com/embed/{yt_id}" title="YouTube" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>"""
                    caption_extra = "(YouTube 影片)"
                else:
                    media_html = f'<div style="padding:40px;background:#eee;text-align:center;color:#666;">影片 {fname} 尚未設定 YouTube ID</div>'
                    caption_extra = "(影片尚未連結)"
            else:
                media_html = f'<img src="{OUTPUT_HTML_IMG_PATH}{fname}" loading="lazy">'
                caption_extra = ""

            day_content += f"""<article class="media-item"><div class="media-content">{media_html}</div><div class="caption"><div>這是 {fname} 的圖說... {caption_extra}</div><div class="filename-ref">{fname}</div></div></article>"""
            
            if (idx + 1) % 10 == 0:
                day_content += f'<div class="journal-block"><h3>Journal</h3><p>（請在此處編輯您的遊記文字...）</p></div>'
        
        day_content += "</div>"
        
        # --- 生成次級導航列 HTML ---
        sub_navbar = ""
        if toc_links:
            sub_links_html = "".join([f'<a href="#{tid}">{ttitle}</a>' for tid, ttitle in toc_links])
            sub_navbar = f"<nav class='sub-nav'><div class='sub-nav-inner'>{sub_links_html}</div></nav>"

        prev_link = f'{all_dates[i-1]}.html' if i > 0 else 'index.html'
        next_link = f'{all_dates[i+1]}.html' if i < len(all_dates) - 1 else 'summary.html'
        day_content += f'<div class="pagination"><a href="{prev_link}" class="btn">← 前一天</a><a href="{next_link}" class="btn">下一天 →</a></div>'
        
        create_html_file(f'{date_str}.html', day_content, get_navbar_html(all_dates, date_str), sub_navbar, f"Day {i+1}")

    # --- 總結頁 ---
    summary_content = f"""<div class="page-header"><h1>旅程總結</h1><p>The End of the Journey</p></div><div class="journal-block" style="margin-left:0;"><h3>後記</h3><p>（請在此處寫下整趟旅程的總結。）</p></div><div class="pagination"><a href="{all_dates[-1] + '.html' if all_dates else 'index.html'}" class="btn">← 回到最後一天</a><a href="index.html" class="btn">回首頁 🏠</a></div>"""
    create_html_file('summary.html', summary_content, get_navbar_html(all_dates, 'summary'), "", "旅程總結")

    print("\n🎉 全部完成！網頁已生成，請開啟 index.html 查看效果。")

if __name__ == "__main__":
    main()