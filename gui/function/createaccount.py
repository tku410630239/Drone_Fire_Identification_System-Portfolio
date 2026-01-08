from function import globalfunction
from tkinter import messagebox

def create_account(username, password, name, window):
    db = globalfunction.connect_to_database()
    cursor = db.cursor()
    if (check_old_username(username)):
        messagebox.showerror("Error", "使用者帳號已經存在")
    else:
        if username != "" and password != "" and name != "":
            query = "INSERT INTO users (Username, Password, name) VALUES (%s, %s, %s)"
            cursor.execute(query, (username, password, name))
            db.commit()
            cursor.close()
            messagebox.showinfo("Success", "帳號創建成功")
            window.destroy()
        else:
            messagebox.showerror("Error", "請輸入完整資料")

def check_old_username(username):
    db = globalfunction.connect_to_database()
    cursor = db.cursor()
    query = "SELECT * FROM users WHERE Username=%s"
    cursor.execute(query, (username,))
    result = cursor.fetchone()
    cursor.close()
    if result:
        return True
    return False
