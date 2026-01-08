import os
import datetime
import mysql.connector
from function import globalfunction

# 讀取數據庫中的資料
def fetch_data(query):
    db = globalfunction.connect_to_database()
    cursor = db.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    db.close()
    return result

# 將查詢結果轉換為 HTML 表格
def generate_html_table(data, columns):
    header = "<tr>" + "".join([f"<th style='border: 1px solid black; padding: 8px; background-color: #f2f2f2;'>{col}</th>" for col in columns]) + "</tr>"
    rows = ["".join([f"<td style='border: 1px solid black; padding: 8px;'>{cell}</td>" for cell in row]) for row in data]
    rows = "<tr>" + "</tr><tr>".join(rows) + "</tr>"
    return f"<table style='border-collapse: collapse; width: 100%;'>{header}{rows}</table>"

# 生成報告
def generate_report():
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    queries = {
        "無人機信息": "SELECT * FROM drones",
        "任務記錄": "SELECT * FROM missions",
        "維護記錄": "SELECT * FROM maintenancerecords"
    }
    columns = {
        "無人機信息": ["無人機ID", "型號", "製造日期", "最大載重", "最大飛行時間", "最大飛行距離", "狀態"],
        "任務記錄": ["任務ID", "無人機ID", "任務類型", "開始時間", "結束時間", "任務地點", "是否成功", "最大高度", "最低高度", "架次"],
        "維護記錄": ["記錄ID", "無人機ID", "維護日期", "維護類型", "維護詳情", "維護費用"]
    }

    html_content = f"<h1>無人機協助消防系統分析報告 (產生日期：{current_date})</h1>"

    # 加入 Power BI 圖表的 iframe 嵌入碼
    powerbi_iframe = '<iframe title="09193pbix" width="600" height="373.5" src="https://app.powerbi.com/view?r=eyJrIjoiYTY4YTkwNDItNjc0OS00NDE1LTg4MTItMDFiNDE2OWRiZjkxIiwidCI6IjM5OTIzMmZiLTE3ZDEtNDVjYS1iZGE2LTViNTQwNDQxYmQ2MiIsImMiOjEwfQ%3D%3D" frameborder="0" allowFullScreen="true"></iframe>'
    html_content += f"<h2>救災系統分析圖表</h2>{powerbi_iframe}"

    html_content += f"<h2>基礎資料信息</h2>"
    for table_name, query in queries.items():
        button_id = f"toggle_{table_name}"
        html_content += f"<h3>{table_name} <button onclick=\"document.getElementById('{button_id}').style.display = (document.getElementById('{button_id}').style.display === 'none' ? 'block' : 'none')\">查看/關閉</button></h3>"
        data = fetch_data(query)
        html_table = generate_html_table(data, columns[table_name])
        html_content += f"<div id='{button_id}' style='display: none;'>{html_table}</div>"

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    filename = f"{desktop_path}\\分析報告_{timestamp}.html"

    # 確保桌面路徑存在
    os.makedirs(desktop_path, exist_ok=True)

    with open(filename, 'w', encoding='utf-8') as file:
        file.write(html_content)

    print(f"Report generated: {filename}")

generate_report()
