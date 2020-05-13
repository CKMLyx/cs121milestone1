import os
from nltk.stem.porter import PorterStemmer


def gen_mapping():
    cwd = os.getcwd()
    mapping = {}
    doc_id = 0
    for p, d, f in os.walk(cwd):
        for file in f:
            if '.json' in file:
                mapping[doc_id] = file
                doc_id += 1
    return mapping

mapping = gen_mapping() #Dictionary holds doc_id --> filename mapping


def parse_posting(line):
    res = []
    for i in range(0,len(line),2):
        doc_id = line[i].strip()
        tfidf = line[i+1].strip()
        res.append((doc_id,tfidf))
    return res


def search(query):
    '''
    For each token, retrieve the postings list 
    '''
    search_result = {}
    query_terms = query.split(" ")
    for query in query_terms:
        term = PorterStemmer().stem(query.lower())
        file = open('index.txt','r')
        simple_index = open("simple_index.txt", "r")    # Format: "(word),(line number)\n"
        for line in simple_index:
            line = line.split(",")
            if term == line[0]:
                file.seek(int(line[1].strip())) 
                file.readline() # reads token, essentially getting to next line
                temp_posting = file.readline().strip('\n').split(',') #Get the postings
                temp_posting = parse_posting(temp_posting)
                temp_posting = sorted(temp_posting,key=lambda x:x[1],reverse=True) #Sorts based on tfidf descending
                search_result[term] = temp_posting
                break
        simple_index.close()
        file.close()

    '''
    1. Get list of just doc_id
    NOTE - Idk how to compute intersection of tuples based on first value. 
    Structure: {token: doc_id}
    '''
    doc_id = {}
    for key in search_result.keys():
        temp = set()
        temp_tfidf = []
        for item in search_result[key]:
            temp.add(item[0])
        doc_id[key] = temp
#    '''
#    Find the intersection of postings
#    '''
    if len(search_result.keys()) > 1: #If more than one term
        posting_set = []
        for key in search_result.keys(): #Turn each set into posting
            posting_set.append(doc_id[key])
        search_result = set.intersection(*posting_set) #Compute intersection
    else:
        search_result = doc_id[key]
    return search_result

import time
start = time.time()
res = search('cristina lopes')
end = time.time()
print("Time taken to search index = " + str(end-start))

#Print top 5 files 
counter = 1
for item in res:
    print(mapping[int(item)])
    counter += 1
    if counter > 5:
        break

'''
TODO
-Create an index for our index to speed up search. The majority of the time spent is on searching for the token (priority)
-Order results by tfidf using cosine sim (?)
'''
