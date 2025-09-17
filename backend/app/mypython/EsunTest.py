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
ESUNaccount = os.getenv("ESUN_ACCOUNT", "tycheng31")
ESUNpassword = os.getenv("ESUN_PASSWORD", "Nivekkevin31")

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
EsunAccount = span_el.text.strip()
print("ESUNAccount：", EsunAccount)


personal_balance_sheet = WebDriverWait(driver, 20).until(
    EC.presence_of_element_located((By.XPATH, "//a[text()='個人資產負債表']"))
)
driver.execute_script("arguments[0].click();", personal_balance_sheet)

balance_td = WebDriverWait(driver, 20).until(
    EC.presence_of_element_located((By.ID, "fms01010a:twTd2"))
)

# 取得文本並去掉逗號
balance_text = balance_td.text.strip().replace(",", "")

# 將文本轉換為數字
balance_value = int(balance_text)

print("ESUNCash:", balance_value)

balance_td = WebDriverWait(driver, 20).until(
    EC.presence_of_element_located((By.ID, "fms01010a:stockTd2"))
)

# 取得文本並去掉逗號
balance_text = balance_td.text.strip().replace(",", "")

# 將文本轉換為數字
balance_value = int(balance_text)

print("ESUNStock:", balance_value)

logout_button = driver.find_element(By.CSS_SELECTOR, "a.log_out")  # 使用CSS選擇器定位
logout_button.click()





# ======================== 等待你關閉瀏覽器 ========================
try:
    while driver.window_handles:  # 只要還有視窗就持續等
        time.sleep(1)
except KeyboardInterrupt:
    print("close")
finally:
    driver.quit()

