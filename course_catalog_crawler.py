import requests
from bs4 import BeautifulSoup

# scrapes online course catalog for course titles & descriptions
#   in: N/A
#   out: (list of tuple) [course title (string), course description (string)]
def FindCoursesOnline() :
    print('\r')
    page = requests.get(course_catalog_main_url + course_catalog_subpage_url)
    #print(page.text)
    #print("0~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    soup = BeautifulSoup(page.text, 'html.parser')

    #find where id is "tAll" for all courses regardless of semester
    courseTbl_section = soup.find(id='tAll').find("tbody")
    #print(courseTbl_section)
    #print("1~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

    courses_list = list()

    for row in courseTbl_section.find_all('tr') :
        r = row.find(class_ = 'rubric')
        t = row.find(class_ = 'title')
    
        #if r is None :
            #print("NO RUBRIC:", row)    
        #if t is None :
            #print("NO TITLE:", row)
    
        if (r is not None) and (t is not None) :
            title = r.text + " " + t.text
            #print(title)
            url = course_catalog_main_url + r.a['href']
            #print(url)
        
            course_page = requests.get(url)
            course_soup = BeautifulSoup(course_page.text, 'html.parser')
        
            #find where id is "extCoursesDescription" and class is "extCoursesProfileContent"
            description_section = course_soup.find(id="extCoursesDescription")
            if description_section is not None :
                description_content = description_section.find(class_="extCoursesProfileContent")
                if description_content is not None :
                    description = description_content.text
                        
                    # save to course dictionary
                    courses_list.append((title, description))
                    
        print("  " + str(len(courses_list)) + " courses found\r", end='\r')
    
    print()
    return courses_list

### MAIN ###
course_catalog_main_url = 'https://siebelschool.illinois.edu'
course_catalog_subpage_url = '/academics/courses'