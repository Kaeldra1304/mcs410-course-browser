#loads requirements into data objects from file using 
#ReadRequirementsFromFile(), data objects empty if issue reading files
#   in: N/A
#   out: success (Boolean)
def LoadRequirements() :    
    global req_titles
    global req_counts
    global req_courses_dict
    
    success = False
    
    Empty() # be sure to empty the data structures first
    ReadRequirementsFromFile()
    
    # debugging
    #print(len(req_titles))
    #print(len(req_counts))
    
    if (sum(req_counts) > 0) and (len(req_titles) == len(req_counts)) :
        success = True
        for key in req_courses_dict.keys() :
            #print(len(req_courses_dict[key]))
            if len(req_courses_dict[key]) != len(req_titles) :
                success = False
                Empty()
                break
    
    return success
    
#reads requirement data from file and stores directly in data objects
#   in: N/A
#   out: N/A   
def ReadRequirementsFromFile() :
    global req_titles
    global req_counts
    global req_courses_dict
    
    try :
        with open(req_filePath, "r") as f:
            i = 0
            lines = f.readlines()
        
            # REWRITE SO THAT ALL LINES ARE IN WHILE LOOP AND CHECK FOR EMPTY LINE
            # parse line to req_titles if len(req_titles) == 0
            # else if parse line to req_counts if len(req_counts) == 0
            # else parse to requirements dictionary
            while i < len(lines) :
            
               # check for non-empty line
                if not lines[i].isspace() :            
                    if len(req_titles) == 0 :
                        # requirements titles (comma separated strings)
                        req_titles = lines[i].split(',')
                    elif len(req_counts) == 0 :
                        # requirements counts (comma separated ints)
                        req_counts = list(map(int, lines[i].strip().split(',')))
                    else :
                        # requirements dictionary
                        # each line is a new key, value pair
                        # format: "title" + ":" + "list of comma separated ints"
                        split_line = lines[i].split(':')
                        if len(split_line) >= 2 :
                            key = split_line[0]
                            value = list(map(int, split_line[1].strip().split(',')))
                            req_courses_dict[key] = value
            
                # increment line
                i += 1
            
    except Exception as e:
        #print("Exception in requirements.py:", e)
        Empty()
    
#write requirement data to file
#   in: N/A
#   out: N/A
def WriteRequirementsToFile() :
    global req_titles
    global req_counts
    global req_courses_dict
    
    with open(req_filePath, "w") as f:
        # write to file
        f.writelines(','.join(req_titles)+'\n')        
        f.writelines(','.join(list(map(str, req_counts)))+'\n')
        # cycle through dictionary to write each key:value pair separate
        for key in req_courses_dict.keys() :
            f.writelines(key + ':' + ','.join(list(map(str,req_courses_dict[key])))+'\n')
   
#empties out the data structures for re-writing
#   in: N/A
#   out: N/A
def Empty() :
    global req_titles
    global req_counts
    global req_courses_dict
    
    req_titles = []
    req_counts = []
    req_courses_dict = dict()
    
#adds requirement to data structure
#   in: req_title (string), course_title (string), num_needed (int), tot_num_needed (int)
#   out: N/A
def AddRequirement(req_title, course_title, num_needed, tot_num_needed = -1) :
    global req_titles
    global req_counts
    global req_courses_dict
    
    # check for new requirement
    if req_title not in req_titles :
        # add title
        req_titles.append(req_title)
        
        # add number required, may need to calculate from total number required if "non-required"
        non_required_flag = ((num_needed == 0) and (tot_num_needed > -1))
        if non_required_flag :
            num_needed = tot_num_needed - sum(req_counts)
        req_counts.append(num_needed)
        
        # cycle through course dictionary appending new requirement
        start_req_val = 0
        if non_required_flag :
            start_req_val = 1
        for key in req_courses_dict.keys() :
            req_courses_dict[key].append(start_req_val) # append a zero to start for all courses b/c its a new requirement

    # check for new course
    if (course_title is not None) and (course_title not in req_courses_dict) :
        # new course, initialize list to all zeroes (False)
        req_courses_dict[course_title] = [0] * len(req_titles)
            
    # find requirement index
    req_idx = req_titles.index(req_title)
    
    # check if requirement applies to all courses
    if course_title is None :
        # cycle through dictionary updating all courses
        for key in req_courses_dict.keys() :
            req_courses_dict[key][req_idx] = 1
    else :
        # update single course requirement in dictionary
        req_courses_dict[course_title][req_idx] = 1 # set this requirement, course combo to True

    # debugging
    #print(req_titles)
    #print(req_counts)
    #print(req_courses_dict)


### MAIN ###
req_filePath = "deg_requirements.txt"
req_titles = []
req_counts = []
req_courses_dict = dict()
