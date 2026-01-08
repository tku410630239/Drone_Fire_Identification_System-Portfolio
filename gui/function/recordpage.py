import os
from tkinter import messagebox
from runpy import run_path

def open_usage_record(window):
    try:
        window.destroy()
        run_path('UsageRecord.py')  # Try to execute UsageRecord.py
        print("Command executed.")  # Output the success message
    except Exception as e:
        print(f"Error occurred from recordpage : {e}")  # If there is an error, print the error message

def open_maintenance_record(window):
    try:
        window.destroy()
        run_path('MaintenanceRecords.py')  # Try to execute MaintenanceRecord.py
        print("Command executed.")  # Output the success message
    except Exception as e:
        print(f"Error occurred from recordpage : {e}")  # If there is an error, print the error message

def create_report():
    try:
        os.system('python CreateReport.py')  # Try to execute CreateReport.py
        print("Report create")  # Output the success message
        messagebox.showinfo("成功", "完整報告已生成，預設位置在桌面")  # Output the success message
    except Exception as e:
        print(f"Error occurred from recordpage : {e}")
        messagebox.showerror("失敗", "生成完整報告時出現問題")  # If there is an error, print the error message

def back_to_homepage(window):
    try:
        window.destroy()
        print("redisplay homepage by recordpage")
    except Exception as e:
        print(f"Error occurred from recordpage: {e}")  # If there is an error, print the error message
