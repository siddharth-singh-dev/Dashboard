import os
import time
import requests
import logging
from datetime import datetime, timedelta

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

logging.basicConfig(
    filename='scraper.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logging.info("Scraper started")

print("Starting script...")

# ================= CONFIG ================= #

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

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
    for el in driver.find_elements(By.XPATH, "//span"):
        if el.is_displayed() and label.lower() in el.text.lower():
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


# =================  EXPORT  ================= #

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
            logging.info("Export clicked")
            export_clicked = True
            return True

    return False


def wait_for_download(timeout=60):
    start = time.time()

    while time.time() - start < timeout:
        files = os.listdir(download_path)

        if any(f.endswith(".crdownload") for f in files):
            time.sleep(1)
            continue

        if len(files) > 0:
            print("Download detected")
            return True

        time.sleep(1)

    print("Download timeout")
    return False


# ================= DISCHARGE EXPORT VIA API ================= #

def export_discharge_api():
    print("Exporting discharge via API...")

    session = requests.Session()

    # copy cookies
    for cookie in driver.get_cookies():
        session.cookies.set(cookie['name'], cookie['value'])

    url = "https://nuvertos.com/his/reports/discharge_report"

    params = {
        "from": from_date,
        "to": to_date,
        "export_data": "true",
        "visit_types": "2,3,4",
        "include_cash": "0"
    }

    response = session.get(url, params=params)

    if response.status_code == 200:
        file_path = os.path.join(download_path, f"discharge_{int(time.time())}.xlsx")

        with open(file_path, "wb") as f:
            f.write(response.content)

        print("Discharge downloaded")
    else:
        print("Discharge API failed", response.status_code)


# ================= MAIN ================= #

from datetime import datetime

def rename_latest_file(report_name):
    files = [
        f for f in os.listdir(download_path)
        if f.endswith(".xlsx") or f.endswith(".xls")
    ]

    if not files:
        print("No files found to rename")
        return

    # latest file
    latest_file = max(
        files,
        key=lambda x: os.path.getctime(os.path.join(download_path, x))
    )

    old_path = os.path.join(download_path, latest_file)

    # 🔥 CREATE ARCHIVE FOLDER
    archive_path = os.path.join(download_path, "archive")
    os.makedirs(archive_path, exist_ok=True)

    # 🔥 ADD DATE IN NAME
    date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    new_filename = f"{report_name}_{date_str}.xlsx"
    new_path = os.path.join(archive_path, new_filename)

    os.rename(old_path, new_path)

    print(f"{report_name.upper()} saved as {new_filename}")

def process_report(name):
    global export_clicked
    export_clicked = False
    logging.info(f"Processing {name} report")

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

    if name == "discharge":
        export_discharge_api()
        time.sleep(3)  # wait for file write
        rename_latest_file("discharge")
        logging.info("Discharge report downloaded and renamed")

    else:
        if safe_export():
            if wait_for_download():
                time.sleep(3)  # VERY IMPORTANT (file writing time)
                rename_latest_file(name)
                logging.info(f"{name} report downloaded and renamed")
            else:
                logging.error(f"{name} download failed")
                print(f"{name} download failed")


# ================= RUN ================= #

process_report("bill")
process_report("service")
process_report("receipt")
process_report("discharge")

print("\nALL REPORTS DONE")

input("Press Enter to close...")
driver.quit()