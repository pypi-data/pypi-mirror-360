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

def search_saved_posts():

    try:
        with open("saved_posts.json", "r", encoding="utf-8") as f:
            posts = json.load(f)
            if not posts:
                print("❌ No saved posts found in the file. Please scrape first.")
                return
    except FileNotFoundError:
        print("❌ No saved posts found. Please run scraping first.")
        return

    print("\n🔎 Enter keywords one by one. Type '0' when done.")
    keywords = []
    while True:
        kw = input("Keyword: ").strip()
        if kw == "0":
            break
        if kw:
            keywords.append(kw)

    if not keywords:
        print("⚠️ No keywords entered. Exiting search.")
        return

    print("\nChoose match type:")
    print("1 - Match ANY keyword (OR search)")
    print("2 - Match ALL keywords (AND search)")
    match_mode = input("Enter 1 or 2: ").strip()

    print("\n🗓️ Do you want to apply a date filter? (y/n): ")
    use_date_filter = input().strip().lower() == "y"

    start_date = end_date = None
    if use_date_filter:
        start_input = input("Start date (YYYY-MM-DD) or press Enter to skip: ").strip()
        end_input = input("End date (YYYY-MM-DD) or press Enter to skip: ").strip()

        try:
            if start_input:
                start_date = datetime.strptime(start_input, "%Y-%m-%d")
            if end_input:
                end_date = datetime.strptime(end_input, "%Y-%m-%d")
        except ValueError:
            print("❌ Invalid date format. Skipping date filtering.")

    # try:
    #     with open("saved_posts.json", "r", encoding="utf-8") as f:
    #         posts = json.load(f)
    # except FileNotFoundError:
    #     print("❌ No saved posts found.")
    #     return

    print("\n🔍 Searching...\n")
    matched_posts = []
    for post in posts:
        
        # content = (post.get("text", "") + " " + post.get("original_text", ""))
        content = " ".join([
            post.get("text", ""),
            post.get("original_text", ""),
            post.get("author", ""),
            post.get("original_author", "")
        ])


        if match_mode == "1":
            matched = any(fuzzy_match(content, kw) for kw in keywords)
        else:
            matched = all(fuzzy_match(content, kw) for kw in keywords)

        if not matched:
            continue

        # Time filter
        if use_date_filter:
            try:
                post_time = datetime.strptime(post["time"], "%Y-%m-%d")
                if (start_date and post_time < start_date) or (end_date and post_time > end_date):
                    continue
            except Exception:
                pass  # In case post["time"] is malformed

        matched_posts.append(post)

    # if not matched_posts:
    #     print("❌ No matching posts found.")
    # else:
    #     print(f"✅ Found {len(matched_posts)} matching post(s):\n")
    #     for i, post in enumerate(matched_posts, 1):
    #         print(f"{i}. {post['time']} | {post['author']} — {post['url']}")
    if not matched_posts:
        print("❌ No matching posts found.")
        return

    print(f"✅ Found {len(matched_posts)} matching post(s):\n")
    for i, post in enumerate(matched_posts, 1):
        print(f"{i}. {post['time']} | {post['author']} — {post['url']}")

    # ✅ Ask if user wants to export
    export_choice = input("\n💾 Do you want to export these results to a file? (y/n): ").strip().lower()
    if export_choice == "y":
        export_filename = input("📁 Enter filename (e.g., matched_results.json): ").strip()
        if not export_filename.endswith(".json"):
            export_filename += ".json"
        with open(export_filename, "w", encoding="utf-8") as f:
            json.dump(matched_posts, f, indent=2, ensure_ascii=False)
        print(f"✅ Results exported to '{export_filename}'")


def fetch_saved_posts():
    start_time = time.time()

    SAVED_POSTS_URL = "https://www.linkedin.com/my-items/saved-posts/"
    driver.get(SAVED_POSTS_URL)

    try:
        with open("saved_urls.json", "r", encoding="utf-8") as f:
            previously_saved_urls = set(json.load(f))
    except FileNotFoundError:
        previously_saved_urls = set()

    try:
        with open("saved_posts.json", "r", encoding="utf-8") as f:
            all_posts = json.load(f)
    except FileNotFoundError:
        all_posts = []

    print("\nChoose scraping mode:")
    print("1 - Scroll-based (default)")
    print("2 - Cutoff date (stop after threshold of old posts)")
    mode = input("Enter 1 or 2: ").strip()

    cutoff_date = None
    max_old_hits = 5
    scroll_count = 10
    if mode == "2":
        while True:
            user_input = input("📅 Enter cutoff date (YYYY-MM-DD): ").strip()
            try:
                cutoff_date = datetime.strptime(user_input, "%Y-%m-%d")
                break
            except ValueError:
                print("❌ Invalid format. Please try again.")
        max_old_hits = int(input("🔁 How many old posts to tolerate before stopping? (default: 5): ") or "5")
    else:
        scroll_count = int(input("🔁 How many times should we scroll to load your saved posts? (e.g., 10): "))

    new_urls = set()
    new_posts = []
    skipped_from_current_run = 0
    skipped_from_previous_runs = 0

    print("\n📥 Loading saved posts...")

    old_hit_count = 0
    scrolls_done = 0

    max_cutoff_scrolls = 300  # Prevent infinite scroll loops for very old cutoff dates

    while (mode == "1" and scrolls_done < scroll_count) or (mode == "2" and old_hit_count <= max_old_hits):
        # driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # time.sleep(2)
        # scrolls_done += 1
        # print(f"🔄 Scroll {scrolls_done}")

        #debug
        # 🧠 Track how many <li> were already on the page
        previous_soup = BeautifulSoup(driver.page_source, "html.parser")
        previous_li_count = len(previous_soup.find_all("li"))

        # 🔽 Scroll to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # ⏳ Wait until more <li> elements are detected
        try:
            WebDriverWait(driver, 10).until(
                lambda d: len(BeautifulSoup(d.page_source, "html.parser").find_all("li")) > previous_li_count
            )
        except:
            print("⏳ Timeout waiting for new content to load (no new <li> detected).")

        # ✅ Continue tracking scrolls
        scrolls_done += 1
        print(f"🔄 Scroll {scrolls_done}")
        ###########################################################

        soup = BeautifulSoup(driver.page_source, "html.parser")

        #debug
        li_count = len(soup.find_all("li"))
        print(f"🧩 Parsed {li_count} <li> elements after scroll {scrolls_done}")


        see_more_buttons = driver.find_elements(By.XPATH, "//span[contains(., '...see more') or contains(., 'See more')]")
        for btn in see_more_buttons:
            try:
                driver.execute_script("arguments[0].click();", btn)
                time.sleep(0.2)
            except:
                pass

        found_any = False

        for li in soup.find_all("li"):
            link_tag = li.select_one("a[href*='/feed/update']")
            if not link_tag:
                continue

            url = link_tag["href"]

            #debug
            print(f"🔗 Found potential post: {url}")

            if url in new_urls:
                print("↪️ Already found in current run, skipping.")
                skipped_from_current_run += 1
                continue

            elif url in previously_saved_urls:
                print("↪️ Already found in previous runs, skipping.")
                skipped_from_previous_runs += 1
                continue


            new_urls.add(url)
            found_any = True

            author = "(unknown)"
            author_span = li.select_one("a[href*='/in/'] span[aria-hidden='true']")
            if author_span:
                author = author_span.get_text(strip=True)
            else:
                page_span = li.select_one("a[href*='/company/'] span[aria-hidden='true']")
                if page_span:
                    author = page_span.get_text(strip=True)

            cursor_pointer_divs = li.find_all("div", class_="cursor-pointer")
            role = cursor_pointer_divs[0].get_text(strip=True) if cursor_pointer_divs else ""
            post_text = cursor_pointer_divs[1].get_text(separator="\n", strip=True) if len(cursor_pointer_divs) > 1 else ""
            for suffix in ["…see more", "See more"]:
                if post_text.endswith(suffix):
                    post_text = post_text[: -len(suffix)].rstrip()

            relative_time = ""
            original_author = ""
            time_tag = li.select_one("p.t-black--light.t-12 span[aria-hidden='true']")
            if time_tag:
                raw_text = time_tag.get_text(strip=True)
                match = re.search(r"(\d+\s*(?:h|d|w|mo|y|yr|yrs))\b", raw_text)
                if match:
                    relative_time = match.group(1).replace(" ", "")
                    relative_time = re.sub(r"yrs?$", "y", relative_time)
                original_author = extract_original_author_from_time_tag(raw_text)

            post_time_str = convert_relative_time_to_timestamp(relative_time)
            post_time = datetime.strptime(post_time_str, "%Y-%m-%d")

            if cutoff_date and post_time < cutoff_date:
                old_hit_count += 1
                print(f"⚠️ {old_hit_count}/{max_old_hits} old post(s) seen — {post_time_str} < cutoff")
                if old_hit_count > max_old_hits:
                    print("🛑 Reached max old post threshold. Stopping.")
                    break
            else:
                old_hit_count = 0
                
            needs_original = not post_text or len(post_text.split()) < 10
            original_text = ""

            if needs_original:
                print(f"↪️ Visiting original post for deeper content: {author}")
                original_window = driver.current_window_handle
                driver.execute_script("window.open('');")
                driver.switch_to.window(driver.window_handles[-1])
                driver.get(url)

                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "update-components-actor__title"))
                    )
                except:
                    print("⚠️ Timeout waiting for original content.")

                try:
                    see_more = driver.find_element(By.XPATH, "//span[contains(., '...see more') or contains(., 'See more')]")
                    driver.execute_script("arguments[0].click();", see_more)
                    time.sleep(0.3)
                except:
                    pass

                ref_soup = BeautifulSoup(driver.page_source, "html.parser")
                text_div = ref_soup.select_one("div.update-components-text.relative.update-components-update-v2__commentary")
                original_text = text_div.get_text(separator="\n", strip=True) if text_div else ""

                driver.close()
                driver.switch_to.window(original_window)

            new_posts.append({
                "author": author,
                "role": role,
                "text": post_text,
                "original_text": original_text,
                "original_author": original_author,
                "relative_time": relative_time,
                "time": post_time_str,
                "url": url
            })

            print(f"✅ {author} — {role[:30]} — {relative_time} — {post_time_str} — {post_text[:60]}...")

        # 🔧 Fix: Stop only if in scroll mode AND found nothing new
        if mode == "1" and not found_any:
            print("⚠️ No new posts found. Ending scroll.")
            break

        # 🔧 Enhancement: max scroll safeguard in cutoff mode
        if mode == "2" and scrolls_done >= max_cutoff_scrolls:
            print("🛑 Reached max scroll limit in cutoff mode. Ending.")
            break

    all_posts.extend(new_posts)
    all_urls = previously_saved_urls.union(new_urls)

    with open("saved_posts.json", "w", encoding="utf-8") as f:
        json.dump(all_posts, f, indent=2, ensure_ascii=False)
        
    with open("saved_urls.json", "w", encoding="utf-8") as f:
        # json.dump(list(all_urls), f, indent=2)
        json.dump([post["url"] for post in all_posts], f, indent=2)


    print(f"📊 Scroll {scrolls_done} stats:")
    print(f"    🔹 New URLs this scroll: {len(new_urls)} total so far")
    print(f"    🔹 Posts added in this scroll: {len(new_posts)} total so far")
    print(f"    🔹 Skipped duplicates (current run): {skipped_from_current_run}")
    print(f"    🔹 Skipped duplicates (previous runs): {skipped_from_previous_runs}")
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
