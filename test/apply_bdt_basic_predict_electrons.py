# Author: Yuriy Ilchenko (ilchenko@physics.utexas.edu)
# Compare scikit-learn and TMVA ROC-curves for a simple case:
#  - sklearn: use BDT predict() method to classify
#  - TMVA: apply bdtOutput >0 cut for positive events (essentially same as above)

import os
import sys

if os.environ['TERM'] == 'xterm':
    os.environ['TERM'] = 'vt100'
# Now it's OK to import readline :)
# Import ROOT libraries

import ROOT
from ROOT import TH1F
import array

import numpy as np
import matplotlib.pyplot as plt

from sklearn import datasets
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.metrics import classification_report, roc_auc_score, roc_curve

from sklearn import tree
import cPickle


reader = ROOT.TMVA.Reader()

m_el_pt = array.array('f',[0])
reader.AddVariable("m_el_pt", m_el_pt)
m_el_eta = array.array('f',[0])
reader.AddVariable("m_el_eta", m_el_eta)
m_el_sigd0PV = array.array('f',[0])
reader.AddVariable("m_el_sigd0PV", m_el_sigd0PV)
m_el_z0SinTheta = array.array('f', [0])
reader.AddVariable("m_el_z0SinTheta", m_el_z0SinTheta)
m_el_etcone20Dpt = array.array('f',[0])
reader.AddVariable("m_el_etcone20Dpt", m_el_etcone20Dpt)
m_el_ptcone20Dpt = array.array('f',[0])
reader.AddVariable("m_el_ptcone20Dpt", m_el_ptcone20Dpt)

# Download BDT weights
#reader.BookMVA("BDT","MVAnalysis_BDT.weights.xml")
reader.BookMVA("BDT",
    "/Users/musthero/Documents/Yura/Applications/koza4ok/test/ttH_Run1_LeptonID/weights/SKLearn_BDT_electons.weights.xml")

# Read ROOT file with the events to classify
input_filename = "/Users/musthero/Documents/Yura/Applications/TMVA-v4.2.0/test/output_electrons_fullsim_v5_20per.root"
file = ROOT.TFile.Open(input_filename)
if file.IsZombie():
    print "Root file is corrupt"

# Un-pickle classifier
fid = open('/Users/musthero/Documents/Yura/Applications/tmva_local/electrons_v5_VeryTightLH_20per.pkl', 'rb') 
bdt = cPickle.load(fid)

# Get a handle to the tree
t = file.JINRTree_3


# Numpy arrays
tmva_y_predicted = None  
sk_y_predicted = None 
y_test = None  

# List for numpy arrays
_tmva_y_predicted =[]  
_sk_y_predicted =[]  
_y_test = []


# Iterate over events in the JINRTree
c = 0
for event in t:
    c = c + 1
    if (c % 10000 == 0):
        print "Event number %i" % c
        sys.stdout.flush()

    if c == 20000: break

    if not event.m_el_VeryTightLH == 1 : continue

    m_el_pt[0] = event.m_el_pt 
    m_el_eta[0] = event.m_el_eta
    m_el_etcone20Dpt[0] = event.m_el_etcone20Dpt
    m_el_ptcone20Dpt[0] = event.m_el_ptcone20Dpt
    m_el_sigd0PV[0] = event.m_el_sigd0PV
    m_el_z0SinTheta[0] = event.m_el_z0SinTheta
    m_el_isprompt = event.m_el_isprompt


    # sklearn score
    score = bdt.predict([m_el_pt[0], m_el_eta[0], m_el_sigd0PV[0], m_el_z0SinTheta[0], 
        m_el_etcone20Dpt[0], m_el_ptcone20Dpt[0]])

    # save sklern score
    _sk_y_predicted.append(score)

    # calculate the value of the classifier with TMVA/TskMVA
    # Note: basically it is equaivalent to a signle-cut case 
    # on the BDT output score, i.e. bdtOutput = 0.0
    bdtOutput = reader.EvaluateMVA("BDT")
    score = 1 if bdtOutput > 0 else 0   # equivalent to bdt.predict()

    # save TMVA score
    _tmva_y_predicted.append(score)

    # save real score
    _y_test.append([m_el_isprompt])


file.Close()

# Obtain numpy arrays
sk_y_predicted = np.array(_sk_y_predicted)
tmva_y_predicted = np.array(_tmva_y_predicted)
y_test = np.array(_y_test)

print classification_report(y_test, sk_y_predicted, target_names=["background", "signal"])
print "Area under ROC curve: %.4f"%(roc_auc_score(y_test, sk_y_predicted))

# Calculate ROC curves
fpr_sk, tpr_sk, _ = roc_curve(y_test, sk_y_predicted)
fpr_tmva, tpr_tmva, _ = roc_curve(y_test, tmva_y_predicted)

# Draw ROC curves
plt.figure()

plt.plot(fpr_sk, tpr_sk, 'b-', label='scikit-learn bdt.predict()')
plt.plot(fpr_tmva, tpr_tmva, 'r--', label='TMVA reader.EvaluateMVA("BDT")')

plt.plot([0, 1], [0, 1], 'k--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Simple ROC-curve comparison')

plt.legend(loc="lower right")

plt.savefig("metrics_roc_curve.png", dpi=96)



