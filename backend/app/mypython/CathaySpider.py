from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

import re
import os
import time
import sys

# ======================== 輸入輸出 ========================
'''
Input (bash):
python3 CathaySpider.py <身分證號碼> <帳號名稱> <密碼> 

Output (ex): 
國泰網路銀行
銀行帳戶:xxx-xxx-xxx-xxx
可用現金: 9,999
股票市值: 9,999

股票明細:

股票名稱: Hims & Hers Health Inc 美國交易所, 目前庫存: 6, 庫存成本現值: USD 342.34 USD 336, 損益報酬率: - USD 6.34 -1.85%
股票名稱: Ondas Holdings Inc 美國交易所, 目前庫存: 100, 庫存成本現值: USD 526.53 USD 788, 損益報酬率: USD 261.47 +49.66%
股票名稱: UnitedHealth Group Inc 美國交易所, 目前庫存: 2, 庫存成本現值: USD 618.62 USD 695.38, 損益報酬率: USD 76.76 +12.41%
'''

if len(sys.argv) < 4:
    sys.stderr.write("Usage: test.py <id> <Account> <Password>\n")
    sys.exit(2)

id = sys.argv[1] 
Account = sys.argv[2]
Password = sys.argv[3]
 

CATHAY_id = os.getenv("CATHAY_ID", id)
CATHAYaccount = os.getenv("CATHAY_ACCOUNT", Account)
CATHAYpassword = os.getenv("CATHAY_PASSWORD", Password)

HEADLESS = True

# ======================== 基本設定 ========================
chrome_options = Options()
if HEADLESS:
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--window-size=1920,1080")
else:
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
driver.execute_script("arguments[0].value = arguments[1];", cust_input, CATHAY_id)

cust_input = WebDriverWait(driver, 20).until(
    EC.visibility_of_element_located((By.ID, "UserIdKeyin"))
)
driver.execute_script("arguments[0].value = arguments[1];", cust_input, CATHAYaccount)

cust_input = WebDriverWait(driver, 20).until(
    EC.visibility_of_element_located((By.ID, "PasswordKeyin"))
)
driver.execute_script("arguments[0].value = arguments[1];", cust_input, CATHAYpassword)

loginButton = WebDriverWait(driver, 20).until(
    EC.element_to_be_clickable((By.XPATH, "//button[@type='button' and @class='btn no-print btn-fill js-login btn btn-fill w-100 u-pos-relative' and @onclick='NormalDataCheck()']"))
)
driver.execute_script("arguments[0].click();", loginButton)

# ======================== 擷取資料 ========================
link_element = WebDriverWait(driver, 20).until(
    EC.visibility_of_element_located((By.XPATH, "//a[contains(@onclick, 'AutoGoMenu') and @class='link u-fs-14']"))
)

CathayAccount = link_element.text
print("國泰網路銀行")
print(f"銀行帳戶:{CathayAccount}")

balance_element = WebDriverWait(driver, 20).until(
    EC.visibility_of_element_located((By.ID, "TD-balance"))
)
balance_text = balance_element.text
print(f"可用現金: {balance_text}")

tabFUND = WebDriverWait(driver, 20).until(
    EC.element_to_be_clickable((By.ID, "tabFUND"))
)
driver.execute_script("arguments[0].click();", tabFUND)

fund_balance_element = WebDriverWait(driver, 20).until(
    EC.visibility_of_element_located((By.ID, "FUND-balance"))
)
fund_balance_text = fund_balance_element.text
print(f"股票市值: {fund_balance_text}\n\n股票明細:\n")

driver.execute_script("document.querySelector('a[href=\"javascript:void(0)\"][onclick=\"AutoGoMenu(\\'SAcctInq\\',\\'S0404_StockInq\\')\"]').click();")

# ======================== 股票明細 ========================
table = WebDriverWait(driver, 20).until(
    EC.presence_of_element_located((By.ID, "SubStocks"))
)

rows = table.find_elements(By.TAG_NAME, "tr")
for row in rows:
    cols = row.find_elements(By.TAG_NAME, "td")
    if len(cols) > 0:
        stock_name = cols[0].text.strip().replace("\n", " ")
        current_inventory = cols[1].text.strip()
        stock_cost_value = cols[2].text.strip().replace("\n", " ")
        profit_loss_rate = cols[3].text.strip().replace("\n", " ")
        print(f"股票名稱: {stock_name}, 目前庫存: {current_inventory}, 庫存成本現值: {stock_cost_value}, 損益報酬率: {profit_loss_rate}")

logout_button = WebDriverWait(driver, 20).until(
    EC.element_to_be_clickable((By.XPATH, "//a[@onclick='IsNeedCheckReconcil()']"))
)
driver.execute_script("arguments[0].click();", logout_button)


