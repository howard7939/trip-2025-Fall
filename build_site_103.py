import os
import datetime
import sys
import textwrap
from collections import defaultdict

# 嘗試匯入圖片處理庫 (只用來讀取尺寸，速度很快)
try:
    from PIL import Image
except ImportError:
    print("錯誤: 需要 Pillow 套件來讀取圖片尺寸以防止頁面跳動。")
    print("請執行: pip install Pillow")
    sys.exit(1)

# --- 設定 ---
INPUT_FILE = 'files.txt'                   # 檔案清單
CSS_FILE = 'style.css'                     # 樣式表名稱
OUTPUT_HTML_IMG_PATH = 'photos_compressed/' # HTML 裡面圖片的連結路徑
LOCAL_IMG_FOLDER = 'photos_compressed/'     # 本地實際讀取圖片的路徑 (用來測量尺寸)
YOUTUBE_ID_FILE = 'youtube_id.txt'         # YouTube ID 對應檔

# --- 每日行程區塊設定 ---
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
    '20251124': [
        ('0900', '🏖️ 海灘散步'),
        ('1200', '🍣 壽司午餐'),
        ('1400', '🛍️ 購物時間'),
        ('1700', '🌇 夕陽美景'),
        ('2000', '🍜 夜市小吃'),
    ],
    '20251125': [
        ('0800', '☕ 早餐咖啡'),
        ('1000', '🏛️ 博物館參觀'),
        ('1300', '🍲 午餐聚會'),
        ('1500', '🎡 遊樂園玩樂'),
        ('1900', '🍰 甜點時間'),
    ],
    '20251126': [
        ('0900', '🥐 早餐時光'),
        ('1100', '🌸 花園漫步'),
        ('1300', '🍛 午餐咖哩'),
        ('1500', '🛶 湖上划船'),
        ('1800', '🍤 海鮮晚餐'),
    ],
    '20251127': [
        ('0800', '🌞 早安出發'),
        ('1000', '🏯 參觀神社'),
        ('1200', '🍜 午餐時光'),
        ('1400', '🌳 漫步公園'),
        ('1630', '☕ 下午茶'),
        ('1800', '🌆 城市夜景'),
        ('1930', '🍽️ 晚餐：居酒屋'),
        ('2100', '🛏️ 回飯店休息'),
    ],
    '20251128': [
        ('0830', '🍳 飯店早餐'),
        ('1000', '⛰️ 登山健行'),
        ('1500', '🍦 休息一下'),
        ('1800', '🍖 燒肉大餐'),
    ],
    '20251129': [
        ('0900', '🏖️ 海灘散步'),
        ('1200', '🍣 壽司午餐'),
        ('1400', '🛍️ 購物時間'),
        ('1700', '🌇 夕陽美景'),
        ('2000', '🍜 夜市小吃'),
    ],
    '20251130': [
        ('0800', '☕ 早餐咖啡'),
        ('1000', '🏛️ 博物館參觀'),
        ('1300', '🍲 午餐聚會'),
        ('1500', '🎡 遊樂園玩樂'),
        ('1900', '🍰 甜點時間'),
    ]
}

def load_youtube_ids(filename):
    mapping = {}
    if not os.path.exists(filename):
        return mapping
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 2:
                fname = parts[0]
                url_or_id = parts[1]
                if 'youtu.be' in url_or_id or 'youtube.com' in url_or_id:
                    if '=' in url_or_id: vid_id = url_or_id.split('=')[-1]
                    else: vid_id = url_or_id.split('/')[-1]
                else: vid_id = url_or_id
                mapping[fname] = vid_id
    print(f"已載入 {len(mapping)} 筆 YouTube 設定。")
    return mapping

def get_image_dimensions(filename):
    """ 
    [新增] 讀取圖片尺寸 
    這能讓瀏覽器預留空間，解決點擊跳轉不準的問題 
    """
    path = os.path.join(LOCAL_IMG_FOLDER, filename)
    if not os.path.exists(path):
        return None, None
    try:
        with Image.open(path) as img:
            return img.width, img.height
    except:
        return None, None

def get_css_content():
    return textwrap.dedent("""
    /* Reset & Base */
    :root { 
        --bg-body: #f4f6f8; --bg-card: #ffffff;
        --text-main: #2d3748; --text-light: #718096;
        --accent: #3182ce; --accent-light: #ebf8ff;
        --shadow-sm: 0 1px 3px rgba(0,0,0,0.1);
        --shadow-md: 0 4px 6px rgba(0,0,0,0.08);
        --radius: 12px; 
        --nav-height: 64px;
        --sub-nav-height: 54px;
    }
    * { box-sizing: border-box; }
    html { scroll-behavior: smooth; }
    body {
        margin: 0; padding: 0;
        font-family: 'Noto Sans TC', sans-serif;
        background-color: var(--bg-body); color: var(--text-main);
        padding-top: var(--nav-height);
        line-height: 1.6;
    }
    /* 導航列與基礎樣式 */
    nav.main-nav {
        position: fixed; top: 0; left: 0; width: 100%; height: var(--nav-height);
        background: rgba(255, 255, 255, 0.98); backdrop-filter: blur(10px);
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

    nav.sub-nav {
        position: sticky; top: var(--nav-height); 
        left: 0; width: 100%; height: var(--sub-nav-height);
        background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(8px);
        border-bottom: 1px solid rgba(0,0,0,0.08); z-index: 900;
        display: flex; align-items: center; justify-content: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    .sub-nav-inner { 
        width: 100%; max-width: 720px; padding: 0 20px; 
        display: flex; overflow-x: auto; white-space: nowrap; gap: 8px;
        align-items: center; height: 100%;
    }
    .sub-nav-inner::-webkit-scrollbar { display: none; }
    nav.sub-nav a {
        text-decoration: none; color: var(--text-light); font-size: 0.9rem; font-weight: 500;
        padding: 6px 16px; border-radius: 20px; background: transparent;
        transition: all 0.2s; border: 1px solid transparent; flex-shrink: 0;
    }
    nav.sub-nav a:hover { color: var(--accent); background: #f7fafc; }
    nav.sub-nav a.active { 
        background-color: var(--accent); color: white; 
        box-shadow: 0 2px 4px rgba(49, 130, 206, 0.4);
    }

    main { width: 100%; max-width: 720px; margin: 0 auto; padding: 40px 20px 100px 20px; }
    .page-header { text-align: center; margin-bottom: 50px; }
    .page-header h1 { font-size: 2rem; font-weight: 700; margin-bottom: 8px; letter-spacing: -0.02em; }

    /* Anchor Offset Fix */
    .section-anchor { scroll-margin-top: 130px; display: block; height: 0; width: 0; visibility: hidden; }

    .section-header {
        margin: 50px 0 25px 0; padding-bottom: 10px;
        border-bottom: 2px solid #edf2f7;
        color: var(--text-main); display: flex; align-items: center;
    }
    .section-header h2 { margin: 0; font-size: 1.4rem; color: var(--accent); }
    .section-dot { 
        width: 10px; height: 10px; background: var(--accent); 
        border-radius: 50%; margin-right: 12px; display: inline-block;
    }

    /* Grid & Cards */
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
    
    /* Media Content (CSS Aspect Ratio fallback) */
    .media-content { width: 100%; border-radius: 8px; overflow: hidden; background: #edf2f7; }
    /* 這裡重要：確保圖片自適應但有基本樣式 */
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
    """).strip()

def get_js_content():
    return textwrap.dedent("""
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        const navLinks = document.querySelectorAll('.sub-nav-inner a');
        if(navLinks.length === 0) return;

        const sections = document.querySelectorAll('.section-anchor');
        let isClicking = false;

        navLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                navLinks.forEach(l => l.classList.remove('active'));
                this.classList.add('active');
                isClicking = true;
                setTimeout(() => { isClicking = false; }, 800); 
                this.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' });
            });
        });

        window.addEventListener('scroll', function() {
            if (isClicking) return;
            let current = '';
            const triggerLine = window.scrollY + 150; 
            sections.forEach(section => {
                if (triggerLine >= section.offsetTop) {
                    current = section.getAttribute('id');
                }
            });
            if ((window.innerHeight + window.scrollY) >= document.body.offsetHeight - 50) {
                if (sections.length > 0) current = sections[sections.length - 1].getAttribute('id');
            }
            navLinks.forEach(link => {
                link.classList.remove('active');
                if (link.getAttribute('href') === '#' + current) {
                    link.classList.add('active');
                    link.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' });
                }
            });
        });
    });
    </script>
    """).strip()

def write_css_file():
    print(f"[{datetime.datetime.now().time()}] 更新樣式表: {CSS_FILE}")
    with open(CSS_FILE, 'w', encoding='utf-8') as f:
        f.write(get_css_content())

def parse_files(filename):
    if not os.path.exists(filename): return {}
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
            files_by_date[date_str].append({'filename': fname, 'datetime': dt, 'time_str': time_str[:4],
                                            'type': 'video' if fname.lower().endswith(('.mp4', '.mov')) else 'image'})
        except ValueError: continue
    for date_key in files_by_date:
        files_by_date[date_key].sort(key=lambda x: x['datetime'])
    return dict(sorted(files_by_date.items()))

def get_navbar_html(all_dates, current_page_key):
    links = []
    cls = ' class="active"' if current_page_key == 'home' else ''
    links.append(f'<a href="index.html"{cls}>首頁</a>')
    for i, date_str in enumerate(all_dates):
        cls = ' class="active"' if current_page_key == date_str else ''
        links.append(f'<a href="{date_str}.html"{cls}>Day {i+1}</a>')
    cls = ' class="active"' if current_page_key == 'summary' else ''
    links.append(f'<a href="summary.html"{cls}>總結</a>')
    return f'<nav class="main-nav"><div class="nav-inner">{"".join(links)}</div></nav>'

def create_html_file(filename, content, navbar, sub_navbar, title):
    full_html = textwrap.dedent(f"""
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
    <main>
    {content}
    </main>
    {get_js_content()}
    </body>
    </html>
    """).strip()
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(full_html)
    print(f"已生成: {filename}")

def build_html(targets):
    if not targets:
        print("請指定要建置的目標，例如 targets = ['all']")
        return
    build_all = 'all' in targets
    print("--- 開始建置網站 ---")
    
    youtube_map = load_youtube_ids(YOUTUBE_ID_FILE)
    data = parse_files(INPUT_FILE)
    if not data: return
    all_dates = list(data.keys())

    if build_all or CSS_FILE in targets or 'css' in targets:
        write_css_file()

    # --- 首頁 ---
    if build_all or 'index.html' in targets or 'index' in targets:
        home_lines = []
        home_lines.append('<div class="page-header"><h1>我的旅遊日誌</h1><p>收藏美好的時光與回憶</p></div>')
        home_lines.append('<div class="home-grid">')
        for i, date_str in enumerate(all_dates):
            cover_img = ""
            for f in data[date_str]:
                if f['type'] == 'image':
                    cover_img = f['filename']
                    break
            
            # [新增] 讀取尺寸，防止首頁跳動 (可選)
            img_attr = ""
            if cover_img:
                w, h = get_image_dimensions(cover_img)
                if w and h:
                    img_attr = f' width="{w}" height="{h}" style="aspect-ratio:{w}/{h};"'

            img_html = f'<img src="{OUTPUT_HTML_IMG_PATH}{cover_img}"{img_attr} loading="lazy">' if cover_img else '<div class="placeholder-gradient"></div>'
            
            card_html = (
                f'    <a href="{date_str}.html" class="day-card">\n'
                f'        <div class="card-img-wrap">{img_html}</div>\n'
                f'        <div class="card-content"><h3>Day {i+1}</h3><p>{date_str[:4]}.{date_str[4:6]}.{date_str[6:]} • {len(data[date_str])} 個項目</p></div>\n'
                f'    </a>'
            )
            home_lines.append(card_html)
        home_lines.append('    <a href="summary.html" class="day-card"><div class="card-img-wrap"><div style="width:100%;height:100%;background:#4a5568;"></div></div><div class="card-content"><h3>旅程總結</h3><p>心得、後記與精選回憶</p></div></a>')
        home_lines.append('</div>')
        create_html_file('index.html', '\n'.join(home_lines), get_navbar_html(all_dates, 'home'), "", "我的旅遊日誌")

    # --- 內頁 ---
    for i, date_str in enumerate(all_dates):
        target_name = f"{date_str}.html"
        if not build_all and date_str not in targets and target_name not in targets:
            continue

        files = data[date_str]
        schedule = DAILY_SCHEDULE.get(date_str, [])
        schedule.sort(key=lambda x: x[0])
        
        toc_links = []
        current_schedule_idx = 0
        day_lines = []
        day_lines.append(f'<div class="page-header"><h1>Day {i+1}</h1><p>{date_str[:4]} 年 {date_str[4:6]} 月 {date_str[6:]} 日</p></div>')
        day_lines.append('<div class="timeline-container">')
        
        for idx, file in enumerate(files):
            # 行程區塊
            if current_schedule_idx < len(schedule):
                next_time, next_title = schedule[current_schedule_idx]
                if file['time_str'] >= next_time:
                    section_id = f"sec-{next_time}"
                    day_lines.append(f'\n    <div id="{section_id}" class="section-anchor"></div>')
                    day_lines.append(f'    <div class="section-header"><span class="section-dot"></span><h2>{next_title}</h2></div>\n')
                    toc_links.append((section_id, next_title))
                    current_schedule_idx += 1

            fname = file['filename']
            if file['type'] == 'video':
                yt_id = youtube_map.get(fname)
                if yt_id:
                    media_html = (
                        f'<iframe width="100%" height="100%" '
                        f'src="https://www.youtube.com/embed/{yt_id}?rel=0" '
                        f'title="YouTube video player" frameborder="0" '
                        f'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" '
                        f'referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>'
                    )
                    caption_extra = "(YouTube 影片)"
                else:
                    media_html = f'<div style="padding:40px;background:#eee;text-align:center;color:#666;">影片 {fname} 尚未設定 YouTube ID</div>'
                    caption_extra = "(影片尚未連結)"
            else:
                # [修正重點] 讀取並寫入圖片尺寸
                img_attr = ' loading="lazy"'
                w, h = get_image_dimensions(fname)
                if w and h:
                    # 加入 width, height 與 aspect-ratio
                    img_attr = f' width="{w}" height="{h}" loading="lazy" style="aspect-ratio:{w}/{h};"'
                
                media_html = f'<img src="{OUTPUT_HTML_IMG_PATH}{fname}"{img_attr}>'
                caption_extra = ""

            item_html = (
                f'    <article class="media-item">\n'
                f'        <div class="media-content">{media_html}</div>\n'
                f'        <div class="caption">\n'
                f'            <div>這是 {fname} 的圖說... {caption_extra}</div>\n'
                f'            <div class="filename-ref">{fname}</div>\n'
                f'        </div>\n'
                f'    </article>'
            )
            day_lines.append(item_html)
            
            if (idx + 1) % 10 == 0:
                day_lines.append('\n    <div class="journal-block"><h3>Journal</h3><p>（請在此處編輯您的遊記文字...）</p></div>\n')
        
        day_lines.append('</div>')
        sub_navbar = ""
        if toc_links:
            sub_links_html = "".join([f'<a href="#{tid}">{ttitle}</a>' for tid, ttitle in toc_links])
            sub_navbar = f'<nav class="sub-nav"><div class="sub-nav-inner">{sub_links_html}</div></nav>'
        prev_link = f'{all_dates[i-1]}.html' if i > 0 else 'index.html'
        next_link = f'{all_dates[i+1]}.html' if i < len(all_dates) - 1 else 'summary.html'
        day_lines.append(f'\n<div class="pagination"><a href="{prev_link}" class="btn">← 前一天</a><a href="{next_link}" class="btn">下一天 →</a></div>')
        create_html_file(target_name, '\n'.join(day_lines), get_navbar_html(all_dates, date_str), sub_navbar, f"Day {i+1}")

    if build_all or 'summary.html' in targets or 'summary' in targets:
        summary_lines = []
        summary_lines.append('<div class="page-header"><h1>旅程總結</h1><p>The End of the Journey</p></div>')
        summary_lines.append('<div class="journal-block" style="margin-left:0;"><h3>後記</h3><p>（請在此處寫下整趟旅程的總結。）</p></div>')
        summary_lines.append(f'<div class="pagination"><a href="{all_dates[-1] + ".html" if all_dates else "index.html"}" class="btn">← 回到最後一天</a><a href="index.html" class="btn">回首頁 🏠</a></div>')
        create_html_file('summary.html', '\n'.join(summary_lines), get_navbar_html(all_dates, 'summary'), "", "旅程總結")

def main():
    targets = ['all']
    build_html(targets)

if __name__ == "__main__":
    main()