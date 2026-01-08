from function import globalfunction
from tkinter import simpledialog, messagebox
from runpy import run_path
import tkinter as tk
from datetime import datetime

def on_closing(window):
    window.destroy()
    run_path('RecordPage.py')

def delete(window):
    user_input = simpledialog.askstring("輸入要刪除的維護紀錄ID", "請輸入維護紀錄ID：", parent=window)
    if user_input:
        try:
            db = globalfunction.connect_to_database()  # 連接到數據庫
            cursor = db.cursor()  # 創建一個游標對象
            # 首先檢查該任務 ID 是否存在
            query_check = "SELECT * FROM maintenancerecords WHERE RecordID = %s"
            cursor.execute(query_check, (user_input,))
            result = cursor.fetchone()
            if result:
                # 如果存在，執行刪除操作
                query_delete = "DELETE FROM maintenancerecords WHERE RecordID = %s"
                cursor.execute(query_delete, (user_input,))
                db.commit()  # 提交更改
                messagebox.showinfo("刪除成功", "ID 為 {} 的記錄已被刪除。".format(user_input))
                window.destroy()
                run_path('MaintenanceRecords.py')
                print("ID 為 {} 的記錄已被刪除。".format(user_input))
            else:
                # 如果任務 ID 不存在
                messagebox.showinfo("未找到", "未找到ID 為 {} 的記錄。".format(user_input))
                window.destroy()
                run_path('MaintenanceRecords.py')
                print("未找到 ID 為 {} 的記錄。".format(user_input))
        except mysql.connector.Error as e:
            print("數據庫操作失敗：", e)
        finally:
            cursor.close()
            db.close()
    else:
        print("用戶沒有輸入任何內容")

def get_table_value():
    db=globalfunction.connect_to_database()  # 连接到数据库
    cursor = db.cursor()  # 创建一个游标对象
    query = "SELECT * FROM maintenancerecords"  # 定义 SQL 查询
    cursor.execute(query)  # 执行查询
    rows = cursor.fetchall()  # 获取所有结果
    cursor.close()  # 关闭游标
    db.close()  # 关闭到数据库的连接
    return rows  # 返回查询结果

def get_column_names():
    return ["記錄ID", "無人機ID", "維護日期", "維護類型", "維護詳情", "維護費用(台幣)"]

def open_maintenance_window(window):

    maintenance_window = tk.Toplevel()
    maintenance_window.title("新增維護紀錄")
    maintenance_window.geometry("250x300")  # 增加窗口高度

    labels = ["無人機ID", "維護日期", "維護類型", "維護詳情", "維護費用"]
    entries = {}
    for i, label in enumerate(labels):
        tk.Label(maintenance_window, text=label).grid(row=i, column=0, pady=5, padx=5, sticky='w')
        if label == "維護類型":
            maintenance_type_var = tk.StringVar(maintenance_window)
            maintenance_type_var.set("保養")  # 設置預設選項
            entry = tk.OptionMenu(maintenance_window, maintenance_type_var, "保養", "維修", "升級")
        else:
            entry = tk.Entry(maintenance_window)
            if label == "維護日期":
                entry.insert(0, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        entry.grid(row=i, column=1, pady=5, padx=5, sticky='ew')
        entries[label] = entry

    button_frame = tk.Frame(maintenance_window)
    button_frame.grid(row=len(labels), column=0, columnspan=2, pady=20, padx=5, sticky='ew')
    maintenance_window.grid_columnconfigure(1, weight=1)
    maintenance_window.grid_rowconfigure(len(labels), weight=1)  # 確保按鈕行能拉伸

    save_button = tk.Button(button_frame, text="保存", command=lambda: save_maintenance_record(entries, maintenance_type_var, window))
    cancel_button = tk.Button(button_frame, text="取消", command=maintenance_window.destroy)
    save_button.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=5)
    cancel_button.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH, padx=5)

    button_frame.grid_columnconfigure(0, weight=1)


#保存維護紀錄
def save_maintenance_record(entries, maintenance_type_var, window):
    db = globalfunction.connect_to_database()
    if db:
        cursor = db.cursor()
        try:
            cursor.execute(
                "INSERT INTO maintenancerecords (DroneID, MaintenanceDate, MaintenanceType, MaintenanceDetails, MaintenanceCost) VALUES (%s, %s, %s, %s, %s)",
                (entries["無人機ID"].get(), entries["維護日期"].get(), maintenance_type_var.get(), entries["維護詳情"].get(), entries["維護費用"].get()))
            db.commit()
            messagebox.showinfo("成功", "維護紀錄已添加")
            window.destroy()
            run_path('MaintenanceRecords.py')
        except mysql.connector.Error as err:
            messagebox.showerror("錯誤", f"數據庫錯誤: {err}")
            db.rollback()
        finally:
            cursor.close()
            db.close()
    else:
        messagebox.showerror("錯誤", "無法連接到數據庫")


def back_to_recordpage(window):
    try:
        window.destroy()
        run_path('RecordPage.py')
        print("redisplay homepage by maintenance records")
    except Exception as e:
        print(f"Error occurred from maintenance records: {e}")  # If there is an error, print the error message