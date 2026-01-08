import datetime
import tkinter
from distutils.command.check import check
from tkinter import messagebox
from tkinter.font import Font
from runpy import run_path
import mysql
from function import globalfunction
import subprocess
import sys
import os


def open_record_page(window):
    try:
        window.destroy()  # Close the current window
        run_path('RecordPage.py')  # Try to execute RecordPage.py
        run_path('HomePage.py')  # Re-display the window
        print("Command executed.")  # Output the success message
    except Exception as e:
        print(f"Error occurred from homepage open_record_page: {e}")  # If there is an error, print the error message

def open_statistical(window):
    try:
        window.destroy()  # Close the current window
        run_path('Statistical.py')  # Try to execute Statistical.py
        run_path('HomePage.py')  # Re-display the window
        print("Command executed.")  # Output the success message
    except Exception as e:
        print(f"Error occurred from homepage open_statistical: {e}")  # If there is an error, print the error message

def open_drone_information(window):
    try:
        window.destroy()  # Close the current window
        run_path('DroneInformation.py')  # Try to execute DroneInformation.py
        run_path('HomePage.py')  # Re-display the window
        print("Command executed.")  # Output the success message
    except Exception as e:
        print(f"Error occurred from homepage open_drone_information : {e}")  # If there is an error, print the error message

def on_closing(window):
    if messagebox.askokcancel("退出", "請確認所有無人機已經完成降落，否則可能出現意外"):
        window.destroy()

def open_logout(window):
    try:
        window.destroy() # 关闭当前窗口
        run_path('Logout.py')  # 尝试执行 Logout.py
        print("Command executed.")  # 输出成功信息
    except Exception as e:
        print(f"Error occurred from homepage open_logout: {e}")  # 如果有错误，输出错误信息


def start_drone(window):
    try:
        window.destroy() # 关闭当前窗口
        try:
            run_path('LineBot_Test_request.py')
        except Exception as e:
            print(f"Error occurred from homepage start_drone: {e}")

        try:
            # 獲得當前腳本所在的目錄
            base_path = os.path.dirname(__file__)

            # 構建相對路徑到 drone_run.py
            script_path = os.path.join(base_path, "..", "drone_run.py")
            # 執行 drone_run.py 腳本
            subprocess.run([sys.executable, script_path], check=True)

            # 構建相對路徑到 SaveMission.py
            script_path = os.path.join(base_path, "..", "SaveMission.py")
            # 執行 SaveMission.py 腳本
            subprocess.run([sys.executable, script_path], check=True)

        except Exception as e:
            print(f"An error occurred: {e}")

        print("Command executed.")  # 输出成功信息
    except Exception as e:
        print(f"Error occurred from homepage start_drone: {e}")  # 如果有错误，输出错误信息
    finally:
        run_path('HomePage.py')  # 重新顯示主頁






