from function import globalfunction
import os
from runpy import run_path

def logout(window):
    try:
        window.destroy()
        globalfunction.set_login_user(None)
        print("logout")
        run_path('LogIn.py')
    except Exception as e:
        print(f"Error occurred from homepage: {e}")  # If there is an error, print the error message

def back_to_homepage(window):
    try:
        window.destroy()
        run_path('HomePage.py')
        print("redisplay homepage by logout")
    except Exception as e:
        print(f"Error occurred from logout: {e}")  # If there is an error, print the error message

def on_closing(window):
    window.destroy()
    run_path('HomePage.py')

def get_username():
    try:
        db = globalfunction.connect_to_database()
        cursor = db.cursor()
        cursor.execute("SELECT Username FROM users WHERE UserID=%s", (globalfunction.return_login_user(),))
        username = cursor.fetchone()
        cursor.close()
        db.close()
        return str(username[0])
    except Exception as e:
        print(f"Error occurred from logout get_username: {e}")

def get_name():
    try:
        db = globalfunction.connect_to_database()
        cursor = db.cursor()
        cursor.execute("SELECT Name FROM users WHERE UserID=%s", (globalfunction.return_login_user(),))
        name = cursor.fetchone()
        cursor.close()
        db.close()
        return str(name[0])
    except Exception as e:
        print(f"Error occurred from logout get_name: {e}")

def get_userID():
    try:
        userID = globalfunction.return_login_user()
        print(userID)
        return str(userID)
    except Exception as e:
        print(f"Error occurred from logout get_userID: {e}")