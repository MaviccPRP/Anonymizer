#!/usr/env/python

"""
Author: Ralf Hauenschild
E-Mail: ralf_hauenschild@gmx.de
"""

import sys
import os
import numpy
import matplotlib
import matplotlib as mpl
import matplotlib.pyplot as plt
import pylab as py
import matplotlib.cm as cm
import math



c = []
sens = [] # sens (recall)
senserror = []
specloss = [] # 1-spec
specerror = []
p = [] # ppv (precision)
perror = []



for i in range(1, len(sys.argv)):
    if sys.argv[i] != "distinct":
        c.append([])
        sens.append([]) # sens (recall)
        senserror.append([])
        specloss.append([]) # 1-spec
        specerror.append([])
        p.append([]) # ppv (precision)
        perror.append([])
        
        infile = open(sys.argv[i], "r")
        line = infile.readline()
        while len(line) > 4:
            splitlist = line[:-1].split("\t")
            
            if "distinct" in sys.argv[i]:
                c[i-1].append(float(splitlist[1]))
                sens[i-1].append(float(splitlist[21]))
                senserror[i-1].append(float(splitlist[23]))
                specloss[i-1].append(1-float(splitlist[33]))
                specerror[i-1].append(float(splitlist[35]))
                p[i-1].append(float(splitlist[27]))
                perror[i-1].append(float(splitlist[29]))
            else:
                c[i-1].append(float(splitlist[1]))
                sens[i-1].append(float(splitlist[3]))
                senserror[i-1].append(float(splitlist[5]))
                specloss[i-1].append(1-float(splitlist[15]))
                specerror[i-1].append(float(splitlist[17]))
                p[i-1].append(float(splitlist[9]))
                perror[i-1].append(float(splitlist[11]))
            
            line = infile.readline()
            
        infile.close()


fig = py.figure(1, figsize=(12, 6))
py.subplots_adjust(top=0.8)

linestyles = ["-", "--"]

#colors=[cb.to_rgba(value) for value in c]

norm=mpl.colors.Normalize(vmin=min(c[0]), vmax=max(c[0]))


fig.suptitle("Anonymization performance assessment under sliding PPV threshold\nfor words leading X-ed out training content")
#labels = ["-1 leader only", "-1 & -2 leader indep."]
labels = ["X-out events", "word-distinct X-out events"]
handles = []

m = cm.ScalarMappable(norm=norm, cmap=cm.jet)

ax = fig.add_subplot(121)

for column in range(0, len(specloss)):
    for i in range(1, len(specloss[column])):
        aplot, = ax.plot(specloss[column][i-1:i+1], sens[column][i-1:i+1], linestyles[column], color=m.to_rgba(numpy.mean(c[column][i-1:i+1])), linewidth=3)
    for i in range(0, len(specloss[column])):
        ax.errorbar(specloss[column][i:i+1], sens[column][i:i+1], xerr=specerror[column][i:i+1], yerr=senserror[column][i:i+1], marker='o', fmt='-o', linewidth=3, color=m.to_rgba(c[column][i]))
    
    group1 = ax.scatter(specloss[column], sens[column], c=c[column], cmap=cm.jet, norm=norm, alpha=0)

import matplotlib.ticker as ticker
#, format=ticker.FormatStrFormatter('%.0f')
cb = py.colorbar(group1)
cb.set_alpha(1)
cb.draw_all()
cb.ax.set_ylabel("PPV threshold for feature to be considered in model")

py.xlim(xmin=0)
py.ylim(ymin=0)

py.xlabel("FPR (1-specificity)")
py.ylabel("TPR (sensitivity)")
py.title("ROC")

a, = ax.plot([-1, -1], [-1, -1], linestyles[0], color=m.to_rgba(c[column][0]), linewidth=3)
b, = ax.plot([-1, -1], [-1, -1], linestyles[1], color=m.to_rgba(c[column][0]), linewidth=3)
#plt.legend([a, b], labels, loc='lower right')
#plt.legend(handles=handles, labels=labels)


ax = fig.add_subplot(122)

for column in range(0, len(specloss)):
    print sens[column]
    for i in range(1, len(specloss[column])):
        ax.plot(sens[column][i-1:i+1], p[column][i-1:i+1], linestyles[column], color=m.to_rgba(numpy.mean(c[column][i-1:i+1])), linewidth=3)
    for i in range(0, len(specloss[column])):
        ax.errorbar(sens[column][i:i+1], p[column][i:i+1], xerr=senserror[column][i:i+1], yerr=perror[column][i:i+1], marker='o', fmt='-o', linewidth=3, color=m.to_rgba(c[column][i]))


cb = py.colorbar(group1)
cb.set_alpha(1)
cb.draw_all()
cb.ax.set_ylabel("PPV threshold for feature to be considered in model")

py.xlim(xmin=0, xmax=1)
py.ylim(ymin=0, ymax=1)

py.xlabel("sensitivity (recall)")
py.ylabel("PPV (precision)")
py.title("P/R (precision by recall)")

a, = ax.plot([-1, -1], [-1, -1], linestyles[0], color=m.to_rgba(c[column][0]), linewidth=3)
b, = ax.plot([-1, -1], [-1, -1], linestyles[1], color=m.to_rgba(c[column][0]), linewidth=3)
#plt.legend([a, b], labels, loc='lower left')

auc = round(numpy.trapz(y=[item for item in sens[0][::-1]], x=[item for item in specloss[0][::-1]]) / numpy.trapz(y=[1.0 for item in sens[0][::-1]], x=[item for item in specloss[0][::-1]]), 4)

print "AUC:", auc

plt.savefig(sys.argv[1] + ".roc" + "_auc_" + str(auc) + ".svg")

plt.show()

plt.close()