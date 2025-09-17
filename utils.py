import customtkinter as ctk
import requests
import sqlite3
from datetime import datetime, timedelta

def change_appearance_mode_event(new_appearance_mode):
    ctk.set_appearance_mode(new_appearance_mode)

def send_sms_notification(to_phone_number, message):
    print("PHONE NUMBER", to_phone_number)
    print("MESSAGE", message)
    api_key = ''  # IMPORTANT: Do not hardcode API keys in production code.
    url = 'https://api.semaphore.co/api/v4/priority'
    payload = {'apikey': api_key, 'number': to_phone_number, 'message': message}
    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print("SEND MESSAGE SUCCESS", response.json())
        else:
            print("ERROR SENDING MESSAGE", response.text, "STATUS CODE", response.status_code)
    except requests.exceptions.RequestException as req_exc:
        print("Request Exception:", req_exc)
    except Exception as e:
        print("Failed to send message", e)

def check_date():
    current_date = datetime.now()
    conn = sqlite3.connect('SQLite db/registration_form.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, end_date, contact_no FROM registration WHERE status = 'Ongoing'")
    registrations = cursor.fetchall()
    for reg_id, end_date_str, contact_no in registrations:
        if datetime.strptime(end_date_str, '%Y-%m-%d') < current_date:
            print(f"ID {reg_id} Expired")
            cursor.execute("UPDATE registration SET status=? WHERE id=?", ("Expired", reg_id))
            conn.commit()
            sms_message = "Your gym membership has expired. Renew your subscription to continue accessing D'GRIT GYM."
            send_sms_notification(contact_no, sms_message)
    conn.close()

def send_sms_for_expiration():
    current_date = datetime.now().date()
    three_days_from_now = current_date + timedelta(days=3)
    conn = sqlite3.connect('SQLite db/registration_form.db')
    cursor = conn.cursor()
    cursor.execute("SELECT end_date, contact_no FROM registration WHERE status = 'Ongoing'")
    registrations = cursor.fetchall()
    for end_date_str, contact_no in registrations:
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        if end_date == three_days_from_now:
            print(f"Contact {contact_no} expiring in 3 days.")
            sms_message = "Your gym membership will expire in 3 days. Renew your subscription to continue accessing D'GRIT GYM."
            send_sms_notification(contact_no, sms_message)
    conn.close()

def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width / 2) - (width / 2)
    y = (screen_height / 2) - (height / 2)
    window.geometry(f"{int(width)}x{int(height)}+{int(x)}+{int(y)}")