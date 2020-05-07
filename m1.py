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
    # inverted index structure:
    # inv_ind = {
    #     token : {
    #       doc_id,
    #       tf-idf score (# times word shows up in doc)
    #     }

#Inverted index structure
    #token : list of postings 

'''
REQUIREMENTS
1. Posting on minimum, should have document id, tf-idf score (yes, but might be able to improve?)
2. Sort the posting by doc-id (no)
3. Modularize (yes)
4. Must off load inverted index from main mem to partial index on disk at least 3 times (no)
5. Merge partial indexes at end (no)

'''

'''
Iterates all the files and creates a dictionary where
the key = int
and value = json file name
also builds a set of tokens

Added desc (Doug)
    output:
        mapping           - dict { doc_id: document }
        doc_token_mapping - dict { doc_id: {token : (frequency, tf score)} }
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
                print(doc_id)
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
import json

def extract_tokens(file):
    temp = open(file,'r') 
    temp = json.load(temp)
    soup = BeautifulSoup(temp['content'],'lxml')
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

'''
Build inverted index  
     inverted index structure:
     inv_ind = {
         token : {
           doc_id,
           tf-idf score (# times word shows up in doc)
         }
    }
'''
import math
def build_index():
    res = compute() #Returns mapping, doc_token mapping, and unique tokens
    tokens = res[2] #Unique tokens
    mapping = res[0] #Document id --> document name mapping
    dt_map = res[1] #document id : {token : (freq, tf)} 
    n = len(res[2]) #Iterate for every unique token
    index = dict()
    for token in tokens:
        print("Working on ... " + token)
        token_result = []
        token_count = 0
        '''
        we are building the postings list for token i
        Ex: 
            Loop iterates document ID in range from 0 to number of documents
                On each iteration, we check if the token is in that document
                    If it is, we increment token_count (we need this for idf)
                    Create a temp tuple of the form (doc id, (freq, tf))
                    Append this tuple to the result array 
        '''
        for i in range(len(mapping.keys())): #mapping.keys tells us the number of documents 
            doc_tokens = dt_map[i].keys() #Returns {token : (freq, tf)} and then we get just the tokens
            if token in doc_tokens: #If token exists in document
                token_count += 1 #documents with token counter
                temp = (i,dt_map[i][token]) #Create tuple with (doc id, (freq,tf))
                token_result.append(temp) #Add the tuple to list
        #This loop modifies the postings with the idf score.
        '''
        Now that we have an array that tells us all the documents where token i occurs,
            We iterate this array
                Retrieve the stored tuple (freq, tf)
                Calculate the idf by log2(num of docs / num of docs w/ token)
                Overwrite the intial tuple with (doc id, tf * idf)
        After the loop, append this result to the index dictionary where the structure is
            index = {
                            token: [(doc id, tf-idf), (doc id, tf - idf)...]
            }
        '''
        ind = 0
        for item in token_result:
            doc_id = item[0] #get doc_id
            temp_token = item[1] #(freq,tf) of token
            tf = temp_token[1] #get tf score 
            temp = len(mapping.keys())/token_count #num of docs / num of docs with that token 
            idf = math.log(temp,2) #get idf 
            token_result[ind] = (doc_id,tf * idf) #set to new tuple 
            ind += 1
        token_result = sorted(token_result,key=lambda tup: tup[0])
        index[token] = token_result
    return index

import time
start = time.time()
print(build_index()) #entry point
end = time.time()
print(end - start)







