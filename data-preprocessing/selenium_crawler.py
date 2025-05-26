import time
import os
from collections import Counter
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, UnexpectedAlertPresentException, NoAlertPresentException
)

# --- 설정 ---
options = Options()
options.add_argument("--headless=new")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")

chromedriver_path = os.path.abspath("../sesac-study/data-preprocessing/chromedriver.exe")
service = Service(executable_path=chromedriver_path)
driver = webdriver.Chrome(service=service, options=options)

url = "https://www.r114.com/?_c=memul&_m=p10"
driver.get(url)

item_xpath = '/html/body/div[11]/div/div[5]/ul[3]'
pagination_xpath = '/html/body/div[11]/div/div[5]/div[5]'

date_counter = Counter()

# --- 유틸 함수들 ---
def handle_alert():
    try:
        alert = driver.switch_to.alert
        print("⚠️ Alert appeared:", alert.text)
        alert.accept()
    except NoAlertPresentException:
        pass

def save_page_snapshot(filename="debug_page.html"):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print(f"📝 Saved page snapshot to {filename}")

# --- 핵심 기능들 ---
def extract_items():
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, item_xpath + '/li[1]'))
        )
    except TimeoutException:
        print("❌ Timeout: Items not loaded.")
        save_page_snapshot()
        handle_alert()
        return

    items = driver.find_elements(By.XPATH, item_xpath + '/li')
    print(f"✅ Found {len(items)} items.")
    for item in items:
        try:
            date_span = item.find_element(By.CSS_SELECTOR, 'span.tag_comm3 > em')
            date = date_span.text.strip()
            print("📅 Date:", date)
            date_counter[date] += 1
        except Exception:
            print("📅 Date: Not found")

def navigate_to_next_page():
    try:
        pagination_div = driver.find_element(By.XPATH, pagination_xpath)
        elems = pagination_div.find_elements(By.XPATH, './*')

        skip_found = False
        for elem in elems:
            if not skip_found and elem.tag_name == 'strong':
                if 'skip' in elem.get_attribute("innerHTML"):
                    print("📍 현재 페이지:", elem.text.strip())
                    skip_found = True
            elif skip_found and elem.tag_name == 'a':
                print("➡️ Navigating to next page:", elem.text)
                driver.execute_script("arguments[0].click();", elem)
                return True

        print("⛔ No next page found.")
        return False

    except Exception as e:
        print("❌ Error during pagination:", e)
        save_page_snapshot()
        handle_alert()
        return False

# --- 메인 루프 ---
try:
    while True:
        extract_items()
        time.sleep(1)
        if not navigate_to_next_page():
            break
except UnexpectedAlertPresentException:
    print("🚨 Unexpected alert encountered.")
    handle_alert()
except Exception as e:
    print(f"❗ Unexpected error: {e}")
    save_page_snapshot()
finally:
    driver.quit()
    print("✅ 작업 완료, 브라우저 종료.")

# --- 결과 출력 ---
print("\n📊 날짜별 매물 수 통계:")
for date, count in sorted(date_counter.items(), reverse=True):
    print(f"{date}: {count}개")
print("📊 통계 완료.")