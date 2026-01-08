from function import globalfunction
from tkinter import simpledialog, messagebox
from runpy import run_path
import tkinter as tk
from datetime import datetime

def get_table_value():
    db=globalfunction.connect_to_database()  # 连接到数据库
    cursor = db.cursor()  # 创建一个游标对象
    query = "SELECT * FROM drones"  # 定义 SQL 查询
    cursor.execute(query)  # 执行查询
    rows = cursor.fetchall()  # 获取所有结果
    cursor.close()  # 关闭游标
    db.close()  # 关闭到数据库的连接
    return rows  # 返回查询结果


def get_column_names():
    return ["無人機ID", "型號", "製造日期", "最大載重", "最大飛行時間", "最大飛行距離"]

def back_to_home_page(window):
    try:
        window.destroy()
        print("redisplay homepage by droneinformation")
    except Exception as e:
        print(f"Error occurred from droneinformation: {e}")  # If there is an error, print the error message


