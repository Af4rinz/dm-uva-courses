from .Base import BaseCrawler
import requests
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger('__main__')


class UCB(BaseCrawler):
    Course_Page_Url = "http://guide.berkeley.edu/courses/"
    University = "University of California Berkeley"
    Abbreviation = "UCB"
    University_Homepage = "https://www.berkeley.edu/"

    # Below fields didn't find in the website
    Prerequisite = None
    References = None
    Scores = None
    Projects = None
    Professor_Homepage = None

    def get_courses_of_department(self, department):
        a_element = department.find('a')
        Department_Name = a_element.text
        department_url = "http://guide.berkeley.edu" + a_element.get('href')
        Course_Homepage = department_url

        department_page_content = requests.get(department_url).text
        department_soup = BeautifulSoup(department_page_content, 'html.parser')

        courses = department_soup.find_all(class_='courseblock')

        return courses, Department_Name, Course_Homepage

    def get_course_data(self, course):
        Course_Title = course.find(class_="title").text

        Unit_Count = course.find(class_="hours").text
        Unit_Count = Unit_Count[:-5].rstrip()

        Description = course.find(class_='courseblockdesc').text

        course_sections = course.find_all(class_='course-section')

        Objective = None
        Outcome = None
        Professor = None
        Required_Skills = None

        for section in course_sections:
            inner_sections = section.find_all('p')
            for inner_section in inner_sections:
                inner_section_title = inner_section.find('strong')

                if inner_section_title.text == "Course Objectives:":
                    inner_section_title.decompose()
                    Objective = inner_section.text.strip()

                if inner_section_title.text == "Student Learning Outcomes:":
                    inner_section_title.decompose()
                    Outcome = inner_section.text.strip()

                if inner_section_title.text == "Instructor:":
                    inner_section_title.decompose()
                    Professor = inner_section.text.strip()

                if inner_section_title.text == "Prerequisites:":
                    inner_section_title.decompose()
                    Required_Skills = inner_section.text.strip()

        return Course_Title, Unit_Count, Objective, Outcome, Professor, Required_Skills, Description

    def handler(self):
        html_content = requests.get(self.Course_Page_Url).text
        soup = BeautifulSoup(html_content, 'html.parser')

        departments = soup.find(id='atozindex').find_all('li')
        for department in departments:
            courses, Department_Name, Course_Homepage = self.get_courses_of_department(department)
            for course in courses:
                Course_Title, Unit_Count, Objective, Outcome, Professor, Required_Skills, Description = self.get_course_data(
                    course)

                self.save_course_data(
                    self.University, self.Abbreviation, Department_Name, Course_Title, Unit_Count,
                    Professor, Objective, self.Prerequisite, Required_Skills, Outcome, self.References, self.Scores,
                    Description, self.Projects, self.University_Homepage, Course_Homepage, self.Professor_Homepage
                )

            logger.info(f"{self.Abbreviation}: {Department_Name} department's data was crawled successfully.")

        logger.info(f"{self.Abbreviation}: Total {self.course_count} courses were crawled successfully.")
