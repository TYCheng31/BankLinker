# BankLinker  

## Proposed  
* Connect all bank account in this system, user can check the balance in a short time.  
* setup update time, so that user can see the change of the balance.  

## Architecture  
* Frontend: React  
* Backend: FastAPI  
* Database: PostgreSQL  
* OS: Ubuntu 24.04 LTS  

## Version

### v1.2.2

- 新增更新bankcard後會自己刷新介面，取得資料庫資料

### v1.2.1

 新增資料庫欄位、修改前端bankcard邏輯

- 資料庫新增BcCash、BcMainaccount
    - 用來記錄主帳戶、現金
- bancard顯示會自己去資料庫找歷史資料顯示
- 修好玉山銀行連續登入問題
- 新增、修改按鈕ICON
- 新增center不同頁面

### v1.2.0

 新增玉山銀行、修改API

- 新增玉山銀行爬蟲程式
- 修改前端程式碼

### v1.1.1

 更新程式邏輯

- 更新前端程式碼 (api統一在index.js修改，原本是寫在post前面)
- 刷新按鈕按完後會更新時間到資料庫last_update裡面
- 各個bankCard顯示為自己在資料庫中的last_update

### v1.1.0

 新增按鈕

- 新增bankCard刪除按鈕
- bankCard有獨立刷新按鈕
- 右側版本資訊

### v1.0.0

 初代介面

- Dashboard全新介面
- BankCard Logo完成 (LINEBANK、ESUNBANK、CATHAYBANK)