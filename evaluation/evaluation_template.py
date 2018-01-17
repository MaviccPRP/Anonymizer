# Evaluation script template for de-identification tool https://github.com/dieterich-lab/Anonymize

from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.metrics import roc_curve, auc
from sklearn.metrics import matthews_corrcoef
from sklearn.metrics import fbeta_score
from sklearn.model_selection import permutation_test_score
import matplotlib.pyplot as plt
import glob
from mlxtend.evaluate import mcnemar
import collections
import numpy as np
from mlxtend.evaluate import mcnemar_table

# Evaluating baseline
# Save predicted labels and gold standard into these variables
y_true = []
y_pred = []

# Define folder of predictions and gold standard
file_list = []

# ENTER the folders of gold standard and labeled data for baseline
types = ('*.conll', '*.tokenized_anon')

for files in types:
	for file in glob.glob(files):
		file_list.append(file)

file_list = sorted(file_list)
list1 = file_list[:int(len(file_list)/2)]
list2 = file_list[int(len(file_list)/2):]
d = 0


for i,j in zip(list2, list1):
	with open(i, "r", encoding="utf-8") as gold, open(j, "r", encoding="utf-8") as anno:
		for g, a in zip(gold, anno):
			g = g.replace(" ", "\t")
			a = a.replace(" ", "\t")
			a = a.split("\t")
			g = g.split("\t")
			g = [elem.replace("ORG", "O") for elem in g]
			a = [elem.replace("ORG", "O") for elem in a]
			if len(a) > 1 and len(g) > 1:
				# Analze binary
				if "ANON" in a[1]:
					y_pred.append(1)
				else:
					y_pred.append(0)
				if len(g[1].strip()) == 1:
					y_true.append(0)
				else:
					y_true.append(1)
			
# Print evaluation report, confusion matrix and f2 scores
print("Evaluation baseline:")
print(classification_report(y_true, y_pred, labels=[1,0]))
print("Confusion matrix:")
print(confusion_matrix(y_true, y_pred, labels= [1,0]))

print("MCC",matthews_corrcoef(y_true, y_pred))
print("F2 - None",fbeta_score(y_true, y_pred, average=None, beta=2))
print("F2 - weighted",fbeta_score(y_true, y_pred, average='weighted', beta=2))
print("F2 - micro",fbeta_score(y_true, y_pred, average='micro', beta=2))
print("F2 - macro",fbeta_score(y_true, y_pred, average='macro', beta=2))

# Evaluating full featured model

y_true = []
y_pred2 = []

import glob

file_list = []
# ENTER the folders of gold standard and labeled data for baseline
types = ('*.conll', '*.tokenized_anon')

for files in types:
	for file in glob.glob(files):
		file_list.append(file)

file_list = sorted(file_list)
list1 = file_list[:int(len(file_list)/2)]
list2 = file_list[int(len(file_list)/2):]
d = 0


for i,j in zip(list2, list1):
	with open(i, "r", encoding="utf-8") as gold, open(j, "r", encoding="utf-8") as anno:
		for g, a in zip(gold, anno):
			g = g.replace(" ", "\t")
			a = a.replace(" ", "\t")
			a = a.split("\t")
			g = g.split("\t")
			g = [elem.replace("ORG", "O") for elem in g]
			a = [elem.replace("ORG", "O") for elem in a]
			if len(a) > 1 and len(g) > 1:
				# Analze binary
				if "ANON" in a[1]:
					y_pred2.append(1)
				else:
					y_pred2.append(0)
				if len(g[1].strip()) == 1:
					y_true.append(0)
				else:
					y_true.append(1)

# Print evaluation report, confusion matrix and f2 scores
print("Evaluation full featured model:")
print(classification_report(y_true, y_pred2, labels= [1,0]))
print("Confusion matrix:")
print(confusion_matrix(y_true, y_pred2, labels= [1,0]))

print("MCC",matthews_corrcoef(y_true, y_pred2))
print("F2 - None",fbeta_score(y_true, y_pred2, average=None, beta=2))
print("F2 - weighted",fbeta_score(y_true, y_pred2, average='weighted', beta=2))
print("F2 - micro",fbeta_score(y_true, y_pred2, average='micro', beta=2))
print("F2 - macro",fbeta_score(y_true, y_pred2, average='macro', beta=2))


# McNemar test

y_true = np.array(y_true)
y_pred = np.array(y_pred)
y_pred2 = np.array(y_pred2)

tb = mcnemar_table(y_target=y_true, y_model1=y_pred, y_model2=y_pred2)
print("McNemar contigency table")
print(tb)

chi2, p = mcnemar(ary=tb, corrected=True)
print('chi-squared:', chi2)
print('p-value:', p)