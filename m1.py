import nltk
import os
from bs4 import BeautifulSoup
from nltk.stem.porter import PorterStemmer
#Extract tokens from all JSON files
#Build a set of all the tokens found in all the json files
#For each token, iterate from 0 to len(mapping.keys())
    #1. How often is token seen?
    #2. tf-idf of token?

    # Doug
    # 
    # inverted index structure:
    # inv_ind = {
    #     token : {
    #       doc_id,
    #       tf-idf score (# times word shows up in doc)
    #     }
    #
    #
    # }
    
    #

#Inverted index structure
    #token : list of postings 
    
#After repeating this for every single token, we should have a complete inverted-index

'''
Iterates all the files and creates a dictionary where
the key = int
and value = json file name
also builds a set of tokens

Added desc (Doug)
    output:
        mapping           - dict { doc_id: document }
        doc_token_mapping - dict { doc_id: {token : frequency, tf score} }
        unique_tokens     - set (unique tokens)

'''
def compute(): 
    cwd = os.getcwd()
    mapping = {}
    doc_id = 0
    unique_tokens = set()
    doc_token_mapping = dict()
    for p, d, f in os.walk(cwd):
        for file in f:
            if '.json' in file:
                mapping[doc_id] = file
                tokens = extract_tokens(str(p)+'\\'+file)
                doc_token_mapping[doc_id] = tokens
                unique_tokens.update(tokens)
                doc_id += 1
    return mapping, doc_token_mapping, unique_tokens 

'''
Will probably only be called through extract_tokens

Added desc (Doug)
    input:
        s - a list of words found in an HTML file
    output:
        stems - a list of valid (alphanumeric) base/root
                words that have been "cleaned" through 
                the PorterStemmer

'''
def tokenize(s):
    res = []
    p = PorterStemmer()
    for word in s:
        if word.isalnum():
            res.append(p.stem(word))
    return res

'''
given a json file, tokenizes the contents

TODO: We should also compute the frequency of each token here, store that so
this should return a dictionary {token:frequency, token2:frequency}
'''
from collections import Counter 

def extract_tokens(file): 
    temp = open(file,'r')
    soup = BeautifulSoup(temp,'lxml')
    s = soup.get_text()
    results = tokenize(s.split())
    n = len(results)
    # compute and map frequency of each token
    token_freq = Counter(results) #Count frequency

    #Calculate tf score
    final_res = dict()
    for key in token_freq.keys():
        tf = token_freq[key]/n 
        final_res[key] = (token_freq[key],tf) #Ex: Apple: (10, 1.2) where 10 is freq, 1.2 is tf score
    
    return final_res # changed from "results" to token_freq


    
