import tkinter as tk
from tkinter import font as tkfont
from tkinter import messagebox
from datetime import datetime
import os
import mysql.connector
from function import globalfunction

def read_drone_log():
    with open('drone_log.txt', 'r') as file:
        data = file.read().splitlines()
    return data

def save_mission(drone_id, mission_type, start_time, end_time, location, success, max_height, min_height, totalFlight):
    try:
        db = globalfunction.connect_to_database()
        if db is not None:
            cursor = db.cursor()
            try:
                success_value = 1 if success == '是' else 0
                insert_query = """
                INSERT INTO missions (DroneID, MissionType, StartTime, EndTime, MissionLocation, Success, MaxHeight, MinHeight, totalFlight)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(insert_query, (drone_id, mission_type, start_time, end_time, location, success_value, max_height, min_height, totalFlight))
                db.commit()
                messagebox.showinfo("成功", "數據已成功保存到數據庫")
            except mysql.connector.Error as err:
                messagebox.showerror("錯誤", f"數據庫錯誤: {err}")
                db.rollback()
            finally:
                cursor.close()
                db.close()
        else:
            messagebox.showerror("錯誤", "無法連接到數據庫")
    except Exception as e:
        messagebox.showerror("錯誤", f"保存任務時發生錯誤: {e}")

#確認並關閉任務窗口
def confirm_and_close(entries, window, success_var,mission_type_var):
    # 呼叫 save_mission 函數並傳入必要的參數
    save_mission(entries[0].get(),
                 mission_type_var.get(),
                 entries[2].get(),
                 entries[3].get(),
                 entries[4].get(),
                 success_var.get(),
                 entries[6].get(),
                 entries[7].get(),
                 entries[8].get())
    # 關閉 details_window
    window.destroy()


def main():
    root = tk.Tk()
    root.title("Drone Mission Details")
    root.geometry("350x420")

    drone_data = read_drone_log()
    large_font = tkfont.Font(size=12)

    labels = ["無人機:", "任務類型:", "開始時間:", "結束時間:", "地點:", "是否成功?", "最大高度(公尺):",
              "最低高度(公尺):", "架次"]
    entries = []
    success_var = tk.StringVar(value="是")  # 預設選項
    mission_type_var = tk.StringVar(value="救災")  # 預設選項

    data_map = [0, None, 1, 2, 3, None, 4, 5, 6]  # 映射 labels 到 drone_data 的索引

    for i, text in enumerate(labels):
        label = tk.Label(root, text=text, font=large_font)
        label.grid(row=i, column=0, sticky='e', padx=10, pady=5)

        if text == "是否成功?":
            entry = tk.OptionMenu(root, success_var, "是", "否")
            entry.config(font=large_font)
        elif text == "任務類型:":
            entry = tk.OptionMenu(root, mission_type_var, "救災", "保養測試")
            entry.config(font=large_font)
        else:
            entry = tk.Entry(root, font=large_font)
            index = data_map[i]  # 使用映射得到的索引
            if index is not None:
                entry.insert(0, drone_data[index])  # 只有在有有效索引時才插入數據

        entry.grid(row=i, column=1, sticky='w', padx=10, pady=5)
        entries.append(entry)

    tk.Button(root, text="確認", font=large_font,
              command=lambda: confirm_and_close(entries, root, success_var, mission_type_var)).grid(row=len(labels),
                                                                                                    column=0,
                                                                                                    columnspan=2,
                                                                                                    pady=20)
    tk.Button(root, text="不記錄此次", font=large_font, command=root.destroy).grid(row=len(labels) + 1, column=0,
                                                                                   columnspan=2, pady=10)

    root.mainloop()


if __name__ == "__main__":
    main()

