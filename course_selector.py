import numpy as np
import requirements

# selects the highest ranked courses from a ranked list 
# that meet the degree requirements
#   in: ranked_list (list of string)
#   out: user_course_list (list of string)
def select_from_ranked_list(ranked_list) :
    # selector code
    req_counts_array = np.array(requirements.req_counts)
    #print("req_counts_array", req_counts_array)
    user_req_array = np.zeros(req_counts_array.shape, int)
    #print("user_req_array", user_req_array)

    ranked_list_index = 0
    user_course_list = []
    while not np.array_equal(req_counts_array, user_req_array) :
        # grab next course
        next_course = ranked_list[ranked_list_index]
        ranked_list_index += 1
    
        # find requirements list
        course_req = requirements.req_courses_dict[next_course]
        #print(next_course, "course_req", course_req)
    
        # loop through requirements by indexing
        # if course meets an unfulfilled requirement,
        # then update user_req_array and add course to course list
        for i in range(len(req_counts_array)) :
            #print("Checking requirement", req_titles[i], "for course", next_course)
            if course_req[i] > 0 :
                # course meets requirement
                if user_req_array[i] < req_counts_array[i] :
                    # need a course in this requirement
                    user_req_array[i] = user_req_array[i] + 1
                    user_course_list.append(next_course + " [" + requirements.req_titles[i].strip() + "]")
                    #print("add course")
                    break #stopping looping
                    
    return user_course_list
 