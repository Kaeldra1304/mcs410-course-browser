import requests
import re
import nltk
nltk.download('words')
from nltk.corpus import words

import io
from PyPDF2 import PdfReader

import word_helper

# checks if word is valid according to nltk corpus
#   in: w (string)
#   out: valid_word (Boolean)
def CheckWord(w) :
    valid_word = True
        
    w = w.lower()
    w = re.sub(r'[^A-Za-z]+', '', w)
    
    if len(w) == 0 :
        # possibly white-space or punctuation only word that got removed
        valid_word = False
    elif len(w) == 1 and w != 'a' :
        # single letter word that isn't 'a'
        valid_word = False
    elif w in words.words() :
        # word is in dictionary
        valid_word = True
    elif word_helper.FindValidStemmedWord(w) != "":
        # valid stemmed word was found
        valid_word = True       
    else :
        # word is not in dictionary, not a plural/past tense/present tense word
        valid_word = False
        
    return valid_word

# tries to remove extra spaces, an issue caused by reading extracting pdf files
#   in: pdf_content (string)
#   out: clean_pdf_content (string)
def CleanUpSpaces(pdf_content) :
    clean_pdf_content = ""
    
    split_pdf_content = re.split(r'(\s)', pdf_content)
    #print(split_pdf_content)
    #print("CleanUpSpaces doc length:", len(split_pdf_content))
    
    j = 2
    while j < len(split_pdf_content) :
        # grab three segment chunk
        w_2 = split_pdf_content[j-2]
        w_1 = split_pdf_content[j-1]
        w = split_pdf_content[j]
        
        # check for specific pattern
        # "word [space] word" 
        # where at least one word is not valid 
        # and the combination of the two words is valid
        if re.search(r'\s', w_1) and ((not CheckWord(w_2)) or (not CheckWord(w))) and CheckWord(w_2+w) :
            # add the combination to the cleaned pdf without space
            clean_pdf_content = clean_pdf_content + w_2 + w
            j = j + 3 # skip ahead to next 3 segment chunk
        else :
            # add the most previous segment
            clean_pdf_content = clean_pdf_content + w_2 
            # increment j to reprocess again
            j = j + 1
        
        # check for end of file after j has been updated
        if j >= len(split_pdf_content) : 
            i = j - 2
            while i < len(split_pdf_content) :
                clean_pdf_content = clean_pdf_content + split_pdf_content[i]
                i = i + 1
                
        #if j % 100 < 2 : print("@", j)
                        
    return clean_pdf_content

# parses the pdf file located at file url for a course description text blob
# and cleans it up using CleanUpSpaces"
#   in: file_url (string)
#   out: course_description (string)
def ParsePDFFile_CourseDescription(file_url, debug = False) :
    course_description = ""
    
    # grab all file contents
    #print("START FILE")
    pdf_content = ""
    try :
        response = requests.get(file_url)
        with io.BytesIO(response.content) as f:
            #for line in f.readlines() :
            #    if "Course Description" in str(line) :
            #        print(line)
                            
            #print(f.readlines())
                        
            # actual code
            pdf = PdfReader(f)
            pdf_content = ""
            for page in pdf.pages :
                pdf_content = pdf_content + page.extract_text()
                
            if debug :
                print("START FILE")
                print(pdf_content)
                print("END FILE")
    except Exception as e:
        #print("!!! Couldn't read pdf file !!!")
        print(e)
    #print("END FILE")
    #print()
                    
    # clean pdf file
    #if "Data Mining Capstone" in pdf_content :
    #pdf_content = CleanUpSpaces(pdf_content)
    #print("START CLEAN FILE")
    #print(pdf_content)
    #print("END CLEAN FILE")
                        
    if "Description" in pdf_content :
        # extract course description
        if debug : print("START DESCRIPTION")
        #DEBUG: print(re.sub(r'\n', "\n~~~~~~~~~~~~~~~~~~~~\n", pdf_content))
        (start1, end1) = re.search('Description', pdf_content).span()
        #if debug : print(end1)
        idx_end = len(pdf_content) - 1
        for end_str in ['Course Goals', 'Course Prerequisite', 'Course Outline', 'Prerequisite', 'Note:', 'Course Objectives', 'Textbook'] :
            if end_str in pdf_content :
                (start, end) = re.search(end_str, pdf_content).span()
                if (start > end1) and (start < idx_end) : idx_end = start
                #if debug : print(idx_end)
        
        # final end index found, grab course description        
        pdf_description = pdf_content[end1:idx_end]
        pdf_description = re.sub(r'\s', " ", pdf_description)
        pdf_description = CleanUpSpaces(pdf_description)
        if debug : print('\n'+pdf_description+'\n')
        course_description = pdf_description
        if debug : print("END DESCRIPTION")
                
    return course_description
    
### MAIN ###
#print(ParsePDFFile_CourseDescription("https://ws.engr.illinois.edu/sitemanager/getfile.asp?id=506", True))