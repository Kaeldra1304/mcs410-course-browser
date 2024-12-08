import io
import math

def calc_dcg(rankings) :
    dcg_sum = 0.0
    for r_i in range(len(rankings)) :
        gain = rankings[r_i]
        
        rank = r_i + 1
        if rank == 1 :
            dcg_sum += gain
        else :
            #print(gain, "/log2(", rank,")")
            dcg_sum += (gain / math.log(rank, 2))
        
        #print(dcg_sum)
    return dcg_sum

topics_list = []
with open("verification_topics.txt", "r") as f:
    
    for line in f.readlines() :
        split_line = line.strip().split(',')
        
        topic_words = []
        for word in split_line[1:] :
            if (not word.isspace()) and (word != "") :
                topic_words.append(word)
        topics_list.append(' '.join(topic_words))
                
print("Topics List")
print(topics_list)

course_rankings_dict = dict()
first_line = True # ignore header
with open("verification_ranked.txt", "r") as f :
    for line in f.readlines() :
        
        if first_line == True :
            first_line = False
        else :
            split_line = line.strip().split(',')
            key = split_line[0]
        
            ver_ranks = []
            for s in split_line[1:] :
                ver_ranks.append(int(s))
            
            course_rankings_dict[key] = ver_ranks
        
print("Course Rankings")
for k in course_rankings_dict.keys() :
    print(k, ":", course_rankings_dict[k])

    
### LOAD REFERENCES ###
import course_data
import requirements
import BM25
import course_selector

### MAIN ###

# course data
print("\nChecking for Data Availability...")
data_load_success = course_data.LoadCourses()
if data_load_success == True :
    print("Course Data is Available!")
       
# degree requirements
print("\nChecking for Degree Requirements...")
req_load_success = requirements.LoadRequirements()
if req_load_success == True :
    print("Degree Requirements are Available!")

# only verify with available data
if (data_load_success == True) and (req_load_success == True) :
    # clean documents so they are the same between topic miner and BM25
    print("\nCleaning Documents...")
    courses_dso_bagOfWords_dict = course_data.CleanCourses(course_data.courses_dso_dict)
    print()    
    
    # list of queries is the same as the topics
    for i in range(len(topics_list)) :
        ver_query = topics_list[i]
        print("Query [" + ver_query + "]:")
                
        # calculate ideal dcg @ 8 using topic rankings
        topics_rankings = []
        for k in course_rankings_dict.keys() :
            topics_rankings.append(course_rankings_dict[k][i]) # ranking for this course & topic combination
        topics_rankings.sort(reverse = True) # in-place sort highest ranking first
        #print(topics_rankings)        
        i_dcg = calc_dcg(topics_rankings[0:8])
    
        # use BM25 to determine ranked list
        ranked_list = BM25.rank_collection(ver_query, courses_dso_bagOfWords_dict)
        #print("Ranked List:")
        #print('\n'.join(ranked_list))    
        
        # calculate Normalized DCG @ 8
        BM25_rankings = []
        for course_title in ranked_list[0:8] :
            BM25_rankings.append(course_rankings_dict[course_title][i])
        #print(BM25_rankings)
        dcg = calc_dcg(BM25_rankings)        
        
        ndcg = dcg / i_dcg
        #print("BM25_rankings NDCG@8 = " + str(round(ndcg, 4)))
        
        # course selection
        user_course_list = course_selector.select_from_ranked_list(ranked_list)
        print("\nRecommended Course List:")
        print('\n'.join(user_course_list))    
        
        # calculate Normalized DCG @ 8
        selector_rankings = []
        for course_title_req in user_course_list[0:8] :
            course_title = (course_title_req.split('[')[0]).strip()
            selector_rankings.append(course_rankings_dict[course_title][i])
        #print(selector_rankings)
        dcg = calc_dcg(selector_rankings)        
        
        ndcg = dcg / i_dcg
        print("selector_rankings NDCG@8 = " + str(round(ndcg, 4)))
        
        