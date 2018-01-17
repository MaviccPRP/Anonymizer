#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import sys
import os
import codecs


originalfolder = "dgdsgagasgasga"

minusonedict = {}
minustwodict = {}

town_suffixes = {}
street_suffixes = {}
towns = {}
streets = {}
names = {}
countrycodes = {".de":True, ".org":True, ".com":True, ".net":True, ".info":True, ".at":True, ".ch":True, ".fr":True}
purgeUrls = False
purgeEmails = False
purgeBlackList = False
blacklist = {}
removepunctuation = False

if "-o" in sys.argv:
    originalfolder = sys.argv[sys.argv.index("-o")+1]
if not os.path.isdir(originalfolder):
    print "Please specify valid parent folder containing sub-folders with target documents! ... -o parentfolder ..."
    sys.exit()

if "-ss" in sys.argv:
    streetsuffixfile = codecs.open(sys.argv[sys.argv.index("-ss")+1], "r", encoding="utf-8")
    line = streetsuffixfile.readline()
    while len(line) > 2:
        splitlist = line.split()
        street_suffixes[splitlist[0]] = True
        line = streetsuffixfile.readline()
    streetsuffixfile.close()
if "-ts" in sys.argv:
    townsuffixfile = codecs.open(sys.argv[sys.argv.index("-ts")+1], "r", encoding="utf-8")
    line = townsuffixfile.readline()
    while len(line) > 2:
        splitlist = line.split()
        town_suffixes[splitlist[0]] = True
        line = townsuffixfile.readline()
    townsuffixfile.close()
if "-s" in sys.argv:
    streetfile = codecs.open(sys.argv[sys.argv.index("-s")+1], "r", encoding="utf-8")
    line = streetfile.readline()
    while len(line) > 2:
        streets[line.rstrip()] = True
        line = streetfile.readline()
    streetfile.close()
if "-t" in sys.argv:
    townfile = codecs.open(sys.argv[sys.argv.index("-t")+1], "r", encoding="utf-8")
    line = townfile.readline()
    while len(line) > 2:
        towns[line.rstrip()] = True
        line = townfile.readline()
    townfile.close()
if "-n" in sys.argv:
    namefile = codecs.open(sys.argv[sys.argv.index("-n")+1], "r", encoding="utf-8")
    line = namefile.readline()
    while len(line) > 2:
        names[line.rstrip()] = True
        line = namefile.readline()
    namefile.close()
if "-u" in sys.argv:
    purgeUrls = True
if "-e" in sys.argv:
    purgeEmails = True
if "-b" in sys.argv:
    purgeBlackList = True
    blacklistfile = codecs.open(sys.argv[sys.argv.index("-b")+1], "r", encoding="utf-8")
    line = blacklistfile.readline()
    while len(line) > 2:
        names[line.rstrip()] = True
        line = blacklistfile.readline()
    blacklistfile.close()
if "-p" in sys.argv:
    removepunctuation = True




keys = ["rel_amount_of_documents_leader_occurs_in", "distinct_words_predicted", "positive_predictive_value"]
thresholds = {"rel_amount_of_documents_leader_occurs_in":0.0, "distinct_words_predicted":1, "positive_predictive_value":0.3}

def readLeadingWords(path):
    dict = {}
    file = codecs.open(path, "r", encoding="utf-8")
    file.readline()
    line = file.readline()
    while len(line) > 0:
        splitlist = line[:-1].split()
        predictor = splitlist[0]
        performance = [float(splitlist[1]), int(splitlist[2]), float(splitlist[3])]
        if all([performance[j] >= thresholds[keys[j]] for j in range(0, len(thresholds))]):
            dict[predictor] = performance
        line = file.readline()
    file.close()
    return dict

for i in range(1, len(sys.argv)):
    if sys.argv[i] == "-c":
        thresholds["rel_amount_of_documents_leader_occurs_in"] = float(sys.argv[i+1])
        thresholds["distinct_words_predicted"] = int(sys.argv[i+2])
        thresholds["positive_predictive_value"] = float(sys.argv[i+3])
    elif sys.argv[i] == "-l":
        minusonedict = readLeadingWords(sys.argv[i+1])
        minustwodict = readLeadingWords(sys.argv[i+2])
        
        
print "Thresholds:", thresholds

if max(len(minusonedict), len(minustwodict)) == 0:
    print "Please specify your leading word list files properly!"
    sys.exit() 
print "Using ", len(minusonedict), "-1 leading words."
print "Using ", len(minustwodict), "-2 leading words."



def hasStreetSuffix(word):
    return any([word.endswith(street_suffix) == street_suffix for street_suffix in street_suffixes])
def hasTownSuffix(word):
    return any([word.endswith(town_suffix) == town_suffix for town_suffix in town_suffixes])
def isStreet(word, minustwoleader, minusoneleader):
    return word in streets or " ".join([minusoneleader, word]) in streets or " ".join([minustwoleader, minusoneleader, word]) in streets
def isTown(word, minustwoleader, minusoneleader):
    return word in towns or " ".join([minusoneleader, word]) in towns or " ".join([minustwoleader, minusoneleader, word]) in towns
def isName(word):
    return word in names
def isUrl(word):
    return "www." in word or "http" in word or word[-3:] in countrycodes
def isEmail(word):
    return "@" in word


print "Expecting target documents to be located in the sub-folders of " + originalfolder
#for p in [1,2]:
for item in os.listdir(originalfolder):
    if os.path.isdir((originalfolder + "/" + item)):
        print "Sub-folder " + item
        for item2 in os.listdir(originalfolder + "/" + item):
            if "ano" not in item2:
                infile = codecs.open(originalfolder + "/" + item + "/" + item2, "r", encoding="utf-8")
                content = infile.read()
                if removepunctuation:
                    wordlist = [word for word in [preword.strip(".,;:'`!?\"") for preword in content.split()] if len(word) > 0]
                else:
                    wordlist = [word for word in content.split() if len(word) > 0]
                crossoutlist = []
                if hasStreetSuffix(wordlist[0]) or hasTownSuffix(wordlist[0]) or isStreet(wordlist[0], "", "") or isTown(wordlist[0], "", "") or isName(wordlist[0]):
                    crossoutlist.append(0)
                elif purgeUrls and isUrl(wordlist[0]):
                    crossoutlist.append(0)
                elif purgeEmails and isEmail(wordlist[0]):
                    crossoutlist.append(0)
                elif wordlist[0] in blacklist:
                    crossoutlist.append(0)
                if wordlist[1] in minusonedict:
                    crossoutlist.append(1)
                elif hasStreetSuffix(wordlist[1]) or hasTownSuffix(wordlist[1]) or isStreet(wordlist[1], "", wordlist[0]) or isTown(wordlist[1], "", wordlist[0]) or isName(wordlist[1]):
                    crossoutlist.append(1)
                elif purgeUrls and isUrl(wordlist[1]):
                    crossoutlist.append(1)
                elif purgeEmails and isEmail(wordlist[1]):
                    crossoutlist.append(1)
                elif wordlist[1] in blacklist:
                    crossoutlist.append(1)
                for i in range(2, len(wordlist)):
                    if wordlist[i-1] in minusonedict or wordlist[i-2] in minustwodict:
                        crossoutlist.append(i)
                    elif hasStreetSuffix(wordlist[i]) or hasTownSuffix(wordlist[i]) or isStreet(wordlist[i], wordlist[i-2], wordlist[i-1]) or isTown(wordlist[i], wordlist[i-2], wordlist[i-1]) or isName(wordlist[i]):
                        crossoutlist.append(i)
                    elif purgeUrls and isUrl(wordlist[i]):
                        crossoutlist.append(i)
                    elif purgeEmails and isEmail(wordlist[i]):
                        crossoutlist.append(i)
                    elif wordlist[i] in blacklist:
                        crossoutlist.append(i)
                
                infile.close()
                for index in crossoutlist:
                    wordlist[index] = "".join(['X' for j in range(0, len(wordlist[index]))])
                outfile = codecs.open(originalfolder + "/" + item + "/" + item2 + ".ano" + "_-p_" + str(removepunctuation), "w", encoding="utf-8")
                outfile.write(" ".join([word for word in wordlist]))
                outfile.close()