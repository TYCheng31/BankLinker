from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

import re
import os
import time

# ======== 認證參數（建議用環境變數帶入，避免硬編碼） ========
LineId = os.getenv("LINE_ID", "D123058213")
LineAccount = os.getenv("LINE_ACCOUNT", "TYCheng31")
LinePassword = os.getenv("LINE_PASSWORD", "Nivekkevin0331")

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
driver.get("https://accessibility.linebank.com.tw/transaction")
wait = WebDriverWait(driver, 15)

wait.until(EC.presence_of_element_located((By.ID, "nationalId"))).send_keys(LineId)
wait.until(EC.presence_of_element_located((By.ID, "userId"))).send_keys(LineAccount)
wait.until(EC.presence_of_element_located((By.ID, "pw"))).send_keys(LinePassword)

btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@title='登入友善網路銀行']")))
btn.click()

btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@title='確定']")))
btn.click()




#==================================================================

# 等到頁面關鍵字出現
wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(., '可用餘額')]")))

# 1) 主帳戶：() 內的數字
h2 = driver.find_element(By.XPATH, "//h2[contains(., '主帳戶')]")
txt = re.sub(r"\s+", "", h2.text)                     # 去掉換行/空白 → "主帳戶(111003906466)"
main_account = re.search(r"[（(]([0-9\-]+)[)）]", txt).group(1)
print("主帳戶：", main_account)

# 2) 可用餘額：NT$ + 金額
p = driver.find_element(By.XPATH, "//p[contains(., '可用餘額')]")
ptxt = re.sub(r"\s+", "", p.text)                     # 例如 "可用餘額NT$12,031"
m = re.search(r"NT\$?([0-9,]+(?:\.[0-9]+)?)", ptxt)
available_display = f"NT${m.group(1)}"
available_number = m.group(1).replace(",", "")
print("可用餘額：", available_display, "(純數值)", available_number)


# ======================== 等待你關閉瀏覽器 ========================
try:
    while driver.window_handles:  # 只要還有視窗就持續等
        time.sleep(1)
except KeyboardInterrupt:
    print("close")
finally:
    driver.quit()

