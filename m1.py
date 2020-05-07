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
dec_values = set()
dec_values.update(range(48,57+1))
dec_values.update(range(65,90+1))
dec_values.update(range(97,122+1))
def tokenize(s):
    res = []
    p = PorterStemmer()
    for word in s:
        if len(word)>1:
            word = p.stem(word)
            val = checkalnum(word)
            if val:
                res.append(word)
            else:
                continue
    return res
def checkalnum(word):
    for i in range(len(word)):
        if ord(word[i]) not in dec_values:
            return False
    return True
'''
given a json file, tokenizes the contents
TODO: We should also compute the frequency of each token here, store that so
this should return a dictionary {token:frequency, token2:frequency}
'''
from collections import Counter
import json

def extract_tokens(file):
    temp = open(file,'r')
    # temp = json.load(temp)
    # soup = BeautifulSoup(temp['content'],'lxml') # this breaks my code because it allows things like făinaru in and i cant encode that
    soup = BeautifulSoup(temp, 'lxml')
    s = soup.get_text()
    results = tokenize(s.split())
    n = len(results)
    # compute and map frequency of each token
    token_freq = Counter(results) #Count frequency
    temp.close()

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

    # Calvin
    MAX_INDEXS = 5000 #Max number of tokens allowed in index before creating partial
    count = 0

    for token in tokens:
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

        # Calvin
        # if 500 or so records then create partial and delete index
        # if more than one partial exist merge them
        count = count + 1
        if count == MAX_INDEXS:
            partialIndex(index)
            index.clear()
            count = 0
    partialIndex(index) # this is for the last set of indexes, i.e. there are 1900 indexes and 400 are left over if we check for 500
    print("Number of unique tokens = " + str(len(tokens)))
    print("Number of documents = " + str(len(mapping.keys())))
    print("Number of tokens in index = " + str(len(index.keys())))
    return index


# Calvin
import re

def saveIndex(filename, index): # saves indexs to files
    f = open(filename, "a")
    for item in index:
        f.write(item)
        f.write("\n")
        f.write(str(index[item]))
        f.write("\n")
        f.write("\n")


def partialIndex(index): # saves partials indexes to files and calls merge
    p1True = os.path.isfile('partial1.txt')
    if p1True or os.path.isfile('index.txt'):
        saveIndex("partial2.txt", index)
        if p1True:
            p1 = getAllIndex("partial1.txt")
            os.remove("partial1.txt")
        else:
            p1 = getAllIndex("index.txt")
            os.remove("index.txt")
        p2 = getAllIndex("partial2.txt")
        os.remove("partial2.txt")
        for walker in p2:
            holder = str(p2[walker]).rstrip().strip("[]")
            mergeIndex(p1, walker, holder)

        saveIndex("index.txt", p1)
    else:
        saveIndex("partial1.txt", index)


def mergeIndex(des, toAddName, index): # if this finds that the index already exist in the first partial index it'll append to that otherwise just add
    if des.__contains__(toAddName):
        info = des[toAddName].strip("[]")
        info = re.split(r"(?<![0-9])[.,](?![0-9])", info)
        for i in range(len(info)):
            info[i] = info[i].strip()
        info.append(index)
        info = sorted(info)
        result = "["
        for temp in range(len(info)):
            result += info[temp]
            if temp + 1 < len(info):
                result += ", "
        result += "]"
        des[toAddName] = result
    else:
        des[toAddName] = "[" + index + "]"


def getAllIndex(file): # grabs all the indexes from a partial index file
    indexes = {}
    with open(file) as f:
        for line in f:
            if line != '\n':
                holder = line.rstrip()
                line = f.__next__()
                indexes[holder] = line.rstrip()
    return indexes



import time
start = time.time()
build_index()
end = time.time()
print(end - start)
