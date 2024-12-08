import re

import numpy as np
import lda

import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize

import word_helper

# grab stop words
stop_words = stopwords.words('english')
#stop_words.extend(['from', 'subject', 're', 'edu', 'use'])

class Topic :
    def __init__(self, title, word_list):
        self.title = title
        self.word_list = word_list
        
    def __str__(self):
        return (f"Topic {self.title}: " +','.join(self.word_list))
        
#loads topics into data objects from file using 
#ReadTopicsFromFile(), data objects empty if issue reading files
#   in: N/A
#   out: success (Boolean)
def LoadTopics() :
    global topics_list    
    
    success = False
    
    Empty() # be sure to empty the data structures first
    ReadTopicsFromFile()
    
    # check that at least 1 topic with 1 word was loaded
    if (len(topics_list) > 0) and (topics_list[0] != None) and (len(topics_list[0].word_list) > 0) :
        success = True
    
    return success
    
#reads topic data from file and stores directly in data objects
#   in: N/A
#   out: N/A   
def ReadTopicsFromFile() :
    global topics_list
    
    try :
        with open(topics_filePath, "r") as f:
            i = 0
            lines = f.readlines()
        
            # cycle through topic lines
            while i < len(lines) :
            
                # check for non-empty line
                if not lines[i].isspace() :
                    # topics list
                    # each line is a new key, value pair
                    # format: "title" + ":" + "list of comma separated topic strings"
                    split_line = lines[i].split(':')
                    if len(split_line) >= 2 :
                        title = split_line[0].strip()
                        word_list = split_line[1].strip().split(',')
                        topics_list.append(Topic(title, word_list))
            
                # increment line
                i += 1
            
    except Exception as e:
        print("Exception in topic_miner.py:", e)
        Empty()
    
#write topics data to file
#   in: N/A
#   out: N/A
def WriteTopicsToFile() :
    global topics_list
    
    with open(topics_filePath, "w") as f:
        # cycle through topics list to write each title:word_list pair separate
        for t in topics_list :
            f.writelines(t.title + ':' + ','.join(t.word_list)+'\n')
            
   
#empties out the data structures for re-writing
#   in: N/A
#   out: N/A
def Empty() :
    global topics_list    
    topics_list = []

# using LDA, mine topics from list of strings
#   in: text_list (list of string), num_topics (int), n_top_words (int)
#   out: N/A, topics saved internally
def Mine_Topics_lda(text_list, num_topics = 20, n_top_words = 8) :
    global topics_list
    Empty()
    
    ps = None#PorterStemmer() # messed up test case! DO NOT USE
    
    vocab_dict = dict()
    
    # cycle through text blobs
    num_texts = len(text_list)
    for i in range(num_texts) :
        print("  mining text" + str(i+1), end='\r')
        text_blob = text_list[i]
        for word in text_blob.split() : # in word_tokenize(text_blob) : # added random blank to vocab, so don't use
            # clean up word
            clean_word = word_helper.CleanWord(word, ps)
            
            # skip stop words
            if (clean_word not in stop_words) and (len(clean_word) > 2) :
                
                # check is word is already in vocabulary
                if (clean_word not in vocab_dict.keys()) :
                    # create zeros array of num of texts
                    vocab_dict[clean_word] = np.zeros(num_texts, int)
                    
                # word is entered into or already exists in vocabulary
                # increment word count
                vocab_dict[clean_word][i] = vocab_dict[clean_word][i] + 1
                #print("@"+str(i), clean_word, str(vocab_dict[clean_word][i]))
            else :
                ignore_this = 3
                #print("stop", clean_word)
                
    # setup X matrix
    vocab_list = list(vocab_dict.keys()) # use list to ensure order
    #print(vocab_list)
    X = np.zeros((num_texts, len(vocab_list)), int)
    #print(X.shape)
    for j in range(len(vocab_list)) :
        X[:,j] = vocab_dict[vocab_list[j]]
    #print(X)

    # LDA
    model = lda.LDA(n_topics=num_topics, n_iter=1500, random_state=1)
    model.fit(X)  # model.fit_transform(X) is also available
    topic_word = model.topic_word_  # model.components_ also works
    #print(topic_word)
    for i, topic_dist in enumerate(topic_word):
        topic_words = np.array(vocab_list)[np.argsort(topic_dist)][:-n_top_words-1:-1]
        topics_list.append(Topic(str(i), topic_words))
        #print('Topic {}: {}'.format(i, ' '.join(topic_words)))
        

def Mine_Topics_NormProb(text_list, doc_index_list,doc_title_list = []) :
    global topics_list
    Empty()
    
    vocab_dict = dict()
    
    # cycle through text blobs
    num_texts = len(text_list)
    for i in range(num_texts) :
        print("  mining text" + str(i+1), end='\r')
        text_blob = text_list[i]
        for word in text_blob.split() : # in word_tokenize(text_blob) : # added random blank to vocab, so don't use
            # clean up word
            clean_word = word_helper.CleanWord(word)
            
            # skip stop words
            if (clean_word not in stop_words) :
                
                # check is word is already in vocabulary
                if (clean_word not in vocab_dict.keys()) :
                    # create zeros array of num of texts
                    vocab_dict[clean_word] = np.zeros(num_texts, int)
                    
                # word is entered into or already exists in vocabulary
                # increment word count
                vocab_dict[clean_word][i] = vocab_dict[clean_word][i] + 1
                #print("@"+str(i), clean_word, str(vocab_dict[clean_word][i]))
            else :
                ignore_this = 3
                #print("stop", clean_word)
                
    # setup X matrix
    vocab_list = list(vocab_dict.keys()) # use list to ensure order
    #print(vocab_list)
    X = np.zeros((num_texts, len(vocab_list)), int)
    #print(X.shape)
    for j in range(len(vocab_list)) :
        X[:,j] = vocab_dict[vocab_list[j]]
    #print(X)
    
    # Collection Probabilities: sum(X_cols) / sum(X) -> 1d array length num_vocab
    # for each document d, 
    #    Document Word Probabilities: X_row_d / sum(X_row_d) -> 1d array length num_vocab
    #    Normalized Doc Prob: Document Word Probabilities / Collection Probabilities -> 1d array length num_vocab
    #    sort by prob, pick top word
    n_top_words = 3
    p_C = np.sum(X, axis = 0)/np.sum(X)
    #print("p_C", p_C)
    for i in doc_index_list :
        p_d = X[i,:] / np.sum(X[i,:])
        #print("p_d", p_d)
        #if len(doc_title_list) > 0 :
            #print(doc_title_list[i])
        #print(np.argsort(p_d))
        #print(np.argsort(p_d)[-n_top_words:])
        #print(np.argsort(p_d)[:-n_top_words-1:-1])        
        top_words = np.array(vocab_list)[np.argsort(p_d)[:-n_top_words-1:-1]]
        topics_list.append(Topic(str(i), top_words))
        #print("top words:", top_words)


# mine documents for topics and save results internally
#   in: (dictionary) [key: original course title (string), value: clean course description (list of string)]
#   out: N/A, topics saved internally
def Mine_Topics(clean_docs_dict) :
    courses_text_title_for_mining = []
    for key in clean_docs_dict.keys() :
        courses_text_title_for_mining.append(' '.join(word_helper.CleanWordString(key)))
        courses_text_title_for_mining.append(' '.join(clean_docs_dict[key]))
    
    # run topic mining
    Mine_Topics_lda(courses_text_title_for_mining, 12, 4)

        
### MAIN ###
topics_filePath = "topics.txt"
topics_list = []


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
    print(text_list)        
    doc_index_list = [0, 1, 2, 3]

    #Mine_Topics_lda(text_list, 10, 4)        
    Mine_Topics_NormProb(text_list, doc_index_list)
