import os
import sys
import warnings
import platform
import subprocess
import zipfile
import requests
import json
import re
import time
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from rapidfuzz import fuzz

# Suppress TensorFlow and general warnings
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
warnings.filterwarnings("ignore")

driver = None  # Global driver reference

# ---------------------- DRIVER SETUP ----------------------

def get_chrome_version():
    system = platform.system()

    if system == "Windows":
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Google\Chrome\BLBeacon") as key:
                version, _ = winreg.QueryValueEx(key, "version")
                return version
        except:
            pass
        try:
            version = subprocess.getoutput('"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" --version')
            return version.replace("Google Chrome ", "").strip()
        except:
            pass
    elif system == "Darwin":
        try:
            out = subprocess.getoutput('/Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --version')
            return out.replace("Google Chrome ", "").strip()
        except:
            pass
    elif system == "Linux":
        try:
            out = subprocess.getoutput("google-chrome --version")
            return out.replace("Google Chrome ", "").strip()
        except:
            pass

    raise RuntimeError("❌ Unable to detect Chrome version.")

def download_and_extract_chromedriver(version=None, dest_dir="drivers"):
    if version is None:
        version = get_chrome_version()

    system = platform.system()
    arch_map = {
        "Windows": "win64",
        "Darwin": "mac-arm64" if platform.machine() == "arm64" else "mac-x64",
        "Linux": "linux64"
    }
    arch = arch_map.get(system)
    if not arch:
        raise RuntimeError(f"Unsupported OS: {system}")

    chromedriver_path = os.path.join(dest_dir, version, "chromedriver.exe" if system == "Windows" else "chromedriver")
    if os.path.exists(chromedriver_path):
        return chromedriver_path

    print(f"⬇️ Downloading ChromeDriver for Chrome v{version} on {arch}...")

    url = f"https://storage.googleapis.com/chrome-for-testing-public/{version}/{arch}/chromedriver-{arch}.zip"
    os.makedirs(os.path.join(dest_dir, version), exist_ok=True)
    zip_path = os.path.join(dest_dir, "chromedriver.zip")

    try:
        r = requests.get(url)
        r.raise_for_status()
    except Exception as e:
        raise RuntimeError(f"❌ Failed to download ChromeDriver: {e}")

    with open(zip_path, "wb") as f:
        f.write(r.content)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(os.path.join(dest_dir, version))

    os.remove(zip_path)

    extracted_path = os.path.join(dest_dir, version, f"chromedriver-{arch}", "chromedriver.exe" if system == "Windows" else "chromedriver")
    if not os.path.exists(extracted_path):
        raise FileNotFoundError("❌ Extracted ChromeDriver not found.")
    return extracted_path

# ---------------------- SELENIUM SESSION ----------------------

def create_headless_driver_with_cookies(cookies):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")

    service = Service(download_and_extract_chromedriver())
    service.creationflags = 0x08000000 if platform.system() == "Windows" else 0
    service.log_file = open(os.devnull, "w")

    driver = webdriver.Chrome(service=service, options=options)
    driver.get("https://www.linkedin.com")
    for cookie in cookies:
        if cookie.get('sameSite') == 'None':
            cookie['sameSite'] = 'Strict'
        try:
            driver.add_cookie(cookie)
        except:
            pass
    driver.get("https://www.linkedin.com/my-items/saved-posts/")
    return driver

def wait_for_user_login():
    global driver
    print("🚀 Opening LinkedIn login page...")

    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")

    service = Service(download_and_extract_chromedriver())
    service.creationflags = 0x08000000 if platform.system() == "Windows" else 0
    service.log_file = open(os.devnull, "w")

    driver = webdriver.Chrome(service=service, options=options)
    driver.get("https://www.linkedin.com/login")

    print("🔐 Please log in manually in the Chrome window.")
    input("⏳ After logging in successfully, press Enter here to continue...")
    return driver.get_cookies()

# ---------------------- POST HANDLING ----------------------

def convert_relative_time_to_timestamp(relative_time_str):
    now = datetime.now()
    match = re.search(r"\d+", relative_time_str)
    if not match:
        return now.strftime("%Y-%m-%d")
    amount = int(match.group())
    if "h" in relative_time_str:
        return (now - timedelta(hours=amount)).strftime("%Y-%m-%d")
    elif "d" in relative_time_str:
        return (now - timedelta(days=amount)).strftime("%Y-%m-%d")
    elif "w" in relative_time_str:
        return (now - timedelta(weeks=amount)).strftime("%Y-%m-%d")
    elif "mo" in relative_time_str:
        return (now - timedelta(days=30 * amount)).strftime("%Y-%m-%d")
    elif "y" in relative_time_str:
        return (now - timedelta(days=365 * amount)).strftime("%Y-%m-%d")
    return now.strftime("%Y-%m-%d")

def extract_original_author_from_time_tag(text):
    match = re.search(r"reposted from\s+(.*?)\s+[\u2022\u00B7\.]", text, re.IGNORECASE)
    return match.group(1).strip() if match else ""

def fuzzy_match(text, keyword, threshold=70):
    return fuzz.partial_ratio(text.lower(), keyword.lower()) >= threshold

# ---------------------- SCRAPING & SEARCH ----------------------

# (You can now insert your `search_saved_posts()` and `fetch_saved_posts()` logic here exactly as it exists in your working script.)

# ---------------------- ENTRY POINT ----------------------

def main():
    global driver
    print("Select mode:")
    print("1 - Scrape and save posts")
    print("2 - Search previously saved posts")
    main_mode = input("Enter 1 or 2: ").strip()

    if main_mode == "1":
        cookies = wait_for_user_login()
        use_headless = input("\n🕵️ Continue scraping in headless mode? (y/n): ").strip().lower() == "y"
        if use_headless:
            driver.quit()
            driver = create_headless_driver_with_cookies(cookies)
        fetch_saved_posts()
        if driver:
            driver.quit()
    elif main_mode == "2":
        search_saved_posts()
    else:
        print("❌ Invalid mode. Exiting.")
