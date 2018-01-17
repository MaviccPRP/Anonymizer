#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import sys
import os
import codecs
import re
from operator import itemgetter


pairedletterfolder = sys.argv[1]
removepunctuation = False
if "-p" in sys.argv:
    removepunctuation = True

contents = {}
crossedDict = {}



encodings = ['utf-8', 'windows-1250', 'windows-1252']

predictionstats = {}
occDict = {}
crossCounts = {}


def readDocument(letternumber, type):
    content = ""
    infile = codecs.open(letterpaths[letternumber][type], 'r', encoding="utf-8")
    content=infile.read()
    #contentoriginal = "".join([c if c not in "\n\t\r" and c not in u'\xa0' else " " for c in contentoriginal]) #u' ßÄÖÜäöü*1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ.,:;+-'
    #contentoriginalwordlist = [word for word in contentoriginal.split(" ") if len(word) > 0]
    if removepunctuation:
        contentwordlist = [word for word in [preword.strip(".,;:'`!?\"") for preword in content.split()] if len(word) > 0]
    else:
        contentwordlist = [word for word in content.split() if len(word) > 0]
    if letternumber not in contents:
        contents[letternumber] = {}
    contents[letternumber][type] = contentwordlist
    infile.close()

 
print "Reading documents..."
letterpaths = {}
for item in os.listdir(pairedletterfolder):
    letternumber = item.split("_")[0]
    if letternumber not in letterpaths:
        letterpaths[letternumber] = {}
    if not "anony" in item:
        letterpaths[letternumber]["original"] = pairedletterfolder + "/" + item
        readDocument(letternumber, "original")
    else:
        letterpaths[letternumber]["anonymous"] = pairedletterfolder + "/" + item
        readDocument(letternumber, "anonymous")

print "Analyzing content..."
for letternumber in contents:
    if letternumber not in crossedDict:
        crossedDict[letternumber] = {"bag_of_crossed_words":set([]), "context_by_crossed_words":{}}
        origset = set(contents[letternumber]["original"])
        crossedDict[letternumber]["bag_of_crossed_words"] = set([word for word in origset if contents[letternumber]["original"].count(word) > contents[letternumber]["anonymous"].count(word)])
        for word in crossedDict[letternumber]["bag_of_crossed_words"]:
            occurrences = [i for i in range(0, len(contents[letternumber]["original"])) if contents[letternumber]["original"][i] == word] # if there weren't dangerous differences between orig & anonymous letters, one could require: and ("XX" in contents[letternumber]["anonymous"][i] or set([char for char in contents[letternumber]["anonymous"][i]]) == set(['X']))
            leadingcontexts = [contents[letternumber]["original"][occ-1] for occ in occurrences if occ >= 2] # and len(contents[letternumber]["original"][occ-1]) >= 2 else None
            preleadingcontexts = [contents[letternumber]["original"][occ-2] for occ in occurrences if occ >= 2] #  and len(contents[letternumber]["original"][occ-2]) >= 2 else None
            crossedDict[letternumber]["context_by_crossed_words"][word] = {1:leadingcontexts, 2:preleadingcontexts}
        for word in set(contents[letternumber]["original"]):
            if word not in occDict:
                occDict[word] = 0
            occDict[word] += contents[letternumber]["original"].count(word)
            if word not in crossCounts:
                crossCounts[word] = 0
            crossCounts[word] += max(0, contents[letternumber]["original"].count(word) - contents[letternumber]["anonymous"].count(word))



finalleadingcontexts = set([context for letternumber in crossedDict for word in crossedDict[letternumber]["context_by_crossed_words"]  for context in crossedDict[letternumber]["context_by_crossed_words"][word][1]])
finalpreleadingcontexts = set([context for letternumber in crossedDict for word in crossedDict[letternumber]["context_by_crossed_words"]  for context in crossedDict[letternumber]["context_by_crossed_words"][word][2]])


print "Writing", len(crossCounts), "distinct X-ed out words to", sys.argv[1].rsplit("/", 1)[0] + "/blacklist.txt ..."
xedoutoutfile = codecs.open(sys.argv[1].rsplit("/", 1)[0] + "/blacklist.txt", "w", encoding="utf-8")
for word in crossCounts:
    if float(crossCounts[word])/occDict[word] > 0:
        xedoutoutfile.write(word + "\t" + str(float(crossCounts[word])/occDict[word]) + "\n")
xedoutoutfile.close()


print "Writing leading words (predictors)..."
for l in [1, 2]:
    outfile = codecs.open(sys.argv[1].rsplit("/", 1)[0] + "/X_predictors_" + str(l) + ".txt", "w", encoding="utf-8")
    outfile.write("context_leading_1_word_ahead\trel_amount_of_documents\tdistinct_words_predicted\tpositive_predictive_value\n")
    contextPowers = []
    for context in [finalleadingcontexts, finalpreleadingcontexts][l-1]:
        predictedwords = []
        letters = []
        for letternumber in crossedDict:
            found = False
            for word in crossedDict[letternumber]["context_by_crossed_words"]:
                for number in range(0, crossedDict[letternumber]["context_by_crossed_words"][word][l].count(context)):
                    predictedwords.append(word)
                    found = True
            if found == True:
                letters.append(letternumber)
        power = 1.0*len(predictedwords)/occDict[context]
        contextPowers.append((len(set(letters)), context, len(set(predictedwords)), power))
        outfile.write(context + "\t" + str(1.0*len(set(letters))/len(crossedDict)) + "\t" + str(len(set(predictedwords))) + "\t" + str(power) + "\n")
    outfile.close()
    print str(len(contextPowers)) + " '-" + str(l) + " leading' words written to " + sys.argv[1].rsplit("/", 1)[0] + "/X_predictors_" + str(l) + ".txt"

