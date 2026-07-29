# -*- coding: utf-8 -*-
"""PRD UT Tee Time Email.ipynb
"""

# ALL INPUTS HERE
# --- EMAIL CONFIGURATION ---
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
# WARNING: Ensure you are using a 16-character 'App Password', not your main account password.
SENDER_EMAIL = "" #Account sending automated email
SENDER_PASSWORD = "" #App password for sender email account
RECIPIENT_EMAIL = "" #The player/booking owner email (sender and recipient emails can be the same)

from datetime import datetime, timedelta
import pytz
import sys

today = datetime.now()


print("It's Sunday, 6:00 PM UTC and Noon MST. Continuing script execution.")
# --- End of script start time check ---


# Find days until the upcoming Friday (Friday is 4 in 0-6 index)
days_until_friday = (4 - today.weekday()) % 7
if days_until_friday == 0: days_until_friday = 7

# Calculate Friday after next
friday_after_next = today + timedelta(days=days_until_friday + 7)
day = friday_after_next.day

# Calculate ordinal suffix
if 11 <= day <= 13:
    suffix = "th"
else:
    suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")

formatted_date = f"{day}{suffix}"
print(f"Friday after next is the {formatted_date}.")
print(f"Full target date: {friday_after_next.strftime('%A, %B')} {formatted_date}")

import smtplib
import schedule
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- EMAIL CONFIGURATION ---
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
# WARNING: Ensure you are using a 16-character 'App Password', not your main account password.
SENDER_EMAIL = "jfrolfes@gmail.com"
SENDER_PASSWORD = "fpcz jedj pukc eujb"
RECIPIENT_EMAIL = "j.giraffe98@gmail.com" #banas.kevin.j@gmail.com" #change to keb's email

def send_tee_time_inquiry():
    """Crafts and sends the weekly golf preference email."""
    print(f"[{datetime.now()}] Attempting to send weekly inquiry email...")

    subject = f"Friday Golf Planning: Selection for the {formatted_date}"
    body = f"""
    Hey,

    It's time to choose a tee time for Friday, the {formatted_date}.
    The bot is ready to process your request. If you don't reply to this email by Monday 6:50 PM, the bot won't book you anything.

    Please reply with your preferred golf course and time. Your reply must be formatted as:

    Golf Course, Time (no more, no less)

    e.g.

    Soldier Hollow Silver, 11:00 AM

    The script will match on course first and try to book the closest 4-man tee time to your preferred time.
    If there are no 4-man openings +/-30 min from the time and course you want, it will book the nearest time at one of the other courses (not Palisade).

    Your options for courses are:

    Wasatch Mountain
    Wasatch Lake
    Soldier Hollow Silver
    Soldier Hollow Gold
    Palisade

    Any time will work as long as it's 00:00 AM/PM format.
    Spelling and spacing are important, remember the comma before the time.

    You can send another reply at any point up to 6:50 PM Monday to update preferences.

    -Jawno's Bot
    """

    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECIPIENT_EMAIL
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Using SMTP_SSL for port 465
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        print("SUCCESS: Weekly inquiry email sent.")
    except Exception as e:
        print(f"FAILURE: Could not send email. Error: {e}")
        print("Note: If using Gmail, verify that 'App Passwords' are enabled and the code is correct.")


send_tee_time_inquiry() # uncomment for live runs:
#time.sleep(111300)
