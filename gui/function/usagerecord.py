from function import globalfunction
from tkinter import simpledialog, messagebox
from runpy import run_path
import subprocess
import sys
import os

def on_closing(window):
    window.destroy()
    run_path('RecordPage.py')

def insert():
    messagebox.showinfo("注意", "此新增任務記錄是上次操作無人機之記錄檔")
    # 儲存結果程式
    try:
        # 獲得當前腳本所在的目錄
        base_path = os.path.dirname(__file__)

        # 構建相對路徑到 SaveMission.py
        script_path = os.path.join(base_path, "..", "SaveMission.py")
        # 執行 SaveMission.py 腳本
        subprocess.run([sys.executable, script_path], check=True)
    except Exception as e:
        print(f"Error occurred from homepage start_drone: {e}")


def delete(window):
    user_input = simpledialog.askstring("輸入要刪除的任務ID", "請輸入任務ID：", parent=window)
    if user_input:
        try:
            db = globalfunction.connect_to_database()  # 連接到數據庫
            cursor = db.cursor()  # 創建一個游標對象
            # 首先檢查該任務 ID 是否存在
            query_check = "SELECT * FROM missions WHERE MissionID = %s"
            cursor.execute(query_check, (user_input,))
            result = cursor.fetchone()
            if result:
                # 如果存在，執行刪除操作
                query_delete = "DELETE FROM missions WHERE MissionID = %s"
                cursor.execute(query_delete, (user_input,))
                db.commit()  # 提交更改
                messagebox.showinfo("刪除成功", "任務 ID 為 {} 的記錄已被刪除。".format(user_input))
                window.destroy()
                run_path('UsageRecord.py')
                print("任務 ID 為 {} 的記錄已被刪除。".format(user_input))
            else:
                # 如果任務 ID 不存在
                messagebox.showinfo("未找到任務", "未找到任務 ID 為 {} 的記錄。".format(user_input))
                window.destroy()
                run_path('UsageRecord.py')
                print("未找到任務 ID 為 {} 的記錄。".format(user_input))
        except mysql.connector.Error as e:
            print("數據庫操作失敗：", e)
        finally:
            cursor.close()
            db.close()
    else:
        print("用戶沒有輸入任何內容")


def back_to_recordpage(window):
    try:
        window.destroy()
        run_path('RecordPage.py')
        print("redisplay homepage by usage record")
    except Exception as e:
        print(f"Error occurred from usage record: {e}")  # If there is an error, print the error message

def get_table_value():
    db=globalfunction.connect_to_database()  # 连接到数据库
    cursor = db.cursor()  # 创建一个游标对象
    query = "SELECT * FROM missions"  # 定义 SQL 查询
    cursor.execute(query)  # 执行查询
    rows = cursor.fetchall()  # 获取所有结果
    cursor.close()  # 关闭游标
    db.close()  # 关闭到数据库的连接
    return rows  # 返回查询结果

def get_column_names():
    return ["任務ID", "無人機ID", "任務類型", "開始時間", "結束時間", "任務地點","是否成功(1:成功，0:失敗)", "最大高度(公尺)", "最低高度(公尺)","架次"]