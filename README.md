20240908 17:20更新  
1.LogIn 加上 LOGO  
2.忘記密碼從 帳號、舊密碼、新密碼 ---> 帳號、姓名、新密碼  
20240909 17:15更新  
1.資料庫改線上存取  

# 專題  
## 寫法   
	.ui 檔案在gui，每一個畫面一個檔案，所需的對應函數程式在 \gui\function裡，方便維護  
## 完整執行步驟  
### 1.開啟 linebot\ngrok-v3-stable-windows-amd64\ngrok.exe  
	輸入 ngrok http 5000 執行    
### 2.複製轉發網址至Line Developers的Webhook URL (https://developers.line.biz/zh-hant/)  
	轉發網址 https://  ??? .ngrok-free.app/callback  
### 3.開啟 \gui\LineBot_App.py   
	確認 Channel access token , Channel secret是否一樣  
	執行 LineBot_App.py  
### 4.執行 \gui\LogIn.py  
	Login.py
## 單純測試UI
	\gui\LogIn.py	
## 測試辨識模型
	test_model.py
