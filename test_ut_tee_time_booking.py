# -*- coding: utf-8 -*-
"""Automation flow for booking Utah State Park tee times."""

# --- CONFIGURATION ---
# Fill these values before running the script.
SENDER_EMAIL = ""  # Must match the sender/recipient values used by the email script.
SENDER_PASSWORD = ""
RECIPIENT_EMAIL = ""
EMAIL_USER = SENDER_EMAIL
EMAIL_PASS = SENDER_PASSWORD

# BOOKING INFORMATION
first_name = ""
last_name = ""
phone_number = ""
CC_number = ""
CC_expiration_month = ""
CC_expiration_year = ""
CC_CVV = "" #Security Code for CC
name_on_card = ""
billing_street_address = ""
zip_code = ""


import email
import imaplib
import re
import sys
from datetime import UTC, datetime, timedelta

# --- IMAP CONFIGURATION ---
IMAP_SERVER = "imap.gmail.com"

EMAIL_USER = SENDER_EMAIL
EMAIL_PASS = SENDER_PASSWORD

def fetch_latest_reply():
    print("Connecting to mailbox to check for replies...")
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_USER, EMAIL_PASS)
        mail.select("inbox")

        # Search for emails from the recipient with our specific subject
        search_query = f'(FROM "{RECIPIENT_EMAIL}" SUBJECT "Friday Golf Planning")'
        status, messages = mail.search(None, search_query)

        if status != "OK" or not messages[0]:
            print("CRITICAL: No matching reply found. Exiting script.")
            sys.exit("Script terminated: No email reply found.")

        # Get the latest message
        latest_email_id = messages[0].split()[-1]
        status, data = mail.fetch(latest_email_id, "(RFC822)")
        raw_email = data[0][1]
        msg = email.message_from_bytes(raw_email)

        # --- DATE VALIDATION LOGIC ---
        # Parse the email date
        date_str = msg.get("Date")
        email_dt = email.utils.parsedate_to_datetime(date_str)
        # Ensure we are comparing aware datetimes
        now = datetime.now(email_dt.tzinfo)

        print(f"Latest reply received on: {email_dt}")

        if now - email_dt > timedelta(days=2):
            print("CRITICAL: The most recent reply is older than 2 days.")
            print("Exiting script to avoid booking with stale data.")
            sys.exit("Script terminated: Reply too old.")

        # --- PARSING BODY ---
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode()
                    break
        else:
            body = msg.get_payload(decode=True).decode()

        pattern = r"^\s*([A-Za-z\s]+),\s*(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm))"
        match = re.search(pattern, body, re.MULTILINE)

        if match:
            course = match.group(1).strip()
            tee_time = match.group(2).strip()
            print(f"Valid recent preference found -> Course: {course}, Time: {tee_time}")
            return course, tee_time
        else:
            print("CRITICAL: Found recent email but could not parse 'Course, Time' format. Exiting.")
            sys.exit("Script terminated: Parse failure.")

    except SystemExit:
        raise
    except Exception as e:
        print(f"Error reading mail: {e}")
        sys.exit(f"Script terminated due to error: {e}")
    finally:
        try:
            mail.logout()
        except: pass

# Execute the fetch
new_course, new_time = fetch_latest_reply()

# Update global variables for subsequent Selenium cells
DESIRED_COURSE = new_course
DESIRED_TEE_TIME = new_time
print(f"SUCCESS: Variables updated. Target: {DESIRED_COURSE} at {DESIRED_TEE_TIME}.")

import os
import time
from datetime import UTC, datetime, timedelta

from IPython.display import Image, display
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def get_target_date():
    today = datetime.now(UTC)
    target_date = today + timedelta(days=10)
    return target_date

def take_step_screenshot(driver, step_name, element=None, scroll=True):
    try:
        if element and scroll:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});", element)
            time.sleep(1)
        elif not scroll:
            pass
        else:
            driver.execute_script("window.scrollTo(0, 0);")
        fname = f"step_{step_name}.png"
        driver.save_screenshot(fname)
        print(f"Screenshot after: {step_name}")
        display(Image(fname))
    except Exception as e:
        print(f"Could not take screenshot for {step_name}: {e}")

with Display(visible=False, size=(1200, 2500)) as disp:
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    # Explicitly enable browser logging
    chrome_options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})

    try:
        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, 20)

        url = 'https://stateparks.utah.gov/golf/wasatch/teetime/'
        print(f'Navigating to {url}...')
        driver.get(url)
        time.sleep(5)

        wait.until(EC.presence_of_element_located((By.TAG_NAME, 'iframe')))
        iframe = driver.find_elements(By.TAG_NAME, 'iframe')[0]
        driver.switch_to.frame(iframe)
        print('Switched to booking iframe and logging is enabled.')

    except Exception as e:
        print(f"An error occurred: {e}")

# 0. Course Selection
dropdown_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[3]/div[2]/div/div[1]/div/div/div[2]/button/span')))
driver.execute_script('arguments[0].click();', dropdown_btn)
time.sleep(1)

select_all_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[3]/div[2]/div/div[1]/div/div/div[2]/div/div[2]/div/div[1]/button[1]')))
driver.execute_script('arguments[0].click();', select_all_btn)
print('All courses selected.')
time.sleep(1)

# 1. Open Calendar
cal_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[3]/div[2]/div/div[1]/div/div/div[3]/button/span')))
driver.execute_script('arguments[0].click();', cal_btn)
time.sleep(1)

target_date = get_target_date()
target_day = str(target_date.day)
day_btn = wait.until(EC.element_to_be_clickable((By.XPATH, f"//button[text()='{target_day}' and not(contains(@class, 'muted'))]")))
driver.execute_script('arguments[0].click();', day_btn)
print(f"Selected day {target_day}.")
time.sleep(2)

driver.execute_script('arguments[0].click();', cal_btn)
print("Closed calendar.")
time.sleep(1)

# 2. Collect Data and Match UPDATE SELECTION LOGIC
container_base_xpath = '/html/body/div[3]/div[2]/div/div[2]/div/div[3]/div[2]/div'
wait.until(EC.presence_of_all_elements_located((By.XPATH, container_base_xpath)))
tee_times_list = []
containers = driver.find_elements(By.XPATH, container_base_xpath)

for index, container in enumerate(containers, start=1):
    try:
        info_text = container.get_attribute('innerText').replace('\n', ' ')
        if 'BOOK NOW' not in info_text: continue
        btn_xpath = f"{container_base_xpath}[{index}]/div/div[2]/button"
        time_parts = [p for p in info_text.split(' ') if p.strip()]
        dt_val = datetime.strptime(f"{time_parts[0]} {time_parts[1]}", "%I:%M %p")

        # First check: Must have 1-4 slots
        has_4 = any(x in info_text for x in ['1 - 4'])
        if not has_4: continue

        tee_times_list.append({
              "info": info_text,
              "time_obj": dt_val,
              "button_xpath": btn_xpath,
              "has_4_slots": True,
              "container_index": index
            })
    except:
        continue

target_dt = datetime.strptime(DESIRED_TEE_TIME, "%I:%M %p")
course_keywords = DESIRED_COURSE.lower().split()

# Logic Part A: Find closest for desired course
desired_course_options = [i for i in tee_times_list if all(kw in i['info'].lower() for kw in course_keywords)]
closest_desired = min(desired_course_options, key=lambda x: abs(x['time_obj'] - target_dt), default=None)

best_match = None

if closest_desired:
    diff = abs(closest_desired['time_obj'] - target_dt).total_seconds() / 60
    if diff <= 30:
        print(f"Found {DESIRED_COURSE} within 1 hour window.")
        best_match = closest_desired

# Logic Part B: If no desired course within 1hr, search all courses (excluding Palisade)
if not best_match:
    print(f"No {DESIRED_COURSE} found within 1hr. Searching other courses (excluding Palisade)...")
    other_options = [i for i in tee_times_list if 'palisade' not in i['info'].lower()]
    best_match = min(other_options, key=lambda x: abs(x['time_obj'] - target_dt), default=None)

if best_match:
    print(f"Selected Match: {best_match['info']}")
    best_xpath = str(best_match['button_xpath'])
    book_button = driver.find_element(By.XPATH, best_xpath)
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", book_button)
    time.sleep(1)
    final_btn = wait.until(EC.element_to_be_clickable((By.XPATH, best_xpath)))
    driver.execute_script('arguments[0].click();', final_btn)
    print("Clicked BOOK NOW.")
    time.sleep(3)
else:
    print("No valid tee times found matching the criteria.")

# Step 5: SELECT 4 GOLFERS
print("Step 5: Selecting 4 golfers...")
g_btn = None

try:
    print("Searching for golfer selection radio button...")
    # Use a data-testid selector which is more stable than absolute XPaths
    golfer_input_xpath = "//input[@data-testid='golfer-select-radio-4']"

    # Wait for the element to exist in DOM
    g_btn = wait.until(EC.presence_of_element_located((By.XPATH, golfer_input_xpath)))

    # Use JS to scroll the element's parent into view and click it
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", g_btn)
    time.sleep(1)
    driver.execute_script("arguments[0].click();", g_btn)

    print("SUCCESS: 4 Golfers selected.")

    # Proceed to Add to Cart
    cart_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'ADD TO CART')] | //button[contains(., 'Add to Cart')]")))
    driver.execute_script('arguments[0].click();', cart_btn)
    print("SUCCESS: Added to cart.")

    # Final Checkout - Hardcoded XPath as requested
    print("Waiting for slide-out cart and checkout button...")
    time.sleep(2)
    checkout_xpath = "/html/body/div[4]/div[3]/div/div[4]/div[2]/button"
    checkout_btn = wait.until(EC.element_to_be_clickable((By.XPATH, checkout_xpath)))

    driver.execute_script('arguments[0].click();', checkout_btn)
    print("SUCCESS: Clicked Check Out using hardcoded XPath.")
    time.sleep(2)

except Exception as e:
    print(f"Process failed: {e}")
    # Take a wide screenshot of the current state for debugging
    driver.save_screenshot("debug_full_state.png")
    display(Image("debug_full_state.png"))

finally:
  # Keeping the driver open for you to see the result
  if 'driver' in locals():
      print("Driver session remains active.")

try:
    print("Step 6: Filling entire form via Keyboard Navigation (ActionChains)...")
    driver.execute_script("document.body.style.zoom='50%'")

    # 1. Focus the first field (First Name)
    first_field = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[3]/div[2]/div/div[2]/div/div[1]/div/div/div[1]/div/div/div[1]/div/div/input")))
    first_field.click()

    actions = ActionChains(driver)

    # 2. Fill Contact Info
    actions.send_keys(first_name) # First Name
    actions.send_keys(Keys.TAB).send_keys(last_name) # Last Name
    actions.send_keys(Keys.TAB).send_keys(RECIPIENT_EMAIL) # Email
    actions.send_keys(Keys.TAB).send_keys(Keys.TAB).send_keys(phone_number) # Mobile

    actions.perform()

    # 3. Fill Payment Details
    actions.send_keys(Keys.TAB).send_keys(Keys.TAB).send_keys(CC_number) # Card Number

    # Exp Month Dropdown (Month 04)
    actions.send_keys(Keys.TAB).send_keys(Keys.ENTER)
    for _ in range(int(CC_expiration_month)-1): actions.send_keys(Keys.ARROW_DOWN)
    actions.send_keys(Keys.ENTER)
    actions.perform()
    # Exp Year Dropdown (Year 2028)
    actions.send_keys(Keys.TAB).send_keys(Keys.ENTER)
    for _ in range(int(CC_expiration_year)-2026): actions.send_keys(Keys.ARROW_DOWN)
    actions.send_keys(Keys.ENTER)
    actions.perform()
    # CVV and Name
    actions.send_keys(Keys.TAB).send_keys(CC_CVV) # CVV
    actions.send_keys(Keys.TAB).send_keys(name_on_card) # Name on Card
    actions.perform()
    # 4. Fill Billing Address
    actions.send_keys(Keys.TAB).send_keys(billing_street_address) # Address Line 1
    actions.send_keys(Keys.TAB).send_keys(zip_code) # Zip Code
    actions.perform()
    # Country Dropdown (United States)
    actions.send_keys(Keys.TAB).send_keys(Keys.ENTER)
    actions.send_keys("U")
    actions.send_keys(Keys.ARROW_DOWN)
    actions.send_keys(Keys.ENTER)
    actions.perform()

    print("SUCCESS: Form filling sequence complete.")
    take_step_screenshot(driver, "filled_form")

except Exception as e:
    print(f"Keyboard navigation failed: {e}")

try:
    # Specifically target the terms checkbox by its name
    print("Attempting to click the specific terms checkbox...")
    terms_checkbox = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[3]/div[2]/div/div[2]/div/div[2]/div/div[3]/label/span/input")))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", terms_checkbox)
    driver.execute_script("arguments[0].click();", terms_checkbox)

    # Scroll to and click the Final Book Button

    # Uncomment for live booking
    #book_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'COMPLETE YOUR PURCHASE')]")))
    #book_button.click()
    time.sleep(4)

    take_step_screenshot(driver, "final_booking_button_view", scroll=False)
    print("SUCCESS: Checkbox clicked and Book button in view!")
except Exception as e:
    print(f"Final step failed: {e}")
    take_step_screenshot(driver, "final_error_state", scroll=False)
finally:
  driver.quit()

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage # Import MIMEImage
from datetime import datetime
import os

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465

def send_booking_status_email(status_message: str, success: bool = True, attachment_paths: list = None):
    """Sends an email with the status of the booking process, optionally with multiple attachments."""
    print(f"[{datetime.now()}] Attempting to send booking status email...")

    subject_prefix = "SUCCESS:" if success else "FAILURE:"
    subject = f"{subject_prefix} Golf Tee Time Booking Status - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    body = f"Hello,\n\nThis is an automated notification regarding your golf tee time booking.\n\nStatus: {status_message}\n\nSmell ya,\nJawno's Golf Bot"

    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECIPIENT_EMAIL
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    if success and attachment_paths:
        for attachment_path in attachment_paths:
            try:
                if os.path.exists(attachment_path):
                    with open(attachment_path, 'rb') as fp:
                        img = MIMEImage(fp.read())
                    img.add_header('Content-Disposition', 'attachment', filename=os.path.basename(attachment_path))
                    msg.attach(img)
                    print(f"Attached screenshot: {os.path.basename(attachment_path)}")
                else:
                    print(f"Warning: Attachment file not found: {attachment_path}")
            except Exception as e:
                print(f"Could not attach screenshot {attachment_path}. Error: {e}")

    try:
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) # SMTP_SERVER and SMTP_PORT are defined in cell _rG9ittzZId7
        server.login(SENDER_EMAIL, SENDER_PASSWORD) # SENDER_EMAIL and SENDER_PASSWORD are defined in cell _rG9ittzZId7
        server.send_message(msg)
        server.quit()
        print(f"SUCCESS: Booking status email sent: {subject}")
    except Exception as e:
        print(f"FAILURE: Could not send booking status email. Error: {e}")
        print("Note: Verify 'App Passwords' for Gmail and correct email configurations.")

# Example usage (uncomment and modify as needed after your booking logic)
send_booking_status_email(f"Your tee time has been successfully booked for {best_match}.", success=True, attachment_paths=['step_final_booking_button_view.png', 'step_filled_form.png'])
