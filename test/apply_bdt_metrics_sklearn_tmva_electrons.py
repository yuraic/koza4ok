# Author: Yuriy Ilchenko (ilchenko@physics.utexas.edu)
# Compare two ROC curves from scikit-learn and from TMVA (using skTMVA converter)

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
#import matplotlib.pyplot as plt

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
    #"/Users/musthero/Documents/Yura/Applications/tmva_local/my.xml")

# Read ROOT file with the events to classify
input_filename = "/Users/musthero/Documents/Yura/Applications/TMVA-v4.2.0/test/output_electrons_fullsim_v5_20per.root"
file = ROOT.TFile.Open(input_filename)
if file.IsZombie():
    print "Root file is corrupt"

# sklearn
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

c = 0
for event in t:
    c = c + 1
    if (c % 10000 == 0):
        print "Event number %i" % c
        sys.stdout.flush()

    if c == 2000: break

    if not event.m_el_VeryTightLH == 1 : continue

    m_el_pt[0] = event.m_el_pt 
    m_el_eta[0] = event.m_el_eta
    m_el_etcone20Dpt[0] = event.m_el_etcone20Dpt
    m_el_ptcone20Dpt[0] = event.m_el_ptcone20Dpt
    m_el_sigd0PV[0] = event.m_el_sigd0PV
    m_el_z0SinTheta[0] = event.m_el_z0SinTheta
    m_el_isprompt = event.m_el_isprompt

    # sklearn score
    score = bdt.decision_function([m_el_pt[0], m_el_eta[0], m_el_sigd0PV[0], m_el_z0SinTheta[0], 
        m_el_etcone20Dpt[0], m_el_ptcone20Dpt[0]]).item(0)
    
    # save sklearn score
    _sk_y_predicted.append(score)

    # calculate the value of the classifier with TMVA/TskMVA
    bdtOutput = reader.EvaluateMVA("BDT")

    # save TMVA score
    _tmva_y_predicted.append(bdtOutput)

    # save real score
    _y_test.append([m_el_isprompt])

file.Close()

# Obtain numpy arrays
sk_y_predicted = np.array(_sk_y_predicted)
tmva_y_predicted = np.array(_tmva_y_predicted)
y_test = np.array(_y_test)

# Calculate ROC curves
# NOTE: looking in the scikit learn internals,
# the trick is that metrics.roc_curve is insenstive to
# whether you provide it with probability or output bdt score. 
# This makes things a lot more easier.
fpr_sk, tpr_sk, _ = roc_curve(y_test, sk_y_predicted)
fpr_tmva, tpr_tmva, _ = roc_curve(y_test, tmva_y_predicted)

sig_eff_sk = array.array('f', [rate for rate in tpr_sk])
bkg_rej_sk = array.array('f',[ (1-rate) for rate in fpr_sk])

sig_eff_tmva = array.array('f', [rate for rate in tpr_tmva])
bkg_rej_tmva = array.array('f',[ (1-rate) for rate in fpr_tmva])

# Stack for keeping plots
plots = []

# Getting ROC-curve for sklearn
g1 = ROOT.TGraph(len(sig_eff_sk), sig_eff_sk, bkg_rej_sk)
g1.GetXaxis().SetRangeUser(0.0,1.0)
g1.GetYaxis().SetRangeUser(0.0,1.0)
g1.SetName("g1")
g1.SetTitle("scikit-learn")
plots.append(g1)

g1.SetLineStyle(3)
g1.SetLineColor(ROOT.kBlue) 
g1.Draw("AL") # draw TGraph with no marker dots

# Getting ROC-curve for skTMVA
g2 = ROOT.TGraph(len(fpr_tmva), sig_eff_tmva, bkg_rej_tmva)
g2.GetXaxis().SetRangeUser(0.0,1.0)
g2.GetYaxis().SetRangeUser(0.0,1.0)
g2.SetName("g2")
g2.SetTitle("skTMVA")
plots.append(g2)

g2.SetLineStyle(7)
g2.SetLineColor(ROOT.kRed)
g2.Draw("SAME") # draw TGraph with no marker dots

## Draw ROC curves
#plt.figure()
#
#plt.plot(fpr_sk, tpr_sk, 'b-', label='scikit-learn bdt.predict()')
#plt.plot(fpr_tmva, tpr_tmva, 'r--', label='TMVA reader.EvaluateMVA("BDT")')
#
#plt.plot([0, 1], [0, 1], 'k--')
#plt.xlim([0.0, 1.0])
#plt.ylim([0.0, 1.05])
#plt.xlabel('False Positive Rate')
#plt.ylabel('True Positive Rate')
#plt.title('Simple ROC-curve comparison')
#
#plt.legend(loc="lower right")
#
#plt.savefig("roc_bdt_curves.png", dpi=96)
