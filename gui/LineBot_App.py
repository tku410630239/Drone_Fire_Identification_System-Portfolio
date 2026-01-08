from flask import Flask, request
from linebot import LineBotApi, WebhookHandler
from linebot.models import TextSendMessage
import json
import tkinter as tk
from tkinter import messagebox
from plyer import notification




app = Flask(__name__)
line_bot_api = LineBotApi('rApzYc1Cmd0ANK3+p1FKL+NpI1v0706513BsD4iUSW98wdiL0TioKe7F77lxg7iCFMgpSMpHYKh/oOsngQQH2DSeeEmcP2Zwf0qaM2AizRJgLxxj0ifXeYEx8X5yY++W++cJHZUAkkKd4AHrnOg5OAdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('e8a72dedc22eb5c151f0738717db7504')

@app.route("/fire-alert",methods=['POST'])
def home():
  try:
    # 網址被執行時，等同使用 GET 方法發送 request，觸發 LINE Message API 的 push_message 方法
    data = request.json  # 假設火災偵測系統以 JSON 格式發送資料
    location = data.get('location')
    if location:
        message = f'緊急警報：在 {location} 發生火災！請遠離該地區方便消防人員現場救援。'
        line_bot_api.push_message('U441f6b627e96aa238b89cac22414007b', TextSendMessage(text=message))
        return '已傳送警報'
  except:
    print('error')
    return 'error'


@app.route("/callback", methods=['POST'])
def linebot():
    body = request.get_data(as_text=True)
    json_data = json.loads(body)
    print("BODY:\n" + json.dumps(json_data))
    try:
        signature = request.headers['X-Line-Signature']
        handler.handle(body, signature)
        tk = json_data['events'][0]['replyToken']         # 取得 reply token
        msg = json_data['events'][0]['message']['text']   # 取得使用者發送的訊息
        if msg == '線上報警':
            notification.notify(
                                title='火災警報',
                                message='警告，有人發生火災，請至消防局官方line訊息查看',
                                app_icon=None,  # 可以指定一個 .ico 格式的圖標路徑
                                timeout=10,  # 通知顯示時間（秒）
                                )
            messagebox.showwarning('警告','有人發生火災，請至消防局官方line訊息查看')
        else:
            #text_message = TextSendMessage(text=msg)          # 設定回傳同樣的訊息
            line_bot_api.reply_message(tk,text_message)       # 回傳訊息
            print("傳送"+ tk,text_message)
    except:
        print('error')
    return 'OK'


if __name__ == "__main__":
    app.run(debug=True)
