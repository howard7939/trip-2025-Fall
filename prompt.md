**角色設定：**
你是一位全端工程師，擅長 Python 自動化腳本與現代 RWD 網頁設計。

**專案目標：**
我有一份包含數百個旅遊照片與影片檔名的清單 (`files.txt`)。
請為我撰寫一個 **Python Script (`build_site.py`)**。
當我執行這個 Python script 時，它要讀取 `files.txt`，並自動生成一個完整的靜態旅遊網站 (`index.html`)。

**輸入資料 (`files.txt` 內容範例)：**
20251122_092133.jpg
20251122_092504.mp4
... (格式為 YYYYMMDD_HHMMSS)

**核心需求變更 (與一般相簿不同)：**
1.  **瀏覽模式 (Feed Style)：**
    * **不要**使用 Masonry (瀑布流) 或 Lightbox (點擊放大)。
    * **要**使用類似 Instagram 或 Blog 的「單欄滾動」模式。使用者不需要點擊，往下滑動即可直接看到大圖與影片。
    * **RWD 設定：** 在手機上滿版顯示；在電腦桌面上，內容需限制在中間 (Max-width: 600px ~ 800px)，置中排列，確保在大螢幕上瀏覽也很舒適，不會太寬。

2.  **圖文配置邏輯：**
    * **每一張** 圖片/影片下方，都要預留一個「圖說 (Caption)」的文字區域。
    * **每隔 10 個** 媒體檔案，請自動插入一個「旅程段落文字 (Journal Section)」的區塊。
    * **自動分頁：** 依然依照檔名日期的 `YYYYMMDD` 自動將內容分到不同日期的區塊 (Section) 或頁面中。

**Python Script (`build_site.py`) 的詳細邏輯：**

1.  **讀取與解析：**
    * 讀取同目錄下的 `files.txt`。
    * 解析檔名時間戳記，依日期分組，並在日內依時間排序。

2.  **HTML 生成 (Jinja2 或 f-string)：**
    * 請在 Python code 內包含 HTML/CSS 的模板 (Template)。
    * **CSS 重點：**
        * `container`: `max-width: 700px; margin: 0 auto;` (電腦版置中)。
        * `media-item`: `width: 100%; display: block; margin-bottom: 10px;` (圖片自適應寬度)。
        * `caption`: `font-size: 0.9rem; color: #555; margin-bottom: 40px;` (圖說)。
        * `journal-block`: `padding: 20px; background-color: #f9f9f9; margin: 50px 0; font-size: 1.1rem; line-height: 1.6;` (穿插的長文區塊)。
        * 導航列 (Navbar)：置頂固定，可快速跳轉不同日期 (Day 1, Day 2...)。
    * **影片處理：** 遇到 `.mp4` 時，使用 `<video controls playsinline preload="metadata">` 標籤，並設定寬度 100%。
    * **圖片處理：** 使用 `<img loading="lazy">` 以優化長網頁載入效能。

3.  **文字內容處理 (Placeholder)：**
    * 由於我尚未提供具體文字，請在 Python 生成 HTML 時，自動填入預設文字：
        * 圖說填入：`"這是 20251122_092133.jpg 的圖說..."`
        * 長文區塊填入：`"<h3>旅程記錄</h3><p>（請在此處編輯您的遊記文字...）</p>"`
    * 生成後的 `index.html` 應該要讓我可以用文字編輯器打開，利用「搜尋取代」功能，輕鬆把這些預設文字換成我真正的遊記。

**交付產出：**
請提供完整的 `build_site.py` 程式碼。我只要執行它，就能得到 `index.html`。