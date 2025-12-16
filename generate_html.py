import os
import sys
import textwrap
try:
    from PIL import Image
except ImportError:
    print("錯誤: 需要 Pillow 套件。請執行: pip install Pillow")
    sys.exit(1)

# --- 使用者設定區 (Hardcoded Dates) ---
ALL_DATES = [
    '20251122',
    '20251123',
    '20251124',
    '20251125',
    '20251126',
    '20251127',
    '20251128',
    '20251129',
    '20251130',
]

# --- 路徑設定 ---
OUTPUT_HTML_IMG_PATH = 'photos_compressed/' # HTML 裡面的 src路徑
LOCAL_IMG_FOLDER = 'photos_compressed/'     # 本機讀取圖片尺寸的路徑
YOUTUBE_ID_FILE = 'youtube_id.txt'
CSS_FILE = 'style.css'
INDEX_CONFIG_FILE = 'index.txt'
SUMMARY_CONFIG_FILE = 'summary.txt'

# --- 輔助函式 ---

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
    return mapping

def get_image_dimensions(filename):
    path = os.path.join(LOCAL_IMG_FOLDER, filename)
    if not os.path.exists(path):
        return None, None
    try:
        with Image.open(path) as img:
            return img.width, img.height
    except:
        return None, None

def get_date_display(date_str):
    if len(date_str) != 8: return date_str
    return f"{date_str[:4]} 年 {date_str[4:6]} 月 {date_str[6:]} 日"

def get_formatted_date(date_str):
    if len(date_str) != 8: return date_str
    return f"{date_str[:4]}.{date_str[4:6]}.{date_str[6:]}"

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

def get_navbar_html(current_page_key):
    links = []
    cls = ' class="active"' if current_page_key == 'home' else ''
    links.append(f'<a href="index.html"{cls}>首頁</a>')
    for i, date_str in enumerate(ALL_DATES):
        cls = ' class="active"' if current_page_key == date_str else ''
        links.append(f'<a href="{date_str}.html"{cls}>Day {i+1}</a>')
    cls = ' class="active"' if current_page_key == 'summary' else ''
    links.append(f'<a href="summary.html"{cls}>總結</a>')
    return f'<nav class="main-nav"><div class="nav-inner">{"".join(links)}</div></nav>'

# --- 解析邏輯 (Parsing Logic) ---

def parse_p_block(buffer):
    """
    解析 p ... end p 區塊
    第一行是標題，其餘是內容
    """
    if not buffer:
        return None, None
    title = buffer[0]
    content = "<br>".join(buffer[1:]) if len(buffer) > 1 else ""
    return title, content

def parse_index_txt():
    """
    讀取 index.txt
    回傳: (main_title, subtitle, cover_map, journal_blocks)
    """
    default_title = "我的旅遊日誌"
    default_subtitle = "收藏美好的時光與回憶"
    cover_map = {}
    journal_blocks = []

    if not os.path.exists(INDEX_CONFIG_FILE):
        return default_title, default_subtitle, cover_map, journal_blocks

    with open(INDEX_CONFIG_FILE, 'r', encoding='utf-8') as f:
        lines = [l.rstrip() for l in f.readlines()] # 保留空白行結構但去除尾端換行

    # 讀取標題 (Line 1) 和 副標題 (Line 2)
    # 過濾掉開頭的空行
    content_lines = [l for l in lines if l]
    main_title = content_lines[0] if len(content_lines) > 0 else default_title
    subtitle = content_lines[1] if len(content_lines) > 1 else default_subtitle

    # 狀態機解析
    in_cover = False
    in_p = False
    p_buffer = []

    for line in lines:
        stripped = line.strip()
        
        # 狀態切換: front cover
        if stripped == 'front cover':
            in_cover = True
            continue
        elif stripped == 'end front cover':
            in_cover = False
            continue
        
        # 狀態切換: p
        if stripped == 'p':
            in_p = True
            p_buffer = []
            continue
        elif stripped == 'end p':
            in_p = False
            title, content = parse_p_block(p_buffer)
            if title:
                journal_blocks.append({'title': title, 'content': content})
            continue

        # 處理內容
        if in_cover and stripped:
            # 格式: DATE FILENAME (e.g., 20251122 img.jpg)
            parts = stripped.split(maxsplit=1)
            if len(parts) == 2:
                cover_map[parts[0]] = parts[1]
        
        elif in_p:
            # p 區塊內保留原樣 (包含空字串，轉成換行)
            p_buffer.append(line)

    return main_title, subtitle, cover_map, journal_blocks

def parse_summary_txt():
    """
    讀取 summary.txt
    回傳: (title, subtitle, journal_blocks)
    """
    default_title = "旅程總結"
    default_subtitle = ""
    journal_blocks = []

    if not os.path.exists(SUMMARY_CONFIG_FILE):
        return default_title, default_subtitle, journal_blocks

    with open(SUMMARY_CONFIG_FILE, 'r', encoding='utf-8') as f:
        lines = [l.rstrip() for l in f.readlines()]

    content_lines = [l for l in lines if l]
    title = content_lines[0] if len(content_lines) > 0 else default_title
    subtitle = content_lines[1] if len(content_lines) > 1 else default_subtitle

    in_p = False
    p_buffer = []

    for line in lines:
        stripped = line.strip()
        if stripped == 'p':
            in_p = True
            p_buffer = []
            continue
        elif stripped == 'end p':
            in_p = False
            j_title, j_content = parse_p_block(p_buffer)
            if j_title:
                journal_blocks.append({'title': j_title, 'content': j_content})
            continue
        
        if in_p:
            p_buffer.append(line)

    return title, subtitle, journal_blocks

def parse_date_txt(date_str):
    """
    讀取 {date}.txt
    格式更新: text/end text -> p/end p (第一行為標題)
    """
    filename = f"{date_str}.txt"
    if not os.path.exists(filename):
        print(f"提示: 找不到 {filename}，將略過此日期內容。")
        return [], 0, None

    blocks = []
    media_count = 0
    first_image = None
    
    in_section = False
    in_p = False
    
    section_buffer = []
    p_buffer = []
    section_counter = 0

    with open(filename, 'r', encoding='utf-8') as f:
        lines = [l.rstrip() for l in f.readlines()]

    for line in lines:
        stripped = line.strip()
        
        # 1. Section
        if stripped == 'section':
            in_section = True
            section_buffer = []
            continue
        elif stripped == 'end section':
            in_section = False
            if section_buffer:
                title = " ".join(section_buffer)
                blocks.append({
                    'type': 'section',
                    'title': title,
                    'id': f'sec-{section_counter}'
                })
                section_counter += 1
            continue
        
        if in_section:
            if stripped: section_buffer.append(stripped)
            continue

        # 2. p (Journal) - Updated Logic
        if stripped == 'p':
            in_p = True
            p_buffer = []
            continue
        elif stripped == 'end p':
            in_p = False
            title, content = parse_p_block(p_buffer)
            if title:
                blocks.append({
                    'type': 'journal',
                    'title': title,
                    'content': content
                })
            continue
        
        if in_p:
            p_buffer.append(line) # 保留原始行內容 (含空白)
            continue

        # 3. Media
        if not stripped:
            continue

        # --- [修正] 支援檔名中有空格 ---
        valid_exts = ['.jpg', '.jpeg', '.png', '.mp4', '.mov']
        lower_line = stripped.lower()
        
        split_pos = -1
        
        # 策略 A: 找尋 "副檔名 + 空格" (代表後面有圖說)
        # 我們要找"最早"出現的那個，以免圖說裡也有副檔名
        min_idx = len(stripped) + 1
        found_len = 0
        
        for ext in valid_exts:
            search_str = ext + " "
            idx = lower_line.find(search_str)
            if idx != -1 and idx < min_idx:
                min_idx = idx
                found_len = len(ext)
        
        if min_idx != len(stripped) + 1:
            split_pos = min_idx + found_len
        else:
            # 策略 B: 如果沒圖說，檢查是否直接以副檔名結尾
            for ext in valid_exts:
                if lower_line.endswith(ext):
                    split_pos = len(stripped)
                    break
        
        # 如果成功辨識出檔名
        if split_pos != -1:
            fname = stripped[:split_pos]
            description = stripped[split_pos:].strip()
            
            is_video = fname.lower().endswith(('.mp4', '.mov'))
            blocks.append({
                'type': 'media',
                'filename': fname,
                'caption': description,
                'is_video': is_video
            })
            media_count += 1
            if not is_video and first_image is None:
                first_image = fname

    return blocks, media_count, first_image

# --- 頁面生成函式 ---

def create_date_html(date_str, blocks, youtube_map, main_site_title):
    display_date = get_date_display(date_str)
    day_idx = ALL_DATES.index(date_str) + 1
    page_title = f"{main_site_title} Day {day_idx}" # Head Title
    
    # 1. Sub-Navbar
    sub_nav_links = []
    for b in blocks:
        if b['type'] == 'section':
            sub_nav_links.append(f'<a href="#{b["id"]}">{b["title"]}</a>')
    
    sub_navbar_html = ""
    if sub_nav_links:
        sub_navbar_html = f'<nav class="sub-nav"><div class="sub-nav-inner">{"".join(sub_nav_links)}</div></nav>'

    # 2. Content
    content_lines = []
    content_lines.append(f'<div class="page-header"><h1>Day {day_idx}</h1><p>{display_date}</p></div>')
    content_lines.append('<div class="timeline-container">')

    for b in blocks:
        if b['type'] == 'section':
            content_lines.append(f'\n    <div id="{b["id"]}" class="section-anchor"></div>')
            content_lines.append(f'    <div class="section-header"><span class="section-dot"></span><h2>{b["title"]}</h2></div>\n')
        
        elif b['type'] == 'journal':
            # 新的 Journal 結構：標題 + 內容
            content_lines.append(textwrap.dedent(f"""
            <div class="journal-block">
                <h3>{b['title']}</h3>
                <p>{b['content']}</p>
            </div>"""))
        
        elif b['type'] == 'media':
            fname = b['filename']
            caption_text = b['caption']
            caption_extra = ""
            media_html = ""

            if b['is_video']:
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
                img_attr = ' loading="lazy"'
                w, h = get_image_dimensions(fname)
                if w and h:
                    img_attr = f' width="{w}" height="{h}" loading="lazy" style="aspect-ratio:{w}/{h};"'
                media_html = f'<img src="{OUTPUT_HTML_IMG_PATH}{fname}"{img_attr}>'

            final_caption = caption_text if caption_text else f"這是 {fname} 的圖說... "
            if caption_extra:
                final_caption += f" {caption_extra}"

            content_lines.append(textwrap.dedent(f"""
            <article class="media-item">
                <div class="media-content">{media_html}</div>
                <div class="caption">
                    <div>{final_caption}</div>
                    <div class="filename-ref">{fname}</div>
                </div>
            </article>"""))

    content_lines.append('</div>')

    # Pagination
    idx = ALL_DATES.index(date_str)
    prev_link = f'{ALL_DATES[idx-1]}.html' if idx > 0 else 'index.html'
    prev_text = '← 前一天' if idx > 0 else '← 回首頁'
    next_link = f'{ALL_DATES[idx+1]}.html' if idx < len(ALL_DATES) - 1 else 'summary.html'
    next_text = '下一天 →' if idx < len(ALL_DATES) - 1 else '看總結 →'
    
    content_lines.append(f'\n<div class="pagination"><a href="{prev_link}" class="btn">{prev_text}</a><a href="{next_link}" class="btn">{next_text}</a></div>')

    full_html = textwrap.dedent(f"""
    <!DOCTYPE html>
    <html lang="zh-TW">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{page_title}</title>
        <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@300;400;500;700&display=swap" rel="stylesheet">
        <link rel="stylesheet" href="{CSS_FILE}">
    </head>
    <body>
    {get_navbar_html(date_str)}
    {sub_navbar_html}
    <main>
    {chr(10).join(content_lines)}
    </main>
    {get_js_content()}
    </body>
    </html>
    """).strip()

    with open(f"{date_str}.html", 'w', encoding='utf-8') as f:
        f.write(full_html)
    print(f"已生成: {date_str}.html (Title: {page_title})")


def create_index_html(day_infos, main_title, subtitle, journal_blocks, cover_map):
    """
    生成 index.html
    day_infos: list of dict {'date': '...', 'count': 123, 'cover': '...'}
    """
    content_lines = []
    content_lines.append(f'<div class="page-header"><h1>{main_title}</h1><p>{subtitle}</p></div>')
    content_lines.append('<div class="home-grid">')

    for info in day_infos:
        date_str = info['date']
        count = info['count']
        
        # 決定封面圖：優先查 index.txt 的設定，沒有則用當天第一張
        cover_img = cover_map.get(date_str, info['cover'])
        
        img_html = '<div class="placeholder-gradient"></div>'
        if cover_img:
            img_attr = ' loading="lazy"'
            w, h = get_image_dimensions(cover_img)
            if w and h:
                img_attr = f' width="{w}" height="{h}" style="aspect-ratio:{w}/{h};" loading="lazy"'
            img_html = f'<img src="{OUTPUT_HTML_IMG_PATH}{cover_img}"{img_attr}>'
        
        card_html = textwrap.dedent(f"""
        <a href="{date_str}.html" class="day-card">
            <div class="card-img-wrap">{img_html}</div>
            <div class="card-content"><h3>Day {ALL_DATES.index(date_str)+1}</h3><p>{get_formatted_date(date_str)} • {count} 個項目</p></div>
        </a>""")
        content_lines.append(card_html)

    # 總結卡片 (也檢查是否有自訂封面)
    summary_cover = cover_map.get('summary', '')
    summary_img_html = '<div style="width:100%;height:100%;background:#4a5568;"></div>' # 預設灰底
    if summary_cover:
        w, h = get_image_dimensions(summary_cover)
        img_attr = ' loading="lazy"'
        if w and h:
            img_attr = f' width="{w}" height="{h}" style="aspect-ratio:{w}/{h};" loading="lazy"'
        summary_img_html = f'<img src="{OUTPUT_HTML_IMG_PATH}{summary_cover}"{img_attr}>'

    content_lines.append(textwrap.dedent(f"""
    <a href="summary.html" class="day-card">
        <div class="card-img-wrap">{summary_img_html}</div>
        <div class="card-content"><h3>旅程總結</h3><p>心得、後記與精選回憶</p></div>
    </a>
    """).strip())
    
    content_lines.append('</div>')

    # 加入 index.txt 裡的 Journal Blocks
    if journal_blocks:
        content_lines.append('\n')
        for b in journal_blocks:
            content_lines.append(textwrap.dedent(f"""
            <div class="journal-block">
                <h3>{b['title']}</h3>
                <p>{b['content']}</p>
            </div>"""))

    full_html = textwrap.dedent(f"""
    <!DOCTYPE html>
    <html lang="zh-TW">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{main_title}</title>
        <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@300;400;500;700&display=swap" rel="stylesheet">
        <link rel="stylesheet" href="{CSS_FILE}">
    </head>
    <body>
    {get_navbar_html('home')}

    <main>
    {chr(10).join(content_lines)}
    </main>
    {get_js_content()}
    </body>
    </html>
    """).strip()

    with open("index.html", 'w', encoding='utf-8') as f:
        f.write(full_html)
    print(f"已生成: index.html (Title: {main_title})")

def create_summary_html(main_site_title, page_title, subtitle, journal_blocks):
    last_date_link = f"{ALL_DATES[-1]}.html" if ALL_DATES else "index.html"
    
    content_lines = []
    content_lines.append(f'<div class="page-header"><h1>{page_title}</h1><p>{subtitle}</p></div>')
    
    for b in journal_blocks:
        content_lines.append(textwrap.dedent(f"""
        <div class="journal-block">
            <h3>{b['title']}</h3>
            <p>{b['content']}</p>
        </div>"""))
        
    content_lines.append(f'<div class="pagination"><a href="{last_date_link}" class="btn">← 回到最後一天</a><a href="index.html" class="btn">回首頁 🏠</a></div>')

    full_html = textwrap.dedent(f"""
    <!DOCTYPE html>
    <html lang="zh-TW">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{main_site_title} summary</title>
        <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@300;400;500;700&display=swap" rel="stylesheet">
        <link rel="stylesheet" href="{CSS_FILE}">
    </head>
    <body>
    {get_navbar_html('summary')}

    <main>
    {chr(10).join(content_lines)}
    </main>
    {get_js_content()}
    </body>
    </html>
    """).strip()

    with open("summary.html", 'w', encoding='utf-8') as f:
        f.write(full_html)
    print("已生成: summary.html")

def main():
    print("--- 開始建置所有網頁 ---")
    
    # 1. 讀取設定檔 (Index & Summary)
    site_title, site_subtitle, cover_map, index_journals = parse_index_txt()
    summary_title, summary_subtitle, summary_journals = parse_summary_txt()
    youtube_map = load_youtube_ids(YOUTUBE_ID_FILE)
    
    day_infos = [] # 儲存每一天的統計資訊給 index 用

    # 2. 生成每一天的內頁
    for date_str in ALL_DATES:
        blocks, count, first_img = parse_date_txt(date_str)
        
        # 產生該日期的 HTML
        create_date_html(date_str, blocks, youtube_map, site_title)
        
        day_infos.append({
            'date': date_str,
            'count': count,
            'cover': first_img # 這是備案，如果 index.txt 沒指定封面就會用這個
        })

    # 3. 生成 index.html
    create_index_html(day_infos, site_title, site_subtitle, index_journals, cover_map)
    
    # 4. 生成 summary.html
    create_summary_html(site_title, summary_title, summary_subtitle, summary_journals)
    
    print("--- 全部完成 ---")

if __name__ == "__main__":
    main()