from function import globalfunction
from tkinter import messagebox


def change_password(username, name, new_password,window):
    db = globalfunction.connect_to_database()
    cursor = db.cursor()

    # 首先验证旧密码是否正确
    query = "SELECT UserID FROM users WHERE Username = %s AND Name = %s"
    cursor.execute(query, (username, name))
    result = cursor.fetchone()  # 捕获查询结果

    if result:
        # 姓名正确，获取 UserID
        userID = result[0]  # UserID 是查询结果的第一列
        update_query = "UPDATE users SET Password = %s WHERE UserID = %s"
        cursor.execute(update_query, (new_password, userID))
        db.commit()
        messagebox.showinfo("更改密碼", "密碼更改成功")
        success = True
        window.destroy()
    else:
        # 旧密码不正确，不更新密码
        messagebox.showerror("更改密碼失敗", "使用者帳號或姓名不正确")
        success = False

    cursor.close()
    db.close()
    return success
