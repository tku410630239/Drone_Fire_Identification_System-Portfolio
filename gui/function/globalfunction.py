import mysql.connector
from tkinter import messagebox
from tkinter import font


login_user = 0

def set_font():
    # 設置字體大小和風格
    custom_font = font.Font(family="Helvetica", size=20)
    return custom_font

def connect_to_database():
    try:
        db_config = {
            "host": '163.13.201.83',
            "port": 3307,
            "user": "tkuim-sd",
            "password": 'Aa123456!',
            "database": "mydatabase"
        }
        return mysql.connector.connect(**db_config)
    except Exception as e:
        messagebox.showerror("數據庫連線失敗", str(e))
        return None

def set_login_user(userid):
    global login_user
    print(f"Setting login_user from {login_user} to {userid}")  # 显示更改前的值到新值
    login_user = userid  # 更新 login_user 的值
    print(login_user)  # 输出更新后的值


def return_login_user():
    global login_user
    try:
        # 尝试将login_user转换为整数
        return int(login_user)
    except (TypeError, ValueError):
        # 如果转换失败，返回一个默认的数字，例如0
        return 5




