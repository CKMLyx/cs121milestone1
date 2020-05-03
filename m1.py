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
        doc_token_mapping - dict { doc_id: tok_freq(dict) {tok: tok_freq} }
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
    for word in s:
        if word.isalnum():
            res.append(word.lower())
    stems = []
    for item in res:
        stems.append(PorterStemmer().stem(item))
    return stems

'''
given a json file, tokenizes the contents

TODO: We should also compute the frequency of each token here, store that so
this should return a dictionary {token:frequency, token2:frequency}
'''
def extract_tokens(file): 
    temp = open(file,'r')
    soup = BeautifulSoup(temp,'lxml')
    s = soup.get_text()
    results = tokenize(s.split())

    # compute and map frequency of each token
    token_freq = dict()

    for word in results:
        if word not in token_freq:
            token_freq[word] = 1
        else:
            token_freq[word] += 1

    return token_freq # changed from "results" to token_freq


    

