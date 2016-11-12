from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import GradientBoostingClassifier

from skTMVA import convert_bdt_sklearn_tmva

import cPickle

import numpy as np
from numpy.random import RandomState

RNG = RandomState(31)

# Construct an example dataset for binary classification
n_vars = 2
n_events = 10000
signal = RNG.multivariate_normal(
    np.ones(n_vars), np.diag(np.ones(n_vars)), n_events)
background = RNG.multivariate_normal(
    np.ones(n_vars) * -1, np.diag(np.ones(n_vars)), n_events)
X = np.concatenate([signal, background])
y = np.ones(X.shape[0])
w = RNG.randint(1, 10, n_events * 2)
y[signal.shape[0]:] *= -1
permute = RNG.permutation(y.shape[0])
X = X[permute]
y = y[permute]

# Use all dataset for training
X_train, y_train, w_train = X, y, w

# Declare BDT - we are going to use AdaBoost Decision Tree
bdt = GradientBoostingClassifier(
    n_estimators=200, learning_rate=0.5,
    min_samples_leaf=int(0.05*len(X_train)),
    max_depth=3, random_state=0)

# Train BDT
bdt.fit(X_train, y_train)

# Save BDT to pickle file
with open('bdt_sklearn_to_tmva_example.pkl', 'wb') as fid:
    cPickle.dump(bdt, fid)


# Save BDT to TMVA xml file 
# Note:
#    - declare input variable names and their type 
#    - variable order is important for TMVA
convert_bdt_sklearn_tmva(bdt, [('var1', 'F'), ('var2', 'F')], 'bdt_sklearn_to_tmva_example.xml')

