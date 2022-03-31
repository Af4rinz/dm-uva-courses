from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains


def iterate_over_institutions():
    pass

def iterate_over_courses(firefox_driver):
    path="/html/body/div/div[3]/div/div/div/article/div/table/tbody/tr[{}]/td/div/table/tbody/tr[2]/td[2]/a"
    url_base = "https://studiegids.uva.nl"
    courses = []
    # 42 courses
    for i in range(2, 4, 2):
        print(path.format(i))
        element = None
        try_count = 0
        while try_count < 5:
            try:
                element = firefox_driver.find_element(by=By.XPATH, value=path.format(i))
                break
            except:
                try_count += 1
                continue
        if try_count == 5:
            continue
        url = element.get_attribute('href')
        driver.execute_script("window.open('');")
        window = firefox_driver.window_handles[1]
        driver.switch_to.window(window)
        firefox_driver.get(url)
        WebDriverWait(firefox_driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/header/nav[2]/div/ul/li/a"))
        )

        course = extract_information(firefox_driver)
        courses.append(course)
        
        
        firefox_driver.close()
        firefox_driver.switch_to.window(firefox_driver.window_handles[0])
    return courses

 
def handle_pagination(firefox_driver):
    try:
        pagination = firefox_driver.find_element(by=By.CLASS_NAME, value="next").find_element(By.XPATH, value="./a")
        pagination.click()
        return True
    except Exception as e:
        return False
    
    
def extract_information(firefox_driver):
    needed_div = firefox_driver.find_element(by=By.XPATH, value="/html/body/div/div[3]/div/div[1]/article/div")
    content = {}
    content["url"] = firefox_driver.current_url
    headers = ["Credits", "Objectives", "Contents", "Required prior knowledge", "Registration", "Study materials", "Assessment"]
    is_in_parent = True
    cursor = 1
    for header in needed_div.find_elements(By.XPATH, value="./child::*"):
        if header.text in headers:
            try: 
                content[header.text] = needed_div.find_element(By.XPATH, value="./child::*[{}]".format(cursor + 1)).text
            except Exception as e:
                print(e)
        cursor += 1
    table = driver.find_element(by=By.XPATH, value="/html/body/div/div[3]/div/div[1]/article/div/div")
    needed_data = [
        "Credits", "Lecturer(s)"
    ]
    xpath_within_table = "/html/body/div/div[3]/div/div[1]/article/div/div/table/tbody/tr[{}]"
    for i in range(1, 10):
        try:
            row = table.find_element(By.XPATH, value=xpath_within_table.format(i))
            first_column = row.find_element(By.XPATH, value="./td[1]")
            if first_column.text in needed_data:
                content[first_column.text] = row.find_element(By.XPATH, value="./td[2]").text
                if first_column.text == "Lecturer(s)":
                    content["Lecturer homepage"] = row.find_element(By.XPATH, value="./td[2]/ul/li/a").get_attribute('href')
        except Exception as e:
            break
    content["course_title"] = driver.find_element(by=By.XPATH, value="/html/body/div/div[3]/div/div[1]/article/div/h1").text
    print(content)
    return content


if __name__ == "__main__":
    driver = webdriver.Firefox()

    main_page = driver.get('https://studiegids.uva.nl/xmlpages/page/2021-2022-en/search-course')

    get_all_courses = driver.find_element(by=By.CLASS_NAME, value='search-all')
    get_all_courses.click()

    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, "/html/body/div/div[3]/div/div/div/aside/div/div/div[7]/ul/li"))
    )
    dept_count = len(driver.find_elements(by=By.XPATH, value="/html/body/div/div[3]/div/div/div/aside/div/div/div[7]/ul/li"))
    cursor = 0
    # import sys
    # sys.exit(0)
    while cursor < dept_count:
        try:
            driver.find_element(by=By.XPATH, value="/html/body/div/div[3]/div/div/div/aside/div/div/div[7]/a").click()
        except Exception as e:
            print(e)
        print(cursor)
        departments = driver.find_elements(by=By.XPATH, value="/html/body/div/div[3]/div/div/div/aside/div/div/div[7]/ul/li")
        dept = departments[cursor]
        courses = []
        dept_name = dept.text
        try:
            dept.click()
        except Exception as e:
            print(e)
            cursor += 1
            continue
        print("Dept:", dept_name)
        WebDriverWait(driver, 30).until(
           EC.element_to_be_clickable((By.CLASS_NAME, "icon-arrow"))
        )

        # //*[@id="search-results"]
        # style="cursor: wait;"
        # https://www.selenium.dev/selenium/docs/api/java/org/openqa/selenium/support/ui/ExpectedConditions.html
        while True:
            import time
            while True:
                try:
                    style = driver.find_element(by=By.XPATH, value="//*[@id=\"search-results\"]").get_attribute('style')
                    if style == 'cursor: wait;':
                        continue
                    else:
                        break
                except Exception as e:
                    print(e)
                    time.sleep(0.5)
                    break
            # WebDriverWait(driver, 30).until(
            #     EC.element_to_be_clickable((By.CLASS_NAME, "icon-arrow"))
            # )
            courses.append(iterate_over_courses(driver))
            # if handle_pagination(driver) == False:
            #     break
            break
        # handle next dept
        # /html/body/div/div[3]/div/div/div/aside/div/div/div[7]/ul/li
        driver.find_element(by=By.XPATH, value="/html/body/div/div[3]/div/div/div/aside/div/div/div[7]/ul/li").click()
        cursor += 1
        WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, "/html/body/div/div[3]/div/div/div/aside/div/div/div[7]/ul/li[3]/a"))
        )
    driver.close()