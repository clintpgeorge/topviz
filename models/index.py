# coding: utf8

import glob
import csv
import unicodedata
import re
import numpy as np
from os.path import isfile, join, split, splitext
from collections import defaultdict

def slugify(value):
    """
    Normalizes string, removes non-alpha characters,
    and converts spaces to underscores.
    http://stackoverflow.com/questions/295135/turn-a-string-into-a-valid-filename-in-python
    """
    value = unicode(value)
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(re.sub('[^\w\s-]', '', value).strip())
    return unicode(re.sub('[-\s]+', '_', value))

wiki_url = "http://en.wikipedia.org/wiki/"
index_name = "Whales-Categories"
root_dir = join(request.folder, 'private', 'data')
pages_dir = join(root_dir, 'pages')
index_file = "%s.csv" % index_name
ldac_file = "%s.ldac" % index_name
vocab_file = "%s.ldac.vocab" % index_name
lda_theta_file = "%s.lda.theta" % index_name
lda_beta_file = "%s.lda.beta" % index_name
lda_topic_labels_file = "%s.lda.topic.labels" % index_name
lda_doc_word_topics_file = "%s.lda.doc.word.topics" % index_name
MIN_DISPLAY_WORD_PROB_VALUE = 1e-3 # We ignore the words with too small probabilities
MIN_DISPLAY_TOPIC_PROB_VALUE = 1e-2;

lda_theta = np.loadtxt(join(root_dir, lda_theta_file))
lda_beta = np.loadtxt(join(root_dir, lda_beta_file))
lda_topic_labels = []
with open(join(root_dir, lda_topic_labels_file)) as fp:
    for line in fp:
        lda_topic_labels.append(line.strip())


vocab = []
vocabnames = defaultdict(str)
vocab_count = 0 # V: the vocab size
with open(join(root_dir, vocab_file)) as fp:
    for line in fp:
        vocabnames[vocab_count] = line.strip()
        vocab_count += 1
        vocab.append(line.strip())

'''
doc_word_topics = []
with open(join(root_dir, lda_doc_word_topics_file)) as fp:
    for line in fp:
        doc = []
        for w in line.strip().split():
            wc =  [int(e) for e in w.split(":")]
            doc.append({"word":vocabnames[wc[0]], "wid":wc[0], "tid":wc[1]})
        doc_word_topics.append(doc)

'''
documents = []
with open(join(root_dir, ldac_file)) as fp:
    for line in fp:
        vc = line.strip().split()
        if len(vc) > 2:
            doc = defaultdict(int)
            for ei in vc[1:]:
                vocab_str = [int(e) for e in ei.split(":")]
                doc[vocabnames[vocab_str[0]]] = vocab_str[1]
            documents.append(doc)

doc_nodes = []
with open(join(root_dir, ldac_file)) as fp:
    for line in fp:
        vc = line.strip().split()
        if len(vc) > 2:
            doc = list()
            for ei in vc[1:]:
                vocab_str = [int(e) for e in ei.split(":")]
                doc.append({"name":vocabnames[vocab_str[0]], "size":vocab_str[1]})
            doc_nodes.append(doc)

file_details = []
categories = []
nodes = []
links = []
nodeids = defaultdict(int)

with open(join(root_dir, index_file), 'rb') as csvfile:
    dr = csv.DictReader(csvfile, delimiter=';')
    count = 0
    # Adds the root node
    nodes.append({"name":index_name,"group":0,"size":3})
    nodeids[index_name] = count
    count += 1
    docid = 0
    for fd in dr:
        file_details.append(fd)
        # Adds categories to the graph
        if fd["category"] not in categories:
            categories.append(fd["category"])
            nodes.append({"name":fd["category"],"group":1,"size":2})
            nodeids[fd["category"]] = count
            count += 1
            links.append({"source":nodeids[index_name],
                          "target":nodeids[fd["category"]],
                          "value":8,
                          "name":"sub-category"})
        # Adds pages to the graph
        nodes.append({"name":fd["title"],"group":2,"size":1,"docid":docid})
        nodeids[fd["title"]] = count
        count += 1
        docid += 1
        links.append({"source":nodeids[fd["category"]],
                      "target":nodeids[fd["title"]],
                      "value":4,
                      "name":"page"})

# nodes = [{"name":"Myriel","group":1},]
# links = [{"source":1,"target":10,"value":100},]

wikidata = {"nodes":nodes, "links": links}


# bubbledata = {
#  "name": "flare",
#  "children": [
#     {
#      "name": "tf",
#      "children": [
#       {"name": "AgglomerativeCluster", "size": 1},
#       {"name": "CommunityStructure", "size": 2},
#       {"name": "HierarchicalCluster", "size": 3},
#       {"name": "MergeEdge", "size": 1}
#      ]
#     },
#     {
#      "name": "tfidf",
#      "children": [
#       {"name": "BetweennessCentrality", "size": 3},
#       {"name": "LinkDistance", "size": 2},
#       {"name": "MaxFlowMinCut", "size": 2},
#       {"name": "ShortestPaths", "size": 7},
#       {"name": "SpanningTree", "size": 1}
#      ]
#     },
# ]
# }

bubbledata = {
    "name": "tf",
    "children": [
        {"name": "BetweennessCentrality", "size": 3},
        {"name": "LinkDistance", "size": 2},
        {"name": "MaxFlowMinCut", "size": 2},
        {"name": "ShortestPaths", "size": 7},
        {"name": "SpanningTree", "size": 1}
     ]
}
