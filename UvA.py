import logging
import time
from BaseCrawler import BaseCrawler
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

logger = logging.getLogger('__main__')

class UvA(BaseCrawler):
    driver = None
    course_page_url = "https://studiegids.uva.nl/xmlpages/page/2021-2022-en/search-course"
    university = "Universiteit van Amsterdam"
    abbreviation = "UvA"
    university_homepage = "https://studiegids.uva.nl"
    outcome = None
    projects = None
    required_skill = None

    def get_courses_of_department(self, department):
        path="/html/body/div/div[3]/div/div/div/article/div/table/tbody/tr[{}]/td/div/table/tbody/tr[2]/td[2]/a"
        courses = []
        # 42 courses
        while True:
            for i in range(2, 42, 2):
                try: 
                    element = self.driver.find_element(by=By.XPATH, value=path.format(i))
                    course = element.get_attribute('href')
                    courses.append(course)
                except Exception as e:
                    print(e)
            if self.pagination_handler() == False:
                break
        return courses

    def get_course_data(self, course):
        self.driver.get(course)
        WebDriverWait(self.driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/header/nav[2]/div/ul/li/a"))
        )
        needed_div = self.driver.find_element(by=By.XPATH, value="/html/body/div/div[3]/div/div[1]/article/div")
        content = {
            "objectives": None,
            "url": None,
            "course title": None,
            "credits": None,
            "lecturer(s)": None,
            "lecturer homepage": None,
            "required prior knowledge": None,
            "recommended prior knowledge": None,
            "contents": None,
            "study materials": None,
            "assessment": None,
        }
        content["url"] = self.driver.current_url
        headers = ["objectives", "contents", "required prior knowledge", "recommended prior knowledge", "study materials", "assessment"]
        # cursor = 1
        parent_header = " "
        for header in needed_div.find_elements(By.XPATH, value="./child::*"):
            if header.text.lower() in headers:
                parent_header = header.text.lower()
                continue
            try:
                if content[parent_header] == None:
                    content[parent_header] = ""
            except Exception as e:
                print(e)
                continue
            try: 
                # for child in needed_div.find_elements(By.XPATH, value="./child::*[{}]".format(cursor + 1)):
                content[parent_header] += header.text
                content[parent_header] += "\n"
            except Exception as e:
                print(e)
            # cursor += 1
        table = self.driver.find_element(by=By.XPATH, value="/html/body/div/div[3]/div/div[1]/article/div/div")
        needed_data = [
            "credits", "lecturer(s)"
        ]
        xpath_within_table = "/html/body/div/div[3]/div/div[1]/article/div/div/table/tbody/tr[{}]"
        for i in range(1, 10):
            try:
                row = table.find_element(By.XPATH, value=xpath_within_table.format(i))
                first_column = row.find_element(By.XPATH, value="./td[1]")
                if first_column.text.lower() in needed_data:
                    content[first_column.text.lower()] = row.find_element(By.XPATH, value="./td[2]").text
                    if first_column.text.lower() == "lecturer(s)":
                        content["lecturer homepage"] = row.find_element(By.XPATH, value="./td[2]/ul/li/a").get_attribute('href')
            except Exception as e:
                break
        content["course title"] = self.driver.find_element(by=By.XPATH, value="/html/body/div/div[3]/div/div[1]/article/div/h1").text

        return content["url"], content["course title"], content["credits"], content["lecturer(s)"], content["lecturer homepage"],\
                content["required prior knowledge"] or content["recommended prior knowledge"] or None,\
                content["objectives"], content["contents"],\
                content["study materials"], content["assessment"]

    def pagination_handler(self):
        try:
            pagination = self.driver.find_element(by=By.CLASS_NAME, value="next").find_element(By.XPATH, value="./a")
            pagination.click()
        except Exception as e:
            return False
        
        while True:
            try:
                style = self.driver.find_element(by=By.XPATH, value="//*[@id=\"search-results\"]").get_attribute('style')
                if style == 'cursor: wait;':
                    continue
                else:
                    break
            except Exception as e:
                print(e)
                time.sleep(0.5)
                break
        return True


    def handler(self):
        self.driver = webdriver.Firefox()
        self.driver.get(self.course_page_url)
        self.driver.find_element(by=By.CLASS_NAME, value='search-all').click()
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div/div[3]/div/div/div/aside/div/div/div[7]/ul/li"))
        )
        dept_count = len(self.driver.find_elements(by=By.XPATH, value="/html/body/div/div[3]/div/div/div/aside/div/div/div[7]/ul/li"))
        cursor = 0
        while cursor < dept_count:
            try:
                self.driver.find_element(by=By.XPATH, value="/html/body/div/div[3]/div/div/div/aside/div/div/div[7]/a").click()
            except Exception as e:
                print(e)
                continue
            departments = self.driver.find_elements(by=By.XPATH, value="/html/body/div/div[3]/div/div/div/aside/div/div/div[7]/ul/li")
            dept = departments[cursor]
            dept_name = dept.text
            dept_name = dept_name[:dept_name.find('(')].strip()
            try:
                dept.click()
            except Exception as e:
                print(e)
                cursor += 1
                continue
            while True:
                try:
                    style = self.driver.find_element(by=By.XPATH, value="//*[@id=\"search-results\"]").get_attribute('style')
                    if style == 'cursor: wait;':
                        continue
                    else:
                        break
                except Exception as e:
                    print(e)
                    time.sleep(0.5)
                    break
            courses = self.get_courses_of_department(dept_name)
            # Open new tab
            self.driver.execute_script("window.open('');")
            window = self.driver.window_handles[1]
            self.driver.switch_to.window(window)

            for course in courses:
                url, course_title, credits, lecturers, lecturer_homepage, prerequisite, objectives, content, study_material, assessment = self.get_course_data(
                    course)
                self.save_course_data(
                    self.university, self.abbreviation, dept_name, course_title, credits,
                    lecturers, objectives, prerequisite, self.required_skill, self.outcome, study_material, assessment,
                    content, self.projects, self.university_homepage, url, lecturer_homepage
                )
            # Close tab
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
            logger.info(f"{self.abbreviation}: {dept_name} department's data was crawled successfully.")
            # handle next dept
            self.driver.find_element(by=By.XPATH, value="/html/body/div/div[3]/div/div/div/aside/div/div/div[7]/ul/li").click()
            cursor += 1
            WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/div/div[3]/div/div/div/aside/div/div/div[7]/ul/li[3]/a"))
            )
        logger.info(f"{self.Abbreviation}: Total {self.course_count} courses were crawled successfully.")
        self.driver.close()



crawler = UvA()
crawler.handler()