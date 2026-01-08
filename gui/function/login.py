import os
from function import globalfunction
from tkinter import messagebox
from runpy import run_path



def open_forget_password(window):
    try:
        window.destroy()  # 關閉當前視窗
        run_path('ForgetPassword.py')  # 嘗試執行ForgetPassword.py
        run_path('LogIn.py')  # 重新顯示視窗
        print("Command executed.")  # 輸出執行成功的訊息
    except Exception as e:
        print(f"Error occurred: {e}")  # 如果有錯誤，打印錯誤訊息


def open_create_account(window):
    try:
        window.destroy()  # 關閉當前視窗
        run_path('CreateAccount.py')  # 嘗試執行ForgetPassword.py
        run_path('LogIn.py')  # 重新顯示視窗
        print("Command executed.")  # 輸出執行成功的訊息
    except Exception as e:
        print(f"Error occurred: {e}")  # 如果有錯誤，打印錯誤訊息


def open_home_page(window, username, password):
    try:
        #判斷輸入的帳號密碼是否正確
        if globalfunction.connect_to_database():
            if login(username, password):
                print("登入成功")
                window.destroy()  # 關閉當前視窗
                run_path('HomePage.py')  # 執行HomePage.py
    except Exception as e:
        print(f"Error occurred: {e}")  # 如果有錯誤，打印錯誤訊息


# 登录函数
def login(username, password):
    db = globalfunction.connect_to_database()
    cursor = db.cursor()
    query = "SELECT * FROM users WHERE Username=%s AND Password=%s"
    cursor.execute(query, (username, password))
    result = cursor.fetchone()
    if result:
        # 查詢用戶ID
        cursor.execute("SELECT UserID FROM users WHERE Username=%s", (username,))
        userid = cursor.fetchone()
        if userid:
            globalfunction.set_login_user(userid[0])  # 確保只傳遞用戶ID

        # 更新最後登入時間
        update_query = "UPDATE users SET LastLoginTime = CURRENT_TIMESTAMP WHERE Username=%s"
        cursor.execute(update_query, (username,))
        db.commit()  # 確保執行更新
        return True
    else:
        messagebox.showerror("登入失敗", "帳號或密碼錯誤")
    cursor.close()
    db.close()
