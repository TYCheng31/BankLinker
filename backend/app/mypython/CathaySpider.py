from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

import re
import os
import time

# ======== 認證參數（建議用環境變數帶入，避免硬編碼） ========
ESUN_id = os.getenv("ESUN_ID", "D123058213")
ESUNaccount = os.getenv("ESUN_ACCOUNT", "tycheng3103")
ESUNpassword = os.getenv("ESUN_PASSWORD", "nivekkevin3103")

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



    # ======================== 登入流程 ========================
driver.get("https://www.cathaybk.com.tw/mybank/")
wait = WebDriverWait(driver, 120)


cust_input = WebDriverWait(driver, 20).until(
    EC.visibility_of_element_located((By.ID, "CustID"))
)
driver.execute_script("arguments[0].value = arguments[1];", cust_input, ESUN_id)

cust_input = WebDriverWait(driver, 20).until(
    EC.visibility_of_element_located((By.ID, "UserIdKeyin"))
)
driver.execute_script("arguments[0].value = arguments[1];", cust_input, ESUNaccount)

cust_input = WebDriverWait(driver, 20).until(
    EC.visibility_of_element_located((By.ID, "PasswordKeyin"))
)
driver.execute_script("arguments[0].value = arguments[1];", cust_input, ESUNpassword)

loginButton = WebDriverWait(driver, 20).until(
    EC.element_to_be_clickable((By.XPATH, "//button[@type='button' and @class='btn no-print btn-fill js-login btn btn-fill w-100 u-pos-relative' and @onclick='NormalDataCheck()']"))
)
driver.execute_script("arguments[0].click();", loginButton)

link_element = WebDriverWait(driver, 20).until(
    EC.visibility_of_element_located((By.XPATH, "//a[contains(@onclick, 'AutoGoMenu') and @class='link u-fs-14']"))
)

CathayAccount = link_element.text
print(CathayAccount)

balance_element = WebDriverWait(driver, 20).until(
    EC.visibility_of_element_located((By.ID, "TD-balance"))
)
balance_text = balance_element.text
print(f"TD Balance: {balance_text}")

tabFUND = WebDriverWait(driver, 20).until(
    EC.element_to_be_clickable((By.ID, "tabFUND"))
)
driver.execute_script("arguments[0].click();", tabFUND)


fund_balance_element = WebDriverWait(driver, 20).until(
    EC.visibility_of_element_located((By.ID, "FUND-balance"))
)
fund_balance_text = fund_balance_element.text
print(f"Fund Balance: {fund_balance_text}")
time.sleep(1000)
logout_button = WebDriverWait(driver, 20).until(
    EC.element_to_be_clickable((By.XPATH, "//a[@onclick='IsNeedCheckReconcil()']"))
)
driver.execute_script("arguments[0].click();", logout_button)
# ======================== 等待你關閉瀏覽器 ========================
try:
    while driver.window_handles:  # 只要還有視窗就持續等
        time.sleep(1)
except KeyboardInterrupt:
    print("close")
finally:
    driver.quit()

