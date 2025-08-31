import sys
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import re
import os



line_id = os.getenv("LINE_ID", "D123058213")
account = os.getenv("LINE_ACCOUNT", "TYCheng31")
password = os.getenv("LINE_PASSWORD", "Nivekkevin0331")

# 若你要在伺服器上跑可改為 True（headless）
HEADLESS = True

# ======================== 基本設定 ========================
chrome_options = Options()
if HEADLESS:
    # 新版 headless 模式
    chrome_options.add_argument("--headless")
    # headless 下沒有真正「最大化」概念，用視窗大小模擬
    chrome_options.add_argument("--window-size=1920,1080")
else:
    # 有視窗環境：啟動即最大化
    chrome_options.add_argument("--start-maximized")

chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")

driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 30)  # 設置最大等待時間為30秒

try:
    # 登入流程
    print("[INFO] Opening login page...")
    driver.get("https://accessibility.linebank.com.tw/transaction")

    # 等待並填寫帳號和密碼
    print("[INFO] Entering login credentials...")
    wait.until(EC.presence_of_element_located((By.ID, "nationalId"))).send_keys(line_id)
    wait.until(EC.presence_of_element_located((By.ID, "userId"))).send_keys(account)
    wait.until(EC.presence_of_element_located((By.ID, "pw"))).send_keys(password)

    # 點選登入按鈕
    print("[INFO] Clicking login button...")
    login_btn = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[@title='登入友善網路銀行']"))
    )
    login_btn.click()

    # 處理彈窗（如果有）
    print("[INFO] Handling potential confirmation popup...")
    # 在執行關鍵操作後打印頁面 HTML 內容
    confirm_btn = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[@title='確定']"))
    )
    confirm_btn.click()

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

    result = {
        "account_name": main_account,
        "available_balance": f"NT${available_number}",
    }


except Exception as e:
    # 捕獲錯誤並顯示詳細的錯誤堆棧跟踪
    sys.stderr.write(f"[ERROR] {repr(e)}\n")
    traceback.print_exc()  # 這會顯示錯誤堆棧，幫助找出是哪一行出錯
    sys.exit(1)

finally:
    if driver:
        try:
            print("[INFO] Closing the browser...")
            driver.quit()  # 關閉瀏覽器
        except Exception as e:
            sys.stderr.write(f"[ERROR] Error quitting driver: {repr(e)}\n")

