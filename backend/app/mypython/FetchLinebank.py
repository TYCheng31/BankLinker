import sys
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException

import re
import json
import os

if len(sys.argv) < 4:
    sys.stderr.write("Usage: test.py <account> <password> <id>\n")
    sys.exit(2)

Account = sys.argv[1]
Password = sys.argv[2]
Line_id = sys.argv[3]  

#print(f"[INFO] Using account: {Account}")
#print(f"[INFO] Using id: {Line_id}")

line_id = os.getenv("LINE_ID", Line_id)
account = os.getenv("LINE_ACCOUNT", Account)
password = os.getenv("LINE_PASSWORD", Password)

HEADLESS = True

# ======================== 基本設定 ========================
chrome_options = Options()
if HEADLESS:
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920,1080")


chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")

driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 30) 

try:
    driver.get("https://accessibility.linebank.com.tw/transaction")

    wait.until(EC.presence_of_element_located((By.ID, "nationalId"))).send_keys(line_id)
    wait.until(EC.presence_of_element_located((By.ID, "userId"))).send_keys(account)
    wait.until(EC.presence_of_element_located((By.ID, "pw"))).send_keys(password)

    login_btn = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[@title='登入友善網路銀行']"))
    )
    login_btn.click()

    confirm_btn = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[@title='確定']"))
    )
    confirm_btn.click()

    wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(., '可用餘額')]")))

    h2 = driver.find_element(By.XPATH, "//h2[contains(., '主帳戶')]")
    txt = re.sub(r"\s+", "", h2.text)                    
    main_account = re.search(r"[（(]([0-9\-]+)[)）]", txt).group(1)

    p = driver.find_element(By.XPATH, "//p[contains(., '可用餘額')]")
    ptxt = re.sub(r"\s+", "", p.text)                    
    m = re.search(r"NT\$?([0-9,]+(?:\.[0-9]+)?)", ptxt)
    available_display = f"NT${m.group(1)}"
    available_number = m.group(1).replace(",", "")
    available_number = available_display.replace("NT$", "").strip()

    result = {
        "account_name": main_account,
        "available_balance": available_number
    }

    print(json.dumps(result))

except Exception as e:
    print(json.dumps({"error": str(e)}))
finally:
    driver.quit()

