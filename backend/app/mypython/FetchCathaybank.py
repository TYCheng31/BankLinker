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

def clean_balance(balance_text):
    """清理數字文本，去除逗號並轉換為數字。"""
    cleaned_text = re.sub(r',', '', balance_text)  # 去除逗號
    try:
        return int(cleaned_text)  # 轉換為浮動數字
    except ValueError:
        return 0.0  # 如果無法轉換為數字，則返回 0.0

try:
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

    # 清理並轉換為數字
    CathayCash = clean_balance(balance_text)

    tabFUND = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.ID, "tabFUND"))
    )
    driver.execute_script("arguments[0].click();", tabFUND)

    fund_balance_element = WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located((By.ID, "FUND-balance"))
    )
    fund_balance_text = fund_balance_element.text
    print(f"Fund Balance: {fund_balance_text}")

    # 清理並轉換為數字
    CathayStock = clean_balance(fund_balance_text)

    logout_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//a[@onclick='IsNeedCheckReconcil()']"))
    )
    driver.execute_script("arguments[0].click();", logout_button)

    result = {
        "account_name": CathayAccount,
        "available_balance": CathayCash,
        "stock": CathayStock,
    }

    # 輸出結果
    print(json.dumps(result))

except Exception as e:
    print(json.dumps({"error": str(e)}))
finally:
    driver.quit()
