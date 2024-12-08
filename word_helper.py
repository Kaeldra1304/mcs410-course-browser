import re
import nltk
nltk.download('words')
from nltk.corpus import words
from nltk.stem import PorterStemmer

# returns a stemmed word from the nltk corpus 
# or nothing if word is not easily stemmable
def FindValidStemmedWord(w) :
    # returns a stemmed word if discovers a valid one in nltk corpus
    if w[-1:] == 's':
        # word is not in dictionary
        # possible plural word, check with deplural word
        if w[:-1] in words.words() :
            return w[:-1]
        elif w[:-2] in words.words() :
            return w[:-2]
    elif w[-2:] == 'ed':
        # word is not in dictionary
        # possible past tense word, check with stem verb
        if w[:-1] in words.words() :
            return w[:-1]
        elif w[:-2] in words.words() :
            return w[:-2]
    elif w[-3:] == 'ing':
        # word is not in dictionary
        # possible present tense word, check with stem verb
        if w[:-3] in words.words() :
            return w[:-3]
        elif w[:-3]+'e' in words.words() :
            return w[:-3]+'e'

    return ""
        
# clean word by removing non-alphabetical characters and stemming if possible
#   in: word (string)
#   out: clean word (string)
def CleanWord(word, ps = None) :
    # remove non-alphabetical characters
    clean_word = re.sub(r'[^A-Za-z]+', '', word.lower())
    
    # stemming words
    if ps is not None : 
        clean_word = ps.stem(clean_word)
    else :        
        possible_stem_word = FindValidStemmedWord(clean_word)
        if possible_stem_word != "" :
            #print("stemming")
            #print(clean_word)
            clean_word = possible_stem_word
            #print(clean_word)
        
    return clean_word
        
# clean string of words, optional delimiter specification
#   in: word_str (string), delimiter (string)
#   out: clean words (list of string)
def CleanWordString(word_str, delimiter = ' ') :
    clean_word_list = []
        
    # cycle through words in string,
    # clean, then append to list
    for word in word_str.split(delimiter) :
        # clean & stem the word
        clean_word = CleanWord(word)
        if not clean_word.isspace() and clean_word != "" :
            # append to clean document list
            clean_word_list.append(clean_word)
    
    return clean_word_list    