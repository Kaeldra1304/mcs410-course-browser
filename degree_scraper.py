import requests
from bs4 import BeautifulSoup
import re

import pdf_processer

# translates english number string into integer
def numStrToInt(num_str) :
    numStr_list = ["zero","one","two","three","four","five","six","seven","eight","nine","ten"]
    return numStr_list.index(num_str)

# scrapes online degrees requirements for requirements
# and adds them directly to requirements script, variable r
# AND pulls available course syllabuses
#   in: r (requirements)
#   out: (list of tuple) [course title (string), course description (string)]
def FindRequirements(r) :
    courses_from_reqs_list = list()
    print('\r')
    
    page = requests.get(degree_webpage_url)
    #print(page.text)

    soup = BeautifulSoup(page.text, 'html.parser')
    
    #find where id is "Requirements" on webpage
    req_section = soup.find(id='Requirements').parent.parent
    #print(req_section)
    #print("1~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        
    #find all <h3> and store <p>
    main_req = []
    for header in req_section.find_all('h3') :
        req_title = header.text
        req_description = ""
        num_req = -1
        num_tot_deg = -1
    
        #print(req_title)
    
        req_description_tag = header.find_next_sibling('p')
        if req_description_tag is not None :
            req_description = req_description_tag.text
            #print(req_description)
            
            #parse requirement description for required number
            if "course" in req_description :
                idx = req_description.index("course")
                req_description_split = req_description[:idx-1].strip().split()
                num = numStrToInt(req_description_split[-1])
                if "not required" in req_description.lower() :
                    num_req = 0
                    num_tot_deg = num
                else :
                    num_req = num
    
        #check for html courses table
        courses_table_tag = header.find_next_sibling('table')
        if courses_table_tag is not None :
            #print("COURSES TABLE")
            #print(courses_table_tag)
        
            #each row is a different requirement
            for table_row in courses_table_tag.find_all('tr') :
                table_cells = table_row.find_all('td')
                req_type = table_cells[0].find('em').text
                #print(req_type)
            
                for line in table_cells[1].prettify().split('<br/>') :
                    #print(line)
                
                    # determine course title
                    course_title = ""
                    soupy_line = BeautifulSoup(line, 'html.parser')
                    clean_line = re.compile(r"\s+").sub(" ", soupy_line.text).strip()
                    if re.match(r".*\b[A-Z]{2,4}\b \b[0-9]{3}\b.*", clean_line) :                    
                        course_title = clean_line
                    else :
                        #print("FAIL MATCH:", clean_line)
                        continue
                    #print(course_title)
                    
                    # add requirement                    
                    r.AddRequirement(req_title + "-" + req_type, course_title, num_req, num_tot_deg)
            
                    # find course description
                    course_description = ""
                    # find pdf file for course description
                    #print(soupy_line)
                    file_link = soupy_line.find("a")
                    if file_link is not None :
                        file_url = file_link['href']
                        #print(file_url)
                    
                        # find course description from pdf file url
                        course_description = pdf_processer.ParsePDFFile_CourseDescription(file_url)
                        #print(course_description)

                    # add course info to list
                    courses_from_reqs_list.append((course_title, course_description))
                    
                    # user feedback
                    print("  " + str(sum(r.req_counts)) + " requirements found, " + str(len(courses_from_reqs_list)) + " courses found\r", end='\r')
                            
        else :    
            #check for html courses list
            courses_list_tag = header.find_next_sibling('ul')
            #print("COURSES LIST")
            #print(courses_tag)
            if courses_list_tag is not None :
                #courses_list_tag_coursesList = courses_list_tag.find_all('li')
                #print(courses_list_tag_coursesList)
                for course in courses_list_tag.find_all('li') :
                                
                    # determine course title
                    course_title = ""
                    course_text = course.text.strip()
                    course_text = re.compile(r"\s+").sub(" ", course_text).strip()
                    if re.match(r".*\b[A-Z]{2,4}\b \b[0-9]{3}\b.*", course_text) :     
                        course_title = course_text                    
                    else :
                        #print("FAIL MATCH:", course_text)
                        continue
                    #print(course_title)
                    
                    # add requirement                    
                    r.AddRequirement(req_title, course_title, num_req, num_tot_deg)
                
                    course_description = ""
                    # find file for course description
                    file_link = course.a
                    if file_link is not None :
                        file_url = file_link['href']
                        #print(file_url)
                    
                        # find course description from pdf file url
                        course_description = pdf_processer.ParsePDFFile_CourseDescription(file_url)
                        #print(course_description)
                
                    # add course info to list
                    courses_from_reqs_list.append((course_title, course_description))
                    
                    # user feedback
                    print("  " + str(sum(r.req_counts)) + " requirements found, " + str(len(courses_from_reqs_list)) + " courses found\r", end='\r')

    print()
    return courses_from_reqs_list

### MAIN ###
degree_webpage_url = 'https://siebelschool.illinois.edu/academics/graduate/professional-mcs/online-master-computer-science-data-science'