from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

import re
import os
import json

import sys

if len(sys.argv) < 4:
    sys.stderr.write("Usage: test.py <account> <password> <id>\n")
    sys.exit(2)

Account = sys.argv[1]
Password = sys.argv[2]
id = sys.argv[3]  

#print(f"[INFO] Using account: {Account}")
#print(f"[INFO] Using id: {Line_id}")

ESUN_id = os.getenv("ESUN_ID", id)
ESUNaccount = os.getenv("ESUN_ACCOUNT", Account)
ESUNpassword = os.getenv("ESUN_PASSWORD", Password)


HEADLESS = True

# ======================== 基本設定 ========================
chrome_options = Options()
if HEADLESS:
    # 新版 headless 模式
    chrome_options.add_argument("--headless")
    # headless 下沒有真正「最大化」概念，用視窗大小模擬
    chrome_options.add_argument("--window-size=1920,1080")

chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")

driver = webdriver.Chrome(options=chrome_options)


try:

    # ======================== 登入流程 ========================
    driver.get("https://ebank.esunbank.com.tw/index.jsp")
    wait = WebDriverWait(driver, 120)

    # 先切進 iframe1
    driver.switch_to.default_content()
    WebDriverWait(driver, 20).until(
        EC.frame_to_be_available_and_switch_to_it((By.ID, "iframe1"))
    )

    # 找到 custid 欄位並輸入
    cust_input = WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located((By.ID, "loginform:custid"))
    )
    cust_input.clear()
    cust_input.send_keys(ESUN_id)

    cust_input = WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located((By.ID, "loginform:name"))
    )
    cust_input.clear()
    cust_input.send_keys(ESUNaccount)

    cust_input = WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located((By.ID, "loginform:pxsswd"))
    )
    cust_input.clear()
    cust_input.send_keys(ESUNpassword)

    login_btn = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.ID, "loginform:linkCommand"))
    )
    login_btn.click()


    span_el = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.ID, "_0"))
    )

    # 取文字內容
    EsunAccount = span_el.text.strip()
    #print("帳號：", EsunAccount)

    balance_td = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "td.td_money"))
    )

    # 取文字內容並去掉空白
    EsunCash = balance_td.text.strip()
    #print("可用餘額：", EsunCash)

    logout_button = driver.find_element(By.CSS_SELECTOR, "a.log_out")  # 使用CSS選擇器定位
    logout_button.click()

    result = {
        "account_name": EsunAccount,
        "available_balance": EsunCash
    }

    # 輸出結果
    print(json.dumps(result))

except Exception as e:
    print(json.dumps({"error": str(e)}))
finally:
    driver.quit()