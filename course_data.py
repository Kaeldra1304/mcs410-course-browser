import word_helper

class Course :
    def __init__(self, title, description):
        self.title = title
        self.description = description
        
    def __str__(self):
        return f"{self.title}:\n{self.description}"
        
# loads courses into courses_all_dict & courses_dso_dict from files
# using ReadCoursesFromFile(), dictionaries are empty if issue reading files
#   in: N/A
#   out: success (Boolean)
def LoadCourses() :
    global courses_all_dict
    global courses_dso_dict
    
    success = False
    
    Empty() # be sure to empty the data structures first
    courses_all_dict = ReadCoursesFromFile(courses_all_filePath)
    courses_dso_dict = ReadCoursesFromFile(courses_dso_filePath)
    
    # verify data loaded
    len_courses_all_dict = len(list(courses_all_dict.keys()))
    len_courses_dso_dict = len(list(courses_dso_dict.keys()))
    if (len_courses_all_dict > 0) and (len_courses_dso_dict > 0) and (len_courses_all_dict > len_courses_dso_dict) :
        success = True

    return success

# reads Courses from file
#   in: filePath
#   out: (dictionary) [key: course title string, value: Course obj]
def ReadCoursesFromFile(file_path) :
    courses_dict = dict()
    try :
        with open(file_path, "r") as f:
            title = ""
            description = ""
            for line in f :
                if "~~~~~" in line :
                    # new title line, save old course if exists
                    # save new title
                    title = line.strip()[5:-5]
                else :
                    # save new part of description
                     description = description + line.strip()
                
                # check for course to save
                if (title != "") and (description != "") : 
                    courses_dict[title] = Course(title, description)
                    title = ""
                    description = ""
            
        return courses_dict
    except Exception as e:
        print("Exception in course_data.py:", e)
        return dict()
        
# writes all Course dictionaries to file
#   in: N/A
#   out: N/A
def WriteAllCoursesToFile() :
    global courses_all_dict
    global courses_dso_dict
    
    WriteCoursesToFile(courses_all_filePath, courses_all_dict)
    WriteCoursesToFile(courses_dso_filePath, courses_dso_dict)
        
# writes Course to file
#   in: filePath (string), (dictionary) [key: course title string, value: Course obj]
#   out: N/A
def WriteCoursesToFile(file_path, courses_dict) :
    global courses_all_dict
    global courses_dso_dict
    
    with open(file_path, "w") as f:
        for key in courses_dict.keys() :
            # cycle through dictionary to write each key:value pair separate
            f.writelines("~~~~~" + courses_dict[key].title + "~~~~~\n")
            f.writelines(courses_dict[key].description +"\n")

# empties out the data structures for re-writing
#   in: N/A
#   out: N/A
def Empty() :
    global courses_all_dict
    global courses_dso_dict
    
    courses_all_dict = dict()
    courses_dso_dict = dict()

# uses course title to find course in course data
#   in: course_title (string)
#   out: (Course obj)
def FindCourse(course_title) :
    global courses_all_dict
    global courses_dso_dict
    
    found_course = None
    
    if course_title in courses_dso_dict :
        found_course = courses_dso_dict[course_title]
    elif course_title in courses_all_dict :
        found_course = courses_all_dict[course_title]
    else :
        # search course dictionary for only course number
        # THIS WILL OVER MATCH FOR MOST COURSES
        # only want to do this if existing description == ""
        course_title_split = course_title.split()
        last_2_digits = int(course_title_split[1][-2:])
        if last_2_digits < 98 :
            course_code = course_title_split[0] + " " + course_title_split[1]
            for key in courses_all_dict.keys() :
                if course_code in key :
                    found_course = courses_all_dict[key]
    
    return found_course

# adds course to the correct data structure(s),
# check for overlapping and duplicate courses using FindCourse().
# If match found, merge descriptions.
#   in: course_title (string), (Course obj), dso (Boolean)
#   out: N/A
def AddCourse(course_title, course_description, dso_flag) :
    global courses_all_dict
    global courses_dso_dict
        
    # search for course in dictionaries
    found_course = FindCourse(course_title)
    
    # if course already exists, consider merging
    if found_course != None :
        # merge Courses if titles match exactly or if found course's description is empty
        if (found_course.title == course_title) or (found_course.description == "") :
            courses_all_dict[found_course.title].description = courses_all_dict[found_course.title].description + course_description
            if dso_flag :
                courses_dso_dict[found_course.title].description = courses_dso_dict[found_course.title].description + course_description
    else :
        # course doesn't exist yet        
        new_course = Course(course_title, course_description)
        courses_all_dict[course_title] = new_course        
        if dso_flag :
            courses_dso_dict[course_title] = new_course

# prints course dictionary to console
#   in: (dictionary) [key: course title string, value: Course obj]
#   out: N/A
def PrintCourseDict_Debug(courses_dict) :
    for (key, course) in courses_dict.items() :
        print(course.title)
        print(course.description)

# clean document contents
#   in: (dictionary) [key: original course title string, value: Course obj]
#   out: (dictionary) [key: original course title (string), value: clean course description (list of string)]
def CleanCourses(courses_dict) :    
    clean_documents = dict()
    
    # cycle through courses by key
    i = 0
    for key in courses_dict.keys() :
        
        # add clean document words to the dictionary
        clean_documents[key] = word_helper.CleanWordString(courses_dict[key].description)
        i += 1
        
        print("  " + str(i) + " of " + str(len(courses_dict)) + " documents cleaned", end='\r')
        
    return clean_documents


### MAIN ###
courses_all_filePath = "courses_all.txt"
courses_dso_filePath = "courses_dso.txt"
courses_all_dict = dict()
courses_dso_dict = dict()