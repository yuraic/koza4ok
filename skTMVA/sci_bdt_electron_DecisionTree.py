from array import array

import numpy as np
import matplotlib.pyplot as plt

from sklearn import datasets
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.metrics import classification_report, roc_auc_score, roc_curve

from sklearn import tree
import cPickle

data = np.load('/Users/musthero/Documents/Yura/Applications/tmva_local/output_electrons_fullsim_v5_VeryTightLH_20per.npz')

# Train on the first 2000, test on the rest
X_train, y_train = data['data_training'], data['isprompt_training'].ravel()
X_test, y_test = data['data_testing'][0:1000], data['isprompt_testing'][0:1000].ravel()

# sklearn
dt = DecisionTreeClassifier(max_depth=3,
                            min_samples_leaf=100)
                            #min_samples_leaf=0.05*len(X_train))

doFit = False

if doFit:
    print "Performing DecisionTree fit..."
    dt.fit(X_train, y_train)

    import cPickle
    with open('electrons_toTMVA.pkl', 'wb') as fid:
        cPickle.dump(dt, fid)
else:
    print "Loading DecisionTree..."
    # load it again
    with open('electrons_toTMVA.pkl', 'rb') as fid:
        dt = cPickle.load(fid)

#sk_y_predicted = dt.predict(X_test)
#sk_y_predicted = dt.predict_proba(X_test)[:, 1]
sk_y_predicted = dt.predict_proba(X_test)[:, 1]
predictions = dt.predict(X_test)
print predictions
print y_test


# Draw ROC curve
fpr, tpr, _ = roc_curve(y_test, sk_y_predicted)

plt.figure()
plt.plot(fpr, tpr, label='ROC curve of class')

plt.plot([0, 1], [0, 1], 'k--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Some extension of Receiver operating characteristic to multi-class')
plt.legend(loc="lower right")

plt.savefig("output_fullsim_v5_electrons_roc_20per_DecisionTree.png", dpi=144)

tree.export_graphviz(dt, out_file='dt_viz.dot')

# Save to file fpr, tpr
#np.savez('output_fullsim_v3_electrons_fpr_tpr_10per.npz', 
#    fpr=fpr, tpr=tpr)