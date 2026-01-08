import requests

# 中介服務的 URL
url = "http://localhost:5000/fire-alert"
# 要發送的數據，假設你的中介服務需要地點信息
data = {
    "location": "淡江大學"
}

# 發送 POST 請求
response = requests.post(url, json=data)

# 打印響應
print("Status Code:", response.status_code)
print("Response Text:", response.text)
