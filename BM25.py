import math
import word_helper

# testing only
import course_data

# calculate average document length
#   in: (dictionary) [key: original course title (string), value: clean course description (list of string)]
#   out: avg_doc_len (float)
def calc_avgLen(doc_dict) :  
    doc_len_sum = 0.0
    
    # cycle through courses by key
    for key in doc_dict.keys() :
        
        # add len of clean doc list to sum
        doc_len_sum = doc_len_sum + len(doc_dict[key])
        
    # calculate average document length
    avg_doc_len = doc_len_sum/len(doc_dict)
        
    return avg_doc_len

# create a dictionary with the count of every word 
#   in: (dictionary) [key: original course title (string), value: clean course description (list of string)]
#   out: (dictionary) [key: word string, value: doc cnt int]
def calc_word_doc_freq(doc_dict) :
    word_doc_freq_dict = dict()
    
    # cycle through documents
    for key in doc_dict.keys() :
        doc_contents = doc_dict[key]
        distinct_clean_words_list = list()
        
        # cycle through clean words in document, adding distinct ones to list
        for clean_word in doc_contents :
            # check clean word exists and not already in list before adding
            if clean_word not in distinct_clean_words_list :
                distinct_clean_words_list.append(clean_word)
                
        # cycle though distinct clean words, 
        # add the clean word to the document frequency dictionary if needed
        # then incrementing the count in the document frequency dictionary
        for clean_word in distinct_clean_words_list :
            # if clean word is not in the dictionary, add it
            if clean_word not in word_doc_freq_dict :
                word_doc_freq_dict[clean_word] = 0
            # increment the count of the clean word
            word_doc_freq_dict[clean_word] = word_doc_freq_dict[clean_word] + 1
                
    # return word document frequency
    return word_doc_freq_dict

# create a dictionary with the count of every word in the string
#   in: word_list (list of string)
#   out: (dictionary) [key: word string, value: count of word int]
def calc_term_freq(word_list) :
    term_freq_dict = dict() 
    
    # cycle through words
    # add word to the term frequency dictionary if needed
    # then incrementing the count in the term frequency dictionary
    for word in word_list :
        # if word is not in the dictionary, add it
        if word not in term_freq_dict :
            term_freq_dict[word] = 0
        # increment the count of the word
        term_freq_dict[word] = term_freq_dict[word] + 1
        
    return term_freq_dict

# scores a document based on a query
#   in: query (string), document words (list of string), avg_doc_len (float), num_docs_M (int),
#       word_doc_freq_dict (dictionary) [key: word string, value: doc cnt int]
#   out: N/A
def BM25 (query, doc_list, avg_doc_len, num_docs_M, word_doc_freq_dict, b, k) :
    doc_len = len(doc_list)
    
    # split and clean words in the query
    clean_query_word_list = word_helper.CleanWordString(query)
            
    # calculate the term frequencies in the query and the document
    query_term_freq_dict = calc_term_freq(clean_query_word_list)
    doc_term_freq_dict = calc_term_freq(doc_list)    
    
    # cycle through document
    score_sum = 0
    for wq in query_term_freq_dict.keys() :
        if wq in doc_term_freq_dict : # check only intersection words
            # word from the query is also in the document
            
            # calculte intermediate values
            c_wq = query_term_freq_dict[wq]
            c_wd = doc_term_freq_dict[wq]
            idf = math.log(((num_docs_M + 1)/word_doc_freq_dict[wq]), 2)
            doc_len_norm = 1 - b + b*(doc_len/avg_doc_len)
            
            # calculate this word's score
            word_score = c_wq * ((k+1) * c_wd)/(c_wd + k*doc_len_norm) * idf
            
            # add word's score to sum
            score_sum = score_sum + word_score
    
    # return final sum of word scores
    return score_sum

# rank documents in collection based on query
#   in: query (string), (dictionary) [key: original course title (string), value: clean course description (list of string)]
#   out: ranked list of courses by key (list)
def rank_collection(query, clean_docs_dict) :
    scores_list = [] # list of tuples: item[0] is course title, item[1] is score
        
    # average the lengths of the documents
    avg_doc_len = calc_avgLen(clean_docs_dict)
    
    # calculate collection wide parameters: num_docs_M, word_doc_freq_dict
    num_docs_M = len(clean_docs_dict)
    word_doc_freq_dict = calc_word_doc_freq(clean_docs_dict)
    
    # score each document based on the query, record in list
    for key in clean_docs_dict.keys() :
        doc_contents = clean_docs_dict[key]
        score = BM25(query, doc_contents, avg_doc_len, num_docs_M, word_doc_freq_dict, 0.5, 1)
        scores_list.append((key, score))    
    
    # sort scores list from largest to smallest score
    scores_list.sort(key=lambda tup: tup[1], reverse = True)
    #for s in scores_list :
        #print(s)

    # created ranked list of course titles
    ranked_list = [x[0] for x in scores_list]
    
    return ranked_list
           
    
### MAIN ###
#word_doc_freq_dict = dict()
#doc_term_freq_dict = dict()

# Test Run
test = False
if test :
    text_list = []
    text_list.append('Bob loves dogs and likes to throw balls for dogs') # topic: dog
    text_list.append('Mary runs and runs and runs all over') # topic: run
    text_list.append('Elly flies... and runs! Then the dog barked.') # topic: ?
    text_list.append('Bug wants a dog and a cat') # topic: ?
    text_list.append('Elly wants two dogs and three cats') # topic: ?
    text_list.append('Why is the dog throwing the cat?') # topic: dog
    print('\n'.join(text_list))
    
    i = 0
    test_courses_dict = dict()
    for line in text_list :
        title = "key"+str(i)
        test_courses_dict[title] = course_data.Course(title, line)
        print(title, ":   ", line)
        i += 1
        
    ids_list = rank_collection("Do dogs like to run?", test_courses_dict)