import os
import pandas as pd
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk, messagebox

from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.font_manager import FontProperties

from function import globalfunction
from runpy import run_path

# 全局字型設置
FONT_PROP = FontProperties(fname=r"C:\Windows\Fonts\mingliu.ttc", size=14)

# 火災時間統計
def show_fire_time_statistics():
    db = globalfunction.connect_to_database()
    cursor = db.cursor()
    cursor.execute("SELECT StartTime FROM missions")
    rows = cursor.fetchall()
    db.close()

    df = pd.DataFrame(rows, columns=['StartTime'])
    df['StartTime'] = pd.to_datetime(df['StartTime'])
    df['Hour'] = df['StartTime'].dt.hour
    df['Month'] = df['StartTime'].dt.month

    hourly_counts = df['Hour'].value_counts().reindex(range(0, 24), fill_value=0).sort_index()
    monthly_counts = df['Month'].value_counts().reindex(range(1, 13), fill_value=0).sort_index()

    fire_time_window = tk.Toplevel()
    fire_time_window.title("火災時間統計")
    fire_time_window.geometry("1200x500")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    hourly_counts.plot(kind='bar', ax=ax1, color='orange', width=0.8)
    ax1.set_title('每小時火災發生次數', fontproperties=FONT_PROP)
    ax1.set_xlabel('小時', fontproperties=FONT_PROP)
    ax1.set_ylabel('發生次數', fontproperties=FONT_PROP)
    ax1.set_xticks(range(0, 24))
    ax1.set_xticklabels([f'{i}' for i in range(1, 25)], fontproperties=FONT_PROP, rotation=0)

    monthly_counts.plot(kind='bar', ax=ax2, color='blue', width=0.8)
    ax2.set_title('每月火災發生次數', fontproperties=FONT_PROP)
    ax2.set_xlabel('月份', fontproperties=FONT_PROP)
    ax2.set_ylabel('發生次數', fontproperties=FONT_PROP)
    ax2.set_xticks(range(0, 12))
    ax2.set_xticklabels([f'{i}月' for i in range(1, 13)], fontproperties=FONT_PROP, rotation=0)

    canvas = FigureCanvasTkAgg(fig, master=fire_time_window)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    fire_time_window.mainloop()

# 成功率顯示
def show_success_rate():
    db = globalfunction.connect_to_database()
    df = pd.read_sql("SELECT AVG(success) AS success_rate FROM missions", db)
    db.close()

    success_rate = df.loc[0, 'success_rate'] * 100  # 轉換成百分比形式

    rate_window = tk.Toplevel()
    rate_window.title("成功率")
    rate_window.geometry("300x100")
    success_label = tk.Label(rate_window, text=f"救災成功率: {success_rate:.2f}%", font=('Helvetica', 20))
    success_label.pack(pady=20)

    rate_window.mainloop()

# 無人機使用時數顯示
def show_drone_usage():
    db = globalfunction.connect_to_database()
    drone_df = pd.read_sql("SELECT DroneID, Model FROM drones", db)
    usage_df = pd.read_sql("SELECT DroneID, SUM(TIMESTAMPDIFF(MINUTE, StartTime, EndTime)) AS TotalMinutes, COUNT(*) AS TotalFlights FROM missions GROUP BY DroneID", db)
    db.close()

    result_df = pd.merge(drone_df, usage_df, on="DroneID", how="left")
    result_df['TotalMinutes'] = result_df['TotalMinutes'].fillna(0)
    result_df['TotalFlights'] = result_df['TotalFlights'].fillna(0)

    usage_window = tk.Toplevel()
    usage_window.title("無人機使用時數")
    usage_window.geometry("550x200")

    # 定義字體
    headingFont = tkfont.Font(family="Helvetica", size=14)  # 較大的字體用於標題

    # 定義樣式
    style = ttk.Style()
    style.configure("Treeview", font=('Helvetica', 12), rowheight=35)
    style.configure("Treeview.Heading", font=headingFont, anchor='center', background='lightgrey')


    tree = ttk.Treeview(usage_window, columns=["DroneID", "Model", "TotalMinutes", "TotalFlights"], show="headings")
    tree.pack(expand=True, fill=tk.BOTH)

    # 設定每列的標題、對齊方式
    tree.heading("DroneID", text="無人機ID", anchor="center")
    tree.heading("Model", text="型號", anchor="center")
    tree.heading("TotalMinutes", text="總時數（分鐘）", anchor="center")
    tree.heading("TotalFlights", text="總飛行架次", anchor="center")

    # 為每一列設定寬度和對齊方式
    tree.column("DroneID", width=100, anchor="center")
    tree.column("Model", width=150, anchor="center")
    tree.column("TotalMinutes", width=150, anchor="center")
    tree.column("TotalFlights", width=150, anchor="center")

    for index, row in result_df.iterrows():
        tree.insert("", tk.END, values=(row['DroneID'], row['Model'], row['TotalMinutes'], row['TotalFlights']))

    usage_window.mainloop()


# 救災時間統計顯示
def show_rescue_time_statistics():
    db = globalfunction.connect_to_database()
    df = pd.read_sql("SELECT StartTime, EndTime, TIMESTAMPDIFF(MINUTE, StartTime, EndTime) AS Duration FROM missions ORDER BY StartTime DESC", db)
    db.close()

    time_window = tk.Toplevel()
    time_window.title("救災時間統計")
    time_window.geometry("600x400")

    # 定義字體和樣式
    headingFont = tkfont.Font(family="Helvetica", size=14)
    contentFont = tkfont.Font(family="Helvetica", size=12)

    style = ttk.Style()
    style.configure("Treeview", font=contentFont, rowheight=35)
    style.configure("Treeview.Heading", font=headingFont, anchor='center', background='lightgrey')
    style.map("Treeview", background=[('selected', 'blue')])
    style.map("Treeview.Heading", background=[('active', 'lightgrey')])

    tree = ttk.Treeview(time_window, columns=["StartTime", "EndTime", "Duration"], show="headings")
    tree.pack(fill='both', expand=True)
    tree.heading("StartTime", text="開始時間", anchor="center")
    tree.heading("EndTime", text="結束時間", anchor="center")
    tree.heading("Duration", text="花費時間 (分鐘)", anchor="center")

    # 設定列寬度和對齊方式
    tree.column("StartTime", width=200, anchor="center")
    tree.column("EndTime", width=200, anchor="center")
    tree.column("Duration", width=150, anchor="center")

    for index, row in df.iterrows():
        tree.insert("", tk.END, values=(row['StartTime'], row['EndTime'], row['Duration']))

    avg_time = df['Duration'].mean()
    avg_label = tk.Label(time_window, text=f"平均花費時間: {avg_time:.2f} 分鐘", font=('Helvetica', 20))
    avg_label.pack()

    time_window.mainloop()

# 高度統計顯示
def show_height_statistics():
    db = globalfunction.connect_to_database()
    df = pd.read_sql("SELECT MaxHeight, MinHeight FROM missions ORDER BY StartTime DESC LIMIT 10", db)
    db.close()

    df['HeightDifference'] = df['MaxHeight'] - df['MinHeight']  # 計算最大高度與最低高度之間的差

    height_window = tk.Toplevel()
    height_window.title("高度統計")
    height_window.geometry("600x500")

    fig, ax = plt.subplots()

    # 繪製堆疊的長條圖，使用柔和的顏色
    indices = range(len(df))
    ax.bar(indices, df['MinHeight'], label='每次最低高度', color='#add8e6')  # 淺藍色
    ax.bar(indices, df['HeightDifference'], bottom=df['MinHeight'], label='高度差（到最大高度）', color='#90ee90')  # 淺綠色

    ax.set_xlabel('任務序號', fontproperties=FONT_PROP)
    ax.set_ylabel('高度 (公尺)', fontproperties=FONT_PROP)
    ax.set_title('最新十次任務的高度統計', fontproperties=FONT_PROP)
    ax.legend(prop=FONT_PROP)

    canvas = FigureCanvasTkAgg(fig, master=height_window)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    height_window.mainloop()


# 返回主頁面函數
def back_to_homepage(window):
    try:
        window.destroy()
        print("返回主頁面")
    except Exception as e:
        print(f"錯誤發生: {e}")
