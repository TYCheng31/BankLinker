from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

import re
import os
import time

# ======== 認證參數（建議用環境變數帶入，避免硬編碼） ========
EsunId = os.getenv("ESUN_ID", "D123058213")
EsunAccount = os.getenv("ESUN_ACCOUNT", "tycheng31")
EsunPassword = os.getenv("ESUN_PASSWORD", "Nivekkevin31")

# 若你要在伺服器上跑可改為 True（headless）
HEADLESS = False

# ======================== 基本設定 ========================
chrome_options = Options()
if HEADLESS:
    # 新版 headless 模式
    chrome_options.add_argument("--headless=new")
    # headless 下沒有真正「最大化」概念，用視窗大小模擬
    chrome_options.add_argument("--window-size=1920,1080")
else:
    # 有視窗環境：啟動即最大化
    chrome_options.add_argument("--start-maximized")

chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")

driver = webdriver.Chrome(options=chrome_options)

# 再保險一次：有些桌面環境/視窗管理器下 start-maximized 可能無效
try:
    driver.maximize_window()             # 盡可能把外部視窗拉滿
except Exception:
    # 若最大化不支援，退而求其次設定位置與尺寸
    driver.set_window_position(0, 0)
    driver.set_window_size(1920, 1080)   # 也可視需求調成 2560x1440 等

# ======================== 登入流程 ========================
driver.get("https://www.cathaybk.com.tw/MyBank/")  # 國泰網銀登入或帳戶頁

for req in driver.requests:
    if req.response and "/api/" in (req.url or ""):
        ctype = (req.response.headers.get("Content-Type") or "").lower()
        if "application/json" in ctype:
            body = sw_decode(req.response.body, req.response.headers.get('Content-Encoding', 'identity'))
            print("API:", req.url)
            print(body.decode("utf-8", "ignore")[:1200])


# ======================== 等待你關閉瀏覽器 ========================
try:
    while driver.window_handles:  # 只要還有視窗就持續等
        time.sleep(1)
except KeyboardInterrupt:
    print("close")
finally:
    driver.quit()

