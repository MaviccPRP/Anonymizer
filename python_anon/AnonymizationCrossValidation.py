#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import sys
import os
import codecs
import random
import numpy
import time

demaskingthresholds = [100] # default: no demasking (value = 100 is never reached)

wordsbyid = {} # index of (redundant) word occurrences

priorminusonedict = {}
priorminustwodict = {}

crossedDict = {}
predictionstats = {}    
occDict = {}          
contents = {}        

crossCounts = {}

verbose = False


town_suffixes = {}
street_suffixes = {}
towns = {}
streets = {}
names = {}
countrycodes = {".de":True, ".org":True, ".com":True, ".net":True, ".info":True, ".at":True, ".ch":True, ".fr":True}

checkurl = False
checkemail = False

repetitions = 5
k = 10
fractions = [1.0] # default: 100 % of input documents
removepunctuation = False


for i in range(1, len(sys.argv)):
    if sys.argv[i] == "-r":
        repetitions = int(sys.argv[i+1])
    elif sys.argv[i] == "-k":
        k = int(sys.argv[i+1])  # k-fold cross-validation
    elif sys.argv[i] == "-l":
        usewhichleaders = sys.argv[i+1]
        if usewhichleaders not in ["leaders1", "leaders2", "both"]:
            sys.exit()
    elif sys.argv[i] == "-o":
        pairedletterfolder = sys.argv[i+1]
    elif sys.argv[i] == "-ss":
        streetsuffixfile = codecs.open(sys.argv[i+1], "r", encoding="utf-8")
        line = streetsuffixfile.readline()
        while len(line) > 2:
            splitlist = line.split()
            street_suffixes[splitlist[0]] = True
            line = streetsuffixfile.readline()
        streetsuffixfile.close()
    elif sys.argv[i] == "-ts":
        townsuffixfile = codecs.open(sys.argv[i+1], "r", encoding="utf-8")
        line = townsuffixfile.readline()
        while len(line) > 2:
            splitlist = line.split()
            town_suffixes[splitlist[0]] = True
            line = townsuffixfile.readline()
        townsuffixfile.close()
    elif sys.argv[i] == "-s":
        streetfile = codecs.open(sys.argv[i+1], "r", encoding="utf-8")
        line = streetfile.readline()
        while len(line) > 2:
            streets[line.rstrip()] = True
            line = streetfile.readline()
        streetfile.close()
    elif sys.argv[i] == "-t":
        townfile = codecs.open(sys.argv[i+1], "r", encoding="utf-8")
        line = townfile.readline()
        while len(line) > 2:
            towns[line.rstrip()] = True
            line = townfile.readline()
        townfile.close()
    elif sys.argv[i] == "-n":
        namefile = codecs.open(sys.argv[i+1], "r", encoding="utf-8")
        line = namefile.readline()
        while len(line) > 2:
            names[line.rstrip()] = True
            line = namefile.readline()
        namefile.close()
    elif sys.argv[i] == "-d":
        j=i+1
        demaskingthresholds = []
        while j < len(sys.argv) and sys.argv[j][0] != "-":
            demaskingthresholds.append(float(sys.argv[j]))
            j += 1
    elif sys.argv[i] == "-p":
        removepunctuation = True
    elif sys.argv[i] == "-f":
        fractions = []
        j=i+1
        while j < len(sys.argv) and sys.argv[j][0] != "-":
            fractions.append(float(sys.argv[j]))
            j += 1
    elif sys.argv[i] == "-u":
        checkurl = True
    elif sys.argv[i] == "-e":
        checkemail = True
    elif sys.argv[i] == "-v":
        verbose = True


if verbose == False:
    print "Silent mode active."

print "Number of repetitions:", repetitions
print (str(k) + "-fold cross-validation")
print "Towns to purge:", len(towns)
print "Town suffixes to purge:", len(town_suffixes)
print "Streets to purge:", len(streets)
print "Street suffixes to purge:", len(street_suffixes)
print "Names to purge:", len(names)
print "Purge emails: ", checkemail
print "Purge URLs: ", checkurl
print "Leading words to use as predictors:", usewhichleaders
print "Remove punctuation:", removepunctuation



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
        



def split(a, n):
    k, m = divmod(len(a), n)
    return (a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in xrange(n))


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
    return checkurl and ("www." in word or "http" in word or word[-3:] in countrycodes)
def isEmail(word):
    return checkemail and "@" in word



for fraction in fractions:
    
    print repetitions, "rep", k, "fold CV on", min(int(fraction*len(letterpaths)), len(letterpaths)), "pairs of documents (", 100*fraction, "% of data)."
    
    for demthresh in demaskingthresholds:
        
        starttime = time.time()
        
        roccurve = []
        
        if demthresh > 1:
            "Running cross-validation. Current run without demasking."
        else:
            print "Running cross-validation. Current demasking-threshold:", demthresh
        outfile = open(pairedletterfolder.rsplit("/", 1)[0] + "/cross_validation_demthresh_" + str(repetitions) + "_" + str(k) + "_" + str(demthresh) + "_-p_" + str(removepunctuation) + "_-t_" + str(len(towns)) + "_-ts_" + str(len(town_suffixes)) + "_-s_" + str(len(streets)) + "_-ss_" + str(len(street_suffixes)) + "_-n_" + str(len(names)) + ".txt", "w")
        detectionstatsfile = open(pairedletterfolder.rsplit("/", 1)[0] + "/detectionstats_demthresh_" + str(repetitions) + "_" + str(k) + "_" + str(demthresh) + "_-p_" + str(removepunctuation) + ".txt", "w")
        detectionstatsfile.write("threshold\tmean_per_rep_leader1percentage_only\tmean_per_rep_leader2percentage_only\tnumpy.mean_per_rep_priorpercentage_only\tmean_per_rep_townpercentage_only\tmean_per_rep_streetpercentage_only\tmean_per_rep_demaskedpercentage_only\tmean_per_rep_namepercentage_only\tmean_per_rep_urlpercentage_only\tmean_per_rep_emailpercentage_only\n")
        
        for threshold in [step*0.02 for step in range(0, 51)]:
            
            print "PPV threshold for usage of leading words as predictors", threshold
            
            per_rep_sensitivity = []
            per_rep_specificity = []
            per_rep_ppv = []
            
            per_rep_sd_of_sens = []
            per_rep_sd_of_spec = []
            per_rep_sd_of_ppv = []
            
            per_rep_dist_word_sensitivity = []
            per_rep_dist_word_specificity = []
            per_rep_dist_word_ppv = []
            
            per_rep_sd_of_dist_word_sens = []
            per_rep_sd_of_dist_word_spec = []
            per_rep_sd_of_dist_word_ppv = []
            
            per_rep_leader1percentage_only = []
            per_rep_leader2percentage_only = []
            per_rep_demaskedpercentage_only = []
            per_rep_streetpercentage_only = []
            per_rep_townpercentage_only = []
            per_rep_priorpercentage_only = []
            per_rep_namepercentage_only = []
            per_rep_urlpercentage_only = []
            per_rep_emailpercentage_only = []
            
            
            mistakesdict = {"fn":{}, "fp":{}}
            
            for r in range(0, repetitions):
                
                #print "Repetition", r
                
                letternumbers = [letternumber for letternumber in letterpaths]
                random.shuffle(letternumbers)
                letternumbers = letternumbers[0:min(int(fraction*len(letternumbers)), len(letternumbers))]
                bins = list(split(letternumbers, k))
                random.shuffle(bins)
                
                per_bin_sensitivity = []
                per_bin_specificity = []
                per_bin_ppv = []
                
                per_bin_dist_word_sensitivity = []
                per_bin_dist_word_specificity = []
                per_bin_dist_word_ppv = []
                
                per_bin_leader1percentage_only = []
                per_bin_leader2percentage_only = []
                per_bin_demaskedpercentage_only = []
                per_bin_streetpercentage_only = []
                per_bin_townpercentage_only = []
                per_bin_priorpercentage_only = []
                per_bin_namepercentage_only = []
                per_bin_urlpercentage_only = []
                per_bin_emailpercentage_only = []
                
                for f in range(0, k):
                    
                    trainingnumbers = []
                    testingnumbers = bins[f]
                    for g in range(0,f):
                        trainingnumbers += bins[g]
                    for g in range(f+1,k):
                        trainingnumbers += bins[g]
                    
                    # training
                    #crossedDict = {}
                    predictionstats = {}
                    occDict = {}
                    crossCounts = {}
                    
                    for letternumber in trainingnumbers:
                        for word in crossedDict[letternumber]["bag_of_crossed_words"]:
                            for distance in [1, 2]:
                                for context in crossedDict[letternumber]["context_by_crossed_words"][word][distance]:
                                    if context not in predictionstats:
                                        predictionstats[context] = {"nondistinctwordsled":{1:[], 2:[]}, "distinctwordsled":{1:{}, 2:{}}, "letters":{1:{}, 2:{}}}
                                    predictionstats[context]["nondistinctwordsled"][distance].append(word)
                                    predictionstats[context]["distinctwordsled"][distance][word] = "yes"
                                    predictionstats[context]["letters"][distance][letternumber] = "yes"
                        for word in set(contents[letternumber]["original"]):
                            if word not in occDict:
                                occDict[word] = 0
                            occDict[word] += contents[letternumber]["original"].count(word)
                            if word not in crossCounts:
                                crossCounts[word] = 0
                            crossCounts[word] += max(0, contents[letternumber]["original"].count(word) - contents[letternumber]["anonymous"].count(word))
                    
                    
                    finalleadingcontexts = set([context for letternumber in trainingnumbers for word in crossedDict[letternumber]["context_by_crossed_words"]  for context in crossedDict[letternumber]["context_by_crossed_words"][word][1]]).difference(set([None]))
                    finalpreleadingcontexts = set([context for letternumber in trainingnumbers for word in crossedDict[letternumber]["context_by_crossed_words"]  for context in crossedDict[letternumber]["context_by_crossed_words"][word][2]]).difference(set([None]))
                    
                    #"context_leading_1_word_ahead\trel_amount_of_documents\tdistinct_words_predicted\tpositive_predictive_value\n
                    leaders1 = []
                    leaders1dict = {}
                    for context in finalleadingcontexts:
                        one_ppv = 1.0*len(predictionstats[context]["nondistinctwordsled"][1])/occDict[context]
                        if one_ppv >= threshold:
                            leaders1.append((context, 1.0*len(predictionstats[context]["letters"][1])/len(trainingnumbers), len(predictionstats[context]["distinctwordsled"][1]), one_ppv))
                            leaders1dict[context] = "yes"
                    leaders2 = []
                    leaders2dict = {}
                    for context in finalpreleadingcontexts:
                        two_ppv = 1.0*len(predictionstats[context]["nondistinctwordsled"][2])/occDict[context]
                        if two_ppv >= threshold:
                            leaders2.append((context, 1.0*len(predictionstats[context]["letters"][2])/len(trainingnumbers), len(predictionstats[context]["distinctwordsled"][2]), two_ppv))
                            leaders2dict[context] = "yes"
                    minusonedict = {}
                    for prior in priorminusonedict:
                        if priorminusonedict[prior][2] >= threshold:
                            minusonedict[prior] = priorminusonedict[prior]
                    minustwodict = {}
                    for prior in priorminustwodict:
                        if priorminustwodict[prior][2] >= threshold:
                            minustwodict[prior] = priorminustwodict[prior]
                    
                    
                    # testing
                    #crossedDict = {}
                    #occDict = {}
                    #crossCounts = {}
                    
                    
                    true_positives = 0
                    true_negatives = 0
                    false_positives = 0
                    false_negatives = 0
                    
                    detections = {"leader1":set([]), "leader2":set([]), "prior":set([]), "demasked":set([]), "town":set([]), "street":set([]), "name":set([]), "url":set([]), "email":set([])}
                    
                    dist_word_frac_true_positives = 0.0
                    dist_word_frac_true_negatives = 0.0
                    dist_word_frac_false_positives = 0.0
                    dist_word_frac_false_negatives = 0.0
                    
                    detectionstats = {}
                    
                    wordsbyid = {}
                    id = 0
                    
                        
                    for letternumber in testingnumbers:
                        
                        idsbyword = {} # true positives in test data
                        
                        # case level performance (not by-word level)
                        #     check words that should be touched (actual positives)
                        for word in crossedDict[letternumber]["context_by_crossed_words"]:
                            if word not in detectionstats:
                                detectionstats[word] = {"true_positives":0.0, "false_negatives":0.0, "false_positives":0.0, "true_negatives":0.0}
                            if word not in idsbyword:
                                idsbyword[word] = []
                            if usewhichleaders == "leaders1":
                                for i in range(0, len(crossedDict[letternumber]["context_by_crossed_words"][word][1])): # len(list1) == len(list2)
                                    id += 1
                                    idsbyword[word].append(id)
                                    if isUrl(word) or isEmail(word) or hasStreetSuffix(word) or hasTownSuffix(word) or isStreet(word, crossedDict[letternumber]["context_by_crossed_words"][word][2][i], crossedDict[letternumber]["context_by_crossed_words"][word][1][i]) or isTown(word, crossedDict[letternumber]["context_by_crossed_words"][word][2][i], crossedDict[letternumber]["context_by_crossed_words"][word][1][i]) or isName(word) or crossedDict[letternumber]["context_by_crossed_words"][word][1][i] in leaders1dict or crossedDict[letternumber]["context_by_crossed_words"][word][1][i] in minusonedict:
                                        if crossedDict[letternumber]["context_by_crossed_words"][word][1][i] in minusonedict:
                                            detections["prior"].add(id)
                                        if hasTownSuffix(word) or isTown(word, crossedDict[letternumber]["context_by_crossed_words"][word][2][i], crossedDict[letternumber]["context_by_crossed_words"][word][1][i]):
                                            detections["town"].add(id)
                                        if hasStreetSuffix(word) or isStreet(word, crossedDict[letternumber]["context_by_crossed_words"][word][2][i], crossedDict[letternumber]["context_by_crossed_words"][word][1][i]):
                                            detections["street"].add(id)
                                        if crossedDict[letternumber]["context_by_crossed_words"][word][1][i] in leaders1dict:
                                            detections["leader1"].add(id)
                                        if isName(word):
                                            detections["name"].add(id)
                                        if isUrl(word):
                                            detections["url"].add(id)
                                        if isEmail(word):
                                            detections["email"].add(id)
                                        true_positives += 1 # correctly touched
                                        detectionstats[word]["true_positives"] += 1
                                    else:
                                        false_negatives += 1 # not touched by anonymization, although it should be
                                        detectionstats[word]["false_negatives"] += 1
                                        if word not in mistakesdict["fn"]:
                                            mistakesdict["fn"][word] = 0
                                        mistakesdict["fn"][word] += 1
                            elif usewhichleaders == "both":
                                for i in range(0, len(crossedDict[letternumber]["context_by_crossed_words"][word][1])): # len(list1) == len(list2)
                                    if isUrl(word) or isEmail(word) or hasStreetSuffix(word) or hasTownSuffix(word) or isStreet(word, crossedDict[letternumber]["context_by_crossed_words"][word][2][i], crossedDict[letternumber]["context_by_crossed_words"][word][1][i]) or isTown(word, crossedDict[letternumber]["context_by_crossed_words"][word][2][i], crossedDict[letternumber]["context_by_crossed_words"][word][1][i]) or isName(word) or crossedDict[letternumber]["context_by_crossed_words"][word][1][i] in leaders1dict or crossedDict[letternumber]["context_by_crossed_words"][word][2][i] in leaders2dict or crossedDict[letternumber]["context_by_crossed_words"][word][1][i] in minusonedict or crossedDict[letternumber]["context_by_crossed_words"][word][2][i] in minustwodict:
                                        id += 1
                                        idsbyword[word].append(id)
                                        if crossedDict[letternumber]["context_by_crossed_words"][word][1][i] in minusonedict or crossedDict[letternumber]["context_by_crossed_words"][word][2][i] in minustwodict:
                                            detections["prior"].add(id)
                                        if hasTownSuffix(word) or isTown(word, crossedDict[letternumber]["context_by_crossed_words"][word][2][i], crossedDict[letternumber]["context_by_crossed_words"][word][1][i]):
                                            detections["town"].add(id)
                                        if hasStreetSuffix(word) or isStreet(word, crossedDict[letternumber]["context_by_crossed_words"][word][2][i], crossedDict[letternumber]["context_by_crossed_words"][word][1][i]):
                                            detections["street"].add(id)
                                        if crossedDict[letternumber]["context_by_crossed_words"][word][1][i] in leaders1dict:
                                            detections["leader1"].add(id)
                                        if crossedDict[letternumber]["context_by_crossed_words"][word][2][i] in leaders2dict:
                                            detections["leader2"].add(id)
                                        if isName(word):
                                            detections["name"].add(id)
                                        if isUrl(word):
                                            detections["url"].add(id)
                                        if isEmail(word):
                                            detections["email"].add(id)
                                        true_positives += 1 # correctly touched
                                        detectionstats[word]["true_positives"] += 1
                                    else:
                                        false_negatives += 1 # not touched by anonymization, although it should be
                                        detectionstats[word]["false_negatives"] += 1
                                        if word not in mistakesdict["fn"]:
                                            mistakesdict["fn"][word] = 0
                                        mistakesdict["fn"][word] += 1
                            elif usewhichleaders == "leaders2":
                                for i in range(0, len(crossedDict[letternumber]["context_by_crossed_words"][word][1])): # len(list1) == len(list2)
                                    if isUrl(word) or isEmail(word) or hasStreetSuffix(word) or hasTownSuffix(word) or isStreet(word, crossedDict[letternumber]["context_by_crossed_words"][word][2][i], crossedDict[letternumber]["context_by_crossed_words"][word][1][i]) or isTown(word, crossedDict[letternumber]["context_by_crossed_words"][word][2][i], crossedDict[letternumber]["context_by_crossed_words"][word][1][i]) or isName(word) or crossedDict[letternumber]["context_by_crossed_words"][word][2][i] in leaders2dict or crossedDict[letternumber]["context_by_crossed_words"][word][2][i] in minustwodict:
                                        id += 1
                                        idsbyword[word].append(id)
                                        if crossedDict[letternumber]["context_by_crossed_words"][word][2][i] in minustwodict:
                                            detections["prior"].add(id)
                                        if hasTownSuffix(word) or isTown(word, crossedDict[letternumber]["context_by_crossed_words"][word][2][i], crossedDict[letternumber]["context_by_crossed_words"][word][1][i]):
                                            detections["town"].add(id)
                                        if hasStreetSuffix(word) or isStreet(word, crossedDict[letternumber]["context_by_crossed_words"][word][2][i], crossedDict[letternumber]["context_by_crossed_words"][word][1][i]):
                                            detections["street"].add(id)
                                        if crossedDict[letternumber]["context_by_crossed_words"][word][2][i] in leaders2dict:
                                            detections["leader2"].add(id)
                                        if isName(word):
                                            detections["name"].add(id)
                                        if isUrl(word):
                                            detections["url"].add(id)
                                        if isEmail(word):
                                            detections["email"].add(id)
                                        true_positives += 1 # correctly touched
                                        detectionstats[word]["true_positives"] += 1
                                    else:
                                        false_negatives += 1 # not touched by anonymization, although it should be
                                        detectionstats[word]["false_negatives"] += 1
                                        if word not in mistakesdict["fn"]:
                                            mistakesdict["fn"][word] = 0
                                        mistakesdict["fn"][word] += 1
                        #    check words that should NOT be touched (actual negatives)
                        for i in range(2, len(contents[letternumber]["original"])):
                            word = contents[letternumber]["original"][i]
                            if word not in idsbyword:
                                idsbyword[word] = []
                            if word not in detectionstats:
                                detectionstats[word] = {"true_positives":0.0, "false_negatives":0.0, "false_positives":0.0, "true_negatives":0.0}
                            if word not in crossedDict[letternumber]["bag_of_crossed_words"]:
                                id += 1
                                if usewhichleaders == "leaders1":
                                    if isUrl(word) or isEmail(word) or hasStreetSuffix(word) or hasTownSuffix(word) or isStreet(word, contents[letternumber]["original"][i-2], contents[letternumber]["original"][i-1]) or isTown(word, contents[letternumber]["original"][i-2], contents[letternumber]["original"][i-1]) or isName(word) or contents[letternumber]["original"][i-1] in leaders1dict or contents[letternumber]["original"][i-1] in minusonedict:
                                        id += 1
                                        idsbyword[word].append(id)
                                        if contents[letternumber]["original"][i-1] in minusonedict:
                                            detections["prior"].add(id)
                                        if hasTownSuffix(word) or isTown(word, contents[letternumber]["original"][i-2], contents[letternumber]["original"][i-1]):
                                            detections["town"].add(id)
                                        if hasStreetSuffix(word) or isStreet(word, contents[letternumber]["original"][i-2], contents[letternumber]["original"][i-1]):
                                            detections["street"].add(id)
                                        if contents[letternumber]["original"][i-1] in leaders1dict:
                                            detections["leader1"].add(id)
                                        if isName(word):
                                            detections["name"].add(id)
                                        if isUrl(word):
                                            detections["url"].add(id)
                                        if isEmail(word):
                                            detections["email"].add(id)
                                        false_positives += 1
                                        detectionstats[word]["false_positives"] += 1
                                        if word not in mistakesdict["fp"]:
                                            mistakesdict["fp"][word] = 0
                                        mistakesdict["fp"][word] += 1
                                    else:
                                        true_negatives += 1
                                        detectionstats[word]["true_negatives"] += 1
                                elif usewhichleaders == "both":
                                    if isUrl(word) or isEmail(word) or hasStreetSuffix(word) or hasTownSuffix(word) or isStreet(word, contents[letternumber]["original"][i-2], contents[letternumber]["original"][i-1]) or isTown(word, contents[letternumber]["original"][i-2], contents[letternumber]["original"][i-1]) or isName(word) or contents[letternumber]["original"][i-1] in leaders1dict or contents[letternumber]["original"][i-2] in leaders2dict or contents[letternumber]["original"][i-1] in minusonedict or contents[letternumber]["original"][i-2] in minustwodict:
                                        id += 1
                                        idsbyword[word].append(id)
                                        if contents[letternumber]["original"][i-1] in minusonedict or contents[letternumber]["original"][i-2] in minusonedict:
                                            detections["prior"].add(id)
                                        if hasTownSuffix(word) or isTown(word, contents[letternumber]["original"][i-2], contents[letternumber]["original"][i-1]):
                                            detections["town"].add(id)
                                        if hasStreetSuffix(word) or isStreet(word, contents[letternumber]["original"][i-2], contents[letternumber]["original"][i-1]):
                                            detections["street"].add(id)
                                        if contents[letternumber]["original"][i-1] in leaders1dict:
                                            detections["leader1"].add(id)
                                        if isName(word):
                                            detections["name"].add(id)
                                        if isUrl(word):
                                            detections["url"].add(id)
                                        if isEmail(word):
                                            detections["email"].add(id)
                                        false_positives += 1
                                        detectionstats[word]["false_positives"] += 1
                                        if word not in mistakesdict["fp"]:
                                            mistakesdict["fp"][word] = 0
                                        mistakesdict["fp"][word] += 1
                                    else:
                                        true_negatives += 1
                                        detectionstats[word]["true_negatives"] += 1
                                elif usewhichleaders == "leaders2":
                                    if isUrl(word) or isEmail(word) or hasStreetSuffix(word) or hasTownSuffix(word) or isStreet(word, contents[letternumber]["original"][i-2], contents[letternumber]["original"][i-1]) or isTown(word, contents[letternumber]["original"][i-2], contents[letternumber]["original"][i-1]) or isName(word) or contents[letternumber]["original"][i-2] in leaders2dict or contents[letternumber]["original"][i-2] in minustwodict:
                                        id += 1
                                        idsbyword[word].append(id)
                                        if contents[letternumber]["original"][i-2] in minustwodict:
                                            detections["prior"].add(id)
                                        if hasTownSuffix(word) or isTown(word, contents[letternumber]["original"][i-2], contents[letternumber]["original"][i-1]):
                                            detections["town"].add(id)
                                        if hasStreetSuffix(word) or isStreet(word, contents[letternumber]["original"][i-2], contents[letternumber]["original"][i-1]):
                                            detections["street"].add(id)
                                        if contents[letternumber]["original"][i-2] in leaders2dict:
                                            detections["leader2"].add(id)
                                        if isName(word):
                                            detections["name"].add(id)
                                        if isUrl(word):
                                            detections["url"].add(id)
                                        if isEmail(word):
                                            detections["email"].add(id)
                                        false_positives += 1
                                        detectionstats[word]["false_positives"] += 1
                                        if word not in mistakesdict["fp"]:
                                            mistakesdict["fp"][word] = 0
                                        mistakesdict["fp"][word] += 1
                                    else:
                                        true_negatives += 1
                                        detectionstats[word]["true_negatives"] += 1
                        # Purging previously demasked words
                        for word in crossedDict[letternumber]["context_by_crossed_words"]: # should be touched
                            if len(idsbyword[word]) > 0 and word in occDict and float(crossCounts[word])/occDict[word] >= demthresh: # word was identified and training cross-out freq of word was high enough
                                #print "hello", word, occDict[word], crossCounts[word]
                                for i in range(0, len(crossedDict[letternumber]["context_by_crossed_words"][word][1]) - len(idsbyword[word])):
                                    id += 1
                                    detections["demasked"].add(id)
                                    true_positives += 1
                                    false_negatives -= 1
                                    #if word not in mistakesdict["fn"]:
                                    #    mistakesdict["fn"][word] = 0
                                    #mistakesdict["fn"][word] += 1
                        for word in set(contents[letternumber]["original"]):
                            if word in idsbyword and len(idsbyword[word]) > 0 and word in occDict and float(crossCounts[word])/occDict[word] >= demthresh and word not in crossedDict[letternumber]["bag_of_crossed_words"]: # shouldn't be touched, but # word was identified and will be touched by demasker if (above-threshold) training stats are available
                                for i in range(0, contents[letternumber]["original"].count(word)-len(idsbyword[word])):
                                    #print word
                                    id += 1
                                    detections["demasked"].add(id)
                                    false_positives += 1
                                    true_negatives -= 1
                                    if word not in mistakesdict["fp"]:
                                        mistakesdict["fp"][word] = 0
                                    mistakesdict["fp"][word] += 1
                    #print true_positives, false_negatives, false_positives, true_negatives
                    per_bin_sensitivity.append(float(true_positives) / (true_positives + false_negatives))
                    per_bin_specificity.append(float(true_negatives) / (false_positives + true_negatives))
                    per_bin_ppv.append(float(true_positives) / (true_positives + false_positives))
                    
                    per_bin_dist_word_sensitivity.append(numpy.mean([detectionstats[word]["true_positives"] / (detectionstats[word]["true_positives"] + detectionstats[word]["false_negatives"]) for word in detectionstats if (detectionstats[word]["true_positives"] + detectionstats[word]["false_negatives"])>0]))
                    per_bin_dist_word_specificity.append(numpy.mean([detectionstats[word]["true_negatives"] / (detectionstats[word]["false_positives"] + detectionstats[word]["true_negatives"]) for word in detectionstats if (detectionstats[word]["false_positives"] + detectionstats[word]["true_negatives"])>0]))
                    per_bin_dist_word_ppv.append(numpy.mean([detectionstats[word]["true_positives"] / (detectionstats[word]["true_positives"] + detectionstats[word]["false_positives"]) for word in detectionstats if (detectionstats[word]["true_positives"] + detectionstats[word]["false_positives"])>0]))
                
                    alldetections = detections["leader1"] | detections["leader2"] | detections["demasked"] | detections["street"] | detections["town"]  | detections["prior"] | detections["name"] | detections["url"] | detections["email"]
                    
                    per_bin_leader1percentage_only.append(float(len(detections["leader1"]-detections["leader2"]-detections["demasked"]-detections["street"]-detections["town"]-detections["prior"]-detections["name"]-detections["url"]-detections["email"])) / len(alldetections))
                    per_bin_leader2percentage_only.append(float(len(detections["leader2"]-detections["leader1"]-detections["demasked"]-detections["street"]-detections["town"]-detections["prior"]-detections["name"]-detections["url"]-detections["email"])) / len(alldetections))
                    per_bin_demaskedpercentage_only.append(float(len(detections["demasked"]-detections["leader2"]-detections["leader1"]-detections["street"]-detections["town"]-detections["prior"]-detections["name"]-detections["url"]-detections["email"])) / len(alldetections))
                    per_bin_streetpercentage_only.append(float(len(detections["street"]-detections["leader2"]-detections["demasked"]-detections["leader1"]-detections["town"]-detections["prior"]-detections["name"]-detections["url"]-detections["email"])) / len(alldetections))
                    per_bin_townpercentage_only.append(float(len(detections["town"]-detections["leader2"]-detections["demasked"]-detections["street"]-detections["leader1"]-detections["prior"]-detections["name"]-detections["url"]-detections["email"])) / len(alldetections))
                    per_bin_priorpercentage_only.append(float(len(detections["prior"]-detections["leader2"]-detections["demasked"]-detections["street"]-detections["town"]-detections["leader1"]-detections["name"]-detections["url"]-detections["email"])) / len(alldetections))
                    per_bin_namepercentage_only.append(float(len(detections["name"]-detections["leader2"]-detections["demasked"]-detections["street"]-detections["town"]-detections["leader1"]-detections["prior"]-detections["url"]-detections["email"])) / len(alldetections))
                    per_bin_urlpercentage_only.append(float(len(detections["url"]-detections["leader2"]-detections["demasked"]-detections["street"]-detections["town"]-detections["leader1"]-detections["name"]-detections["prior"]-detections["email"])) / len(alldetections))
                    per_bin_emailpercentage_only.append(float(len(detections["email"]-detections["leader2"]-detections["demasked"]-detections["street"]-detections["town"]-detections["leader1"]-detections["name"]-detections["prior"]-detections["url"])) / len(alldetections))
                    
                    
                per_rep_sensitivity.append(numpy.mean(per_bin_sensitivity))
                per_rep_sd_of_sens.append(numpy.std(per_bin_sensitivity))
                per_rep_specificity.append(numpy.mean(per_bin_specificity))
                per_rep_sd_of_spec.append(numpy.std(per_bin_specificity))
                per_rep_ppv.append(numpy.mean(per_bin_ppv))
                per_rep_sd_of_ppv.append(numpy.std(per_bin_ppv))
                
                per_rep_dist_word_sensitivity.append(numpy.mean(per_bin_dist_word_sensitivity))
                per_rep_sd_of_dist_word_sens.append(numpy.std(per_bin_dist_word_sensitivity))
                per_rep_dist_word_specificity.append(numpy.mean(per_bin_dist_word_specificity))
                per_rep_sd_of_dist_word_spec.append(numpy.std(per_bin_dist_word_specificity))
                per_rep_dist_word_ppv.append(numpy.mean(per_bin_dist_word_ppv))
                per_rep_sd_of_dist_word_ppv.append(numpy.std(per_bin_dist_word_ppv))
                
                per_rep_leader1percentage_only.append(numpy.mean(per_bin_leader1percentage_only))
                per_rep_leader2percentage_only.append(numpy.mean(per_bin_leader2percentage_only))
                per_rep_demaskedpercentage_only.append(numpy.mean(per_bin_demaskedpercentage_only))
                per_rep_streetpercentage_only.append(numpy.mean(per_bin_streetpercentage_only))
                per_rep_townpercentage_only.append(numpy.mean(per_bin_townpercentage_only))
                per_rep_priorpercentage_only.append(numpy.mean(per_bin_priorpercentage_only))
                per_rep_namepercentage_only.append(numpy.mean(per_bin_namepercentage_only))
                per_rep_urlpercentage_only.append(numpy.mean(per_bin_urlpercentage_only))
                per_rep_emailpercentage_only.append(numpy.mean(per_bin_emailpercentage_only))
            
            crossvalidationoutput = ("threshold" + "\t" + str(threshold) + "\t" + 
            "mean_per-rep_per-bin_sensitivity_(recall):" + "\t" + str(numpy.mean(per_rep_sensitivity)) + "\t" + 
            "avg_inter-bin-SD_per_rep_+-" + "\t" + str(numpy.mean(per_rep_sd_of_sens)) + "\t" + 
            "SD_of_inter-bin-SDs_per_rep_+-" + "\t" + str(numpy.std(per_rep_sd_of_sens)) + "\t" + 
            "mean_per-rep_per-bin_PPV_(precision):" + "\t" + str(numpy.mean(per_rep_ppv)) + "\t" + 
            "avg_inter-bin-SD_per_rep_+-" + "\t" + str(numpy.mean(per_rep_sd_of_ppv)) + "\t" + 
            "SD_of_inter-bin-SDs_per_rep_+-" + "\t" + str(numpy.std(per_rep_sd_of_ppv)) + "\t" + 
            "mean_per-rep_per-bin_specificity_(TNR):" + "\t" + str(numpy.mean(per_rep_specificity)) + "\t" + 
            "avg_inter-bin-SD_per_rep_+-" + "\t" + str(numpy.mean(per_rep_sd_of_spec)) + "\t" + 
            "SD_of_inter-bin-SDs_per_rep_+-" + "\t" + str(numpy.std(per_rep_sd_of_spec)) + "\t" +
            
            "mean_per-rep_per-bin_dist_word_sensitivity_(recall):" + "\t" + str(numpy.mean(per_rep_dist_word_sensitivity)) + "\t" + 
            "avg_inter-bin-SD_per_rep_+-" + "\t" + str(numpy.mean(per_rep_sd_of_dist_word_sens)) + "\t" + 
            "SD_of_inter-bin-SDs_per_rep_+-" + "\t" + str(numpy.std(per_rep_sd_of_dist_word_sens)) + "\t" + 
            "mean_per-rep_per-bin_dist_word_PPV_(precision):" + "\t" + str(numpy.mean(per_rep_dist_word_ppv)) + "\t" + 
            "avg_inter-bin-SD_per_rep_+-" + "\t" + str(numpy.mean(per_rep_sd_of_dist_word_ppv)) + "\t" + 
            "SD_of_inter-bin-SDs_per_rep_+-" + "\t" + str(numpy.std(per_rep_sd_of_dist_word_ppv)) + "\t" + 
            "mean_per-rep_per-bin_dist_word_specificity_(TNR):" + "\t" + str(numpy.mean(per_rep_dist_word_specificity)) + "\t" + 
            "avg_inter-bin-SD_per_rep_+-" + "\t" + str(numpy.mean(per_rep_sd_of_dist_word_spec)) + "\t" + 
            "SD_of_inter-bin-SDs_per_rep_+-" + "\t" + str(numpy.std(per_rep_sd_of_dist_word_spec)))
            roccurve.append((numpy.mean(per_rep_specificity), numpy.mean(per_rep_sensitivity)))
            
            #print mistakesdict
            if verbose:
                print crossvalidationoutput
            outfile.write(crossvalidationoutput + "\n")
            detectionstatsfile.write(str(threshold) + "\t" + str(numpy.mean(per_rep_leader1percentage_only)) + "\t" + str(numpy.mean(per_rep_leader2percentage_only)) + "\t" + str(numpy.mean(per_rep_priorpercentage_only)) + "\t" + str(numpy.mean(per_rep_townpercentage_only)) + "\t" + str(numpy.mean(per_rep_streetpercentage_only)) + "\t" + str(numpy.mean(per_rep_demaskedpercentage_only)) + "\t" + str(numpy.mean(per_rep_namepercentage_only)) + "\t" + str(numpy.mean(per_rep_urlpercentage_only)) + "\t" + str(numpy.mean(per_rep_emailpercentage_only)) + "\n")
        print fraction*100, "% of data yielded an AUC of", numpy.trapz(y=[item[1] for item in roccurve], x=[1.0-item[0] for item in roccurve]) / numpy.trapz(y=[1.0 for item in roccurve], x=[1.0-item[0] for item in roccurve])
        
        endtime = time.time()
        print "Time elapsed under demasking threshold", demthresh, " - ", endtime - starttime, "seconds"
        
        outfile.close()
        detectionstatsfile.close()