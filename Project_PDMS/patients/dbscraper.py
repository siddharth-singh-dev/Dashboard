# SCRAPING + CLEANING + DB_INSERTION

import os
import time
import requests
from datetime import datetime, timedelta
import pandas as pd
import mysql.connector

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

print("Starting script...")

# ================= CLEAN FUNCTION ================= #

def clean_data(df, report_type, report_date):
    # standardize column names
    df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
    .str.replace(".", "", regex=False)   
    )


    # handle numeric columns FIRST
    for col in df.columns:
        if 'amount' in col:
            df[col] = df[col].replace('[₹,]', '', regex=True)
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # fill numeric NaN with 0
    num_cols = df.select_dtypes(include=['float64', 'int64']).columns
    df[num_cols] = df[num_cols].fillna(0)

    # fill object (text) NaN with empty string
    obj_cols = df.select_dtypes(include=['object']).columns
    df[obj_cols] = df[obj_cols].fillna("")

    # handle date column
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce').dt.date

    # add metadata
    df['report_type'] = report_type
    df['report_date'] = report_date

    return df


# ================= CONFIG ================= #

EMAIL = "siddharth.kumar@vedanshmedicare.com"
PASSWORD = "Callmesiddie@123"

download_path = "/Users/siddharthkumarsingh/Desktop/Surya Hospital data/PDMS PROJECT/scraper_exports"
os.makedirs(download_path, exist_ok=True)

yesterday = datetime.now() - timedelta(days=1)
from_date = yesterday.strftime("%Y-%m-%d 00:00:00")
to_date = yesterday.strftime("%Y-%m-%d 23:59:59")

print("Backend Date:", from_date, "-", to_date)

# ================= CHROME ================= #

chrome_options = Options()
profile_path = os.path.join(os.getcwd(), "chrome_profile")
chrome_options.add_argument(f"--user-data-dir={profile_path}")

prefs = {
    "download.default_directory": download_path,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True,
    "profile.default_content_setting_values.automatic_downloads": 1
}
chrome_options.add_experimental_option("prefs", prefs)

driver = webdriver.Chrome(options=chrome_options)
driver.maximize_window()

# ================= LOGIN ================= #

driver.get("https://nuvertos.com/home/")
time.sleep(3)

def login_if_needed():
    try:
        driver.find_element(By.XPATH, "//button[contains(text(),'Login')]").click()
        time.sleep(2)

        driver.find_element(By.XPATH, "//input[@placeholder='Enter your registered email']").send_keys(EMAIL)
        driver.find_element(By.XPATH, "//input[@type='password']").send_keys(PASSWORD)

        driver.find_element(By.XPATH, "//button[contains(@class,'login-but')]").click()
        print("Login Successful")
        time.sleep(5)
    except:
        print("Already logged in")

login_if_needed()

# ================= NAVIGATION ================= #

driver.get("https://nuvertos.com/his/reports")
time.sleep(5)

# ================= HELPERS ================= #

def click_menu(label):
    for el in driver.find_elements(By.XPATH, "//span[contains(@class,'menu-title')]"):
        if label.lower() == el.text.strip().lower():
            driver.execute_script("arguments[0].click();", el)
            return
    raise Exception(f"{label} menu not found")


def set_date():
    hidden_inputs = driver.find_elements(By.XPATH, "//input[@type='hidden']")

    from_hidden = hidden_inputs[0]
    to_hidden = hidden_inputs[1]

    driver.execute_script("""
        arguments[0].value = arguments[2];
        arguments[1].value = arguments[3];

        arguments[0].dispatchEvent(new Event('input', {bubbles:true}));
        arguments[0].dispatchEvent(new Event('change', {bubbles:true}));

        arguments[1].dispatchEvent(new Event('input', {bubbles:true}));
        arguments[1].dispatchEvent(new Event('change', {bubbles:true}));
    """, from_hidden, to_hidden, from_date, to_date)

    time.sleep(2)


def click_button(name):
    for btn in driver.find_elements(By.XPATH, "//button"):
        if btn.is_displayed() and name.lower() in btn.text.lower():
            driver.execute_script("arguments[0].click();", btn)
            return True
    return False


def load_all_rows():
    last = 0

    for _ in range(15):
        rows = driver.find_elements(By.XPATH, "//table//tbody//tr")
        count = len(rows)

        if count == last:
            break

        last = count

        driver.execute_script("""
            var table = document.querySelector('table');
            if (table) table.parentElement.scrollTop = table.parentElement.scrollHeight;
        """)

        time.sleep(2)


def get_latest_file(timeout=30):
    start = time.time()

    while time.time() - start < timeout:
        files = [
            os.path.join(download_path, f)
            for f in os.listdir(download_path)
            if f.endswith(".xlsx")
        ]

        if files:
            return max(files, key=os.path.getctime)

        time.sleep(1)

    raise Exception("No .xlsx file found after waiting")

def get_amount(row):
    for col in row.index:
        if 'amount' in col:
            val = row[col]
            if pd.notna(val) and val != 0:
                return val
    return 0

def clear_download_folder():
    for f in os.listdir(download_path):
        os.remove(os.path.join(download_path, f))



def insert_bill(df):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="callmesiddie@123",
        database="report_dashboard"
    )
    cursor = conn.cursor()

    count = 0

    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO bill_reports 
            (report_date, uhid, patient_name, gender, bill_id, file_id,
             doctor_name, department_name, panel_name,
             service_final_amount, payment_total, settlement_amount_received, created_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            row.get('report_date'),
            str(row.get('uhid')).replace('.0',''),
            row.get('patient_name'),
            row.get('gender'),
            row.get('bill_id'),
            row.get('file_id'),
            row.get('doctor_name'),
            row.get('dept_name'),  
            row.get('panel_name'),
            float(row.get('service_final_amt') or 0),
            float(row.get('payment_total') or 0),
            float(row.get('settlement_amount_received') or 0),
            datetime.now()
        ))
        count += 1

    conn.commit()
    conn.close()

    print("Bill inserted:", count)

def insert_service(df):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="callmesiddie@123",
        database="report_dashboard"
    )
    cursor = conn.cursor()

    count = 0

    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO service_reports 
            (report_date, uhid, patient_name, gender, doctor_name, department_name, panel_name, service_type, created_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            row.get('report_date'),
            str(row.get('uhid')).replace('.0',''),
            row.get('patient_name'),   
            row.get('gender'),
            row.get('doctor_name'),
            row.get('dept_name'),
            row.get('panel_name'),
            row.get('service_type'),
            datetime.now()
        ))
        count += 1

    conn.commit()
    conn.close()

    print("Service inserted:", count)

def insert_receipt(df):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="callmesiddie@123",
        database="report_dashboard"
    )
    cursor = conn.cursor()

    count = 0

    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO receipt_reports 
            (report_date, uhid, patient_name, file_id, receipt_id, total_payment, created_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, (
            row.get('report_date'),
            str(row.get('uhid')).replace('.0',''),
            row.get('patient_name'),
            row.get('file_id'),   
            None,                 
            float(row.get('service_final_amt') or 0),  
            datetime.now()
        ))
        count += 1

    conn.commit()
    conn.close()

    print("Receipt inserted:", count)

# ================= EXPORT ================= #

export_clicked = False

def safe_export():
    global export_clicked

    if export_clicked:
        return False

    for btn in driver.find_elements(By.XPATH, "//button"):
        if btn.is_displayed() and "Export" in btn.text:
            driver.execute_script("arguments[0].scrollIntoView(true);", btn)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", btn)
            print("Export clicked")
            export_clicked = True
            return True

    return False


def wait_for_download(timeout=60):
    start = time.time()

    while time.time() - start < timeout:
        files = os.listdir(download_path)

        # still downloading
        if any(f.endswith(".crdownload") for f in files):
            time.sleep(1)
            continue

        # at least one file exists
        if any(f.endswith(".xlsx") for f in files):
            print("Download complete")
            return True

        time.sleep(1)

    raise Exception("Download timeout")


# ================= DISCHARGE (API TEMP) ================= #

#def export_discharge_api():
#    print("Exporting discharge via API...")

#    session = requests.Session()

#   for cookie in driver.get_cookies():
 #       session.cookies.set(cookie['name'], cookie['value'])

#    url = "https://nuvertos.com/his/reports/discharge_report"

#    params = {
#        "from": from_date,
#        "to": to_date,
 #       "export_data": "true",
 #       "visit_types": "2,3,4",
 #       "include_cash": "0"
 #   }

 #   response = session.get(url, params=params)

 #   print("Status:", response.status_code)


# ================= MAIN ================= #

def process_report(name):
   # clear_download_folder()
    global export_clicked
    export_clicked = False

    print(f"\nProcessing {name.upper()} report")

    click_menu(name)
    time.sleep(4)

    set_date()

    click_button("Search")
    time.sleep(2)
    click_button("Search")

    time.sleep(5)

    load_all_rows()

    time.sleep(2)

#    if name == "discharge":
#        export_discharge_api()
#        return

    if safe_export():
        wait_for_download()

        # CLEAN AFTER DOWNLOAD
        file_path = get_latest_file()
        df = pd.read_excel(file_path)

        df = clean_data(df, name, from_date.split(" ")[0])
        print("Columns in dataframe:")
        print(df.columns)

        print(f"{name} cleaned preview:")
        print(df.head())

        if name == "bill":
            print(df[['uhid','dept_name','service_final_amt']].head())  
            insert_bill(df)

        elif name == "service":
            print(df[['uhid','patient_name','dept_name']].head())
            insert_service(df)

        elif name == "receipt":
            print(df[['uhid','patient_name','service_final_amt']].head())
            insert_receipt(df)


# ================= RUN ================= #

process_report("bill")
process_report("service")
process_report("receipt")
# process_report("discharge")

print("\nALL REPORTS DONE")

input("Press Enter to close...")
driver.quit()