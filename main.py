### FRONT-END START ###

print("\nWelcome to the MCS-DS Course Browser!")
print("-------------------------------------")

print("\nLoading Dependencies...")
import subprocess
subprocess.run(["pip", "install", "-r", "requirements.txt"])

### LOAD REFERENCES ###
import course_data
import course_catalog_crawler
import requirements
import degree_scraper
import topic_miner
import BM25
import course_selector

### MAIN ###

# course data
print("\nChecking for Data Availability...")
data_load_success = course_data.LoadCourses()
if data_load_success == True :
    print("Course Data is Available!")
else :
    print("Course Data is Unavailable.")
    user_response = input("Would you like to rebuild the database now? [type \"yes\" or \"no\"]:  "   )
    if (user_response.lower() != "yes") and (user_response.lower() != "y") :
        print("ok, goodbye!")
        quit()
       
# degree requirements
print("\nChecking for Degree Requirements...")
req_load_success = requirements.LoadRequirements()
if req_load_success == True :
    print("Degree Requirements are Available!")
else :
    print("Degree Requirements are Unavailable.")
    user_response = input("Would you like to rebuild the requirements now? [type \"yes\" or \"no\"]:  "   )
    if not ((user_response.lower() == "yes") or (user_response.lower() == "y")) :
        print("ok, goodbye!")
        quit()

# reload data and requirements is needed
# TODO: user feedback in the methods
if (data_load_success == False) or (req_load_success == False) :
    print("\nReloading Degree Requirements and Course Data...")
    # loading some of the data failed, all structures should be emptied
    course_data.Empty()
    requirements.Empty()
    
    # run degree scraper to find requirements and dso specific courses
    courses_from_reqs_list = degree_scraper.FindRequirements(requirements)
    for (course_title, course_description) in courses_from_reqs_list :
        course_data.AddCourse(course_title, course_description, True)
        
    # run course catalog crawler to find general courses
    courses_from_catalog_list = course_catalog_crawler.FindCoursesOnline()
    for (course_title, course_description) in courses_from_catalog_list :
        course_data.AddCourse(course_title, course_description, False)

    # rewrite the courses and requirements to file
    course_data.WriteAllCoursesToFile()
    requirements.WriteRequirementsToFile()

# clean documents so they are the same between topic miner and BM25
print("\nCleaning Documents...")
courses_dso_bagOfWords_dict = course_data.CleanCourses(course_data.courses_dso_dict)

#print("\nnGram Tester...")
#topic_miner.nGram_Tester(courses_dso_bagOfWords_dict)

# topic mining
print("\nChecking for Topics...")
topics_load_success = topic_miner.LoadTopics()
if topics_load_success == True:
    print("Topics are Available!")
else :
    print("Topics are Unavailable.")
    user_response = input("Would you like to re-mine the topics now? [type \"yes\" or \"no\"]:  "   )
    if not ((user_response.lower() == "yes") or (user_response.lower() == "y")) :
        user_response = input("Would you like to continue without available topics? [type \"yes\" or \"no\"]:  "   )
        if not ((user_response.lower() == "yes") or (user_response.lower() == "y")) :
            print("ok, goodbye!")
            quit()
    else :
        # re-mine for topics
        topic_miner.Mine_Topics(courses_dso_bagOfWords_dict)
        topic_miner.WriteTopicsToFile()
        topics_load_success = True


# main UI loop
course_cnt = len(courses_dso_bagOfWords_dict)
req_cnt = sum(requirements.req_counts)
user_response = ""
exit_response = "quit"
while (user_response.lower() != exit_response) :
    print("\nWelcome to the MCS-DS Course Browser!")
    print("-------------------------------------\n")    
    print("There are", course_cnt, "courses available to fufill", req_cnt, "requirements.\n")
    if (topics_load_success == True) :
        print("Available Topics:")
        for t in topic_miner.topics_list :
            print(str(t))
        print()
        
    user_response = input("What subjects are you interested in? [type \"" + exit_response + "\" to exit]:  ")
    
    if user_response.lower() != exit_response :
        # use BM25 to determine ranked list
        ranked_list = BM25.rank_collection(user_response, courses_dso_bagOfWords_dict)
        #print("Ranked List:")
        #print('\n'.join(ranked_list))

        user_course_list = course_selector.select_from_ranked_list(ranked_list)

        print("\nRecommended Course List:")
        for i in range(len(user_course_list)) :
            print(str(i+1)+")", user_course_list[i])
        print("\n*WARNING: Please verify any prerequisites are met before using recommended course list!")
