#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys,math
from collections import defaultdict
import xml.etree.ElementTree as ET

n = 46972 #total number of file in file list
idf = lambda k: math.log10(n) - math.log10(k)
vocab = {}


class raw_query:
    def __init__(self, topic):
        self.title = topic.find('title').text
        self.num = topic.find('number').text[-3:]
        self.question = topic.find('question').text.strip().replace(u'、', ' ').replace(u'。', ' ').split()
        self.narrative = topic.find('narrative').text.strip().replace(u'、', ' ').replace(u'。', ' ').split()
        self.concepts = topic.find('concepts').text.strip().replace(u'、', ' ').replace(u'。', ' ').split()

class Inverted_file:
    def __init__(self, inv_file):
        
        self.bigram = {}
        self.doc = defaultdict(dict)
        for line in inv_file:
            item = line.split()
            if len(item) == 3:
                bigram = '%s_%s' % (item[0], item[1])
                bigram_idf = idf(int(item[2]))
                self.bigram[bigram] = {'idf': bigram_idf, 'score': {}}
            else:                       
                (doc_id, tf) = line.split()
                self.doc[doc_id][bigram] = int(tf) * self.bigram[bigram]['idf']
        self.vector_len = { doc_id : (sum(map(lambda x: x**2, self.doc[doc_id].values())) ** 0.5) for doc_id in self.doc}


def deal_query(query, inverted_file):
    sentence_list = query.question + query.narrative + query.concepts

    #print map(lambda x: vocab['bigram'][x], word_list)
    combine(sentence_list) #all the bigram from the list
    

def combine(sentence_list):

    reload(sys)
    sys.setdefaultencoding('utf8')
    with open('model/vocab.all', 'r') as file:
        print 'Reading vocab.all...'
        tmp = map(str.strip, file.readlines())
        vocab = {word.strip().encode("utf-8"): line for line, word in enumerate(tmp)}
        print 'End reading'
    bigrams = []
    for sentence in sentence_list:
        for i in range(len(sentence)-1):
            if vocab.has_key(str(sentence[i]).encode("utf-8")) and vocab.has_key(str(sentence[i+1]).encode("utf-8")):
                bigrams.append('%s_%s' % (vocab[sentence[i].encode("utf-8")], vocab[sentence[i+1].encode("utf-8")]))
                bigrams.append('%s_-1' % (vocab[sentence[i].encode("utf-8")]))
    return bigrams
def main():

    with open('model/file-list', 'r') as file:
        print 'Reading file-list...'
        f_list = file.readlines()
        n = len(f_list)
        file_list = map(str.strip, f_list)
        print 'End reading'
    with open('model/inverted-file','r') as file:
        print 'Reading inverted-file...'
        #inverted_file = Inverted_file(file) 
        print 'End reading'

    tree = ET.parse('query/query-train.xml')
    root = tree.getroot()
    query_list = [ raw_query(RawQuery) for RawQuery in root.findall('topic') ]
    inverted_file = ''

    with open('ranking_list', 'w') as ranked_list:
        for query in query_list:
            print 'processing query %s...' % (query.num)
            deal_query(query, inverted_file)


    return 0

if __name__ == '__main__':
    main()
