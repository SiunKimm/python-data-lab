import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

options = Options()
options.add_argument("--headless=new")
service = Service(executable_path="../sesac-study/data-preprocessing/chromedriver.exe")
driver = webdriver.Chrome(service=service, options=options)

url = "https://www.r114.com/?_c=memul&_m=p10"
driver.get(url)

xpath = '/html/body/div[11]/div/div[5]/ul[3]'
pagination_xpath = '/html/body/div[11]/div/div[5]/div[5]'

def extract_items():
    # 특정 XPath에 해당하는 요소가 로드되었다고 해서 그 안에 있는 <li> 태그들이 로드되었다고 볼 수 없다.
    # 따라서 WebDriverWait을 사용하여 <li> 태그가 로드될 때까지 기다린다.
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, xpath + '/li[1]'))
    )
    while True:
        items_ul = driver.find_element(By.XPATH, xpath)
        items = items_ul.find_elements(By.TAG_NAME, "li")
        if items:
            break
        # 개발 초기 <ul> 기준으로 WebDriverWait을 사용하면 내부 <li>가 로드되지 않아 items가 빈 리스트로 반환된다.
        # 따라서 items가 비어있으면 계속해서 기다린다.
        print("Waiting for items to load even though WebDriverWait...")
        time.sleep(0.2)
    print("Items:", len(items))
    for item in items:
        # Date만 추출하여 print하고 있는데, 필요한 정보를 추가로 추출할 수 있다.
        try:
            date_span = item.find_element(By.CSS_SELECTOR, 'span.tag_comm3 > em')
            print("Date:", date_span.text)
        except Exception:
            print("Date: Not found")

# 페이지네이션 루프
while True:
    extract_items()
    # 페이지네이션 div에서 다음 페이지를 클릭하여 이동해야 한다.
    # 부동산 114에서 페이지네이션 div는 다음과 같은 구조로 되어 있다.
    # 즉, <strong> 태그 다음에 나오는 <a> 태그를 클릭하여 다음 페이지로 이동한다.
    # <div class="paging pagingBasic">
    #   <strong><span class="skip">현재페이지</span>1</strong>
    #   <a href="javascript:goPage(2, 1);">2</a>
    #   <a href="javascript:goPage(3, 1);">3</a>
    #   <a href="javascript:goPage(4, 1);">4</a>
    #   <a href="javascript:goPage(5, 1);">5</a>
    #   <a href="javascript:goPage(6, 1);">6</a>
    #   <a href="javascript:goPage(7, 1);">7</a>
    #   <a href="javascript:goPage(8, 1);">8</a>
    #   <a href="javascript:goPage(9, 1);">9</a>
    #   <a href="javascript:goPage(10, 1);">10</a>
    #   <a href="javascript:next_page(1);"><span class="ico_comm_s next_10">다음 10페이지</span></a>
    # </div>
    pagination_div = driver.find_element(By.XPATH, pagination_xpath)
    skip_found = False
    next_page_clicked = False
    elems = pagination_div.find_elements(By.XPATH, './*')
    for elem in elems:
        if not skip_found:
            if elem.tag_name == 'strong':
                try:
                    span = elem.find_element(By.CLASS_NAME, 'skip')
                    skip_found = True
                    print("Skip found:", elem.text)
                except Exception as e:
                    print("Error finding skip:", e)
                    exit(1)
        elif elem.tag_name == 'a':
            try:
                # elem.click()으로 페이지를 넘기고자 하였으나, 다음 Exception 발생.
                # Error clicking next page: Message: element click intercepted: Element is not clickable at point (394, 5069)
                # Google 검색 결과로 다음 page를 참조하여 해결
                # https://www.geeksforgeeks.org/how-to-fix-seleniums-element-is-not-clickable-at-point/ 에 제안된 방식중
                # "Scroll to the element"는 동작하지 않았고, "Click using JavaScript"는 동작하여 적용.
                # href가 javascript로 정의되어 있어서 click()으로는 동작하지 않는 것으로 추정됨.
                print("Clicking next page:", elem.text)
                driver.execute_script("arguments[0].click();", elem)
                next_page_clicked = True
                break
            except Exception as e:
                print("Error clicking next page:", e)
                exit(1)
    if not next_page_clicked:
        print("No more pages to navigate.")
        break

driver.quit()