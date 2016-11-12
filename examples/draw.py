# Author: Yuriy Ilchenko (ilchenko@physics.utexas.edu)
# Compare two ROC curves from scikit-learn and from TMVA (using skTMVA converter)

import os
import sys

if os.environ['TERM'] == 'xterm':
    os.environ['TERM'] = 'vt100'
# Now it's OK to import readline :)
# Import ROOT libraries

import ROOT
import array


from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.metrics import roc_curve

from sklearn import tree
import cPickle

import numpy as np
from numpy.random import RandomState

RNG = RandomState(45)

# Construct an example dataset for binary classification
n_vars = 2
n_events = 300
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

# Some print-out
print "Event numbers total:", 2 * n_events

# Plot the testing points
c1 = ROOT.TCanvas("c1","Testing Dataset",200,10,700,500)
c1.cd()
plot_colors = (ROOT.kRed, ROOT.kBlue)
mg = ROOT.TMultiGraph()
for i, n, c in zip([-1, 1], ('Class A', 'Class B'), plot_colors):
    idx = np.where(y == i)

    n = len(idx[0])
    g = ROOT.TGraph(n,X[idx, 0][0],X[idx, 1][0])

    g.SetMarkerColor(c)
    g.SetMarkerStyle(8)
    g.SetMarkerSize(0.5)

    mg.Add(g)
 
mg.Draw("ap p")
mg.SetTitle("Testing dataset")
mg.GetXaxis().SetTitle("var1")
mg.GetYaxis().SetTitle("var2")

c1.Update()
c1.Modified()


# Use all dataset for testing
X_test, y_test, w_test = X, y, w

# sklearn, get BDT from pickle file
fid = open('bdt_sklearn_to_tmva_example.pkl', 'rb') 
bdt = cPickle.load(fid)

# create TMVA reader
reader = ROOT.TMVA.Reader()

var1 = array.array('f',[0.])
reader.AddVariable("var1", var1)
var2 = array.array('f',[0.])
reader.AddVariable("var2", var2)

# TMVA, get BDT from the xml file
reader.BookMVA("BDT", "bdt_sklearn_to_tmva_example.xml")

# List for numpy arrays
sk_y_predicted =[]  
tmva_y_predicted =[]  

# Number of events
n = X.shape[0]

# Iterate over events
# Note: this is not the fastest way for sklearn
#        but most representative, I believe
for i in xrange(n):

    if (i % 100 == 0) and (i != 0):
        print "Event %i" % i

    var1[0] = X.item((i,0))
    var2[0] = X.item((i,1))

    # sklearn score
    score = bdt.decision_function([var1[0], var2[0]]).item(0)

    # calculate the value of the classifier with TMVA/TskMVA
    bdtOutput = reader.EvaluateMVA("BDT")

    # save skleanr and TMVA BDT output scores
    sk_y_predicted.append(score)
    tmva_y_predicted.append(bdtOutput)


# Convert arrays to numpy arrays
sk_y_predicted = np.array(sk_y_predicted)
tmva_y_predicted = np.array(tmva_y_predicted)

# Calculate ROC curves
fpr_sk, tpr_sk, _ = roc_curve(y_test, sk_y_predicted)
fpr_tmva, tpr_tmva, _ = roc_curve(y_test, tmva_y_predicted)

# Derive signal efficiencies and background rejections
# for sklearn and TMVA
sig_eff_sk = array.array('f', [rate for rate in tpr_sk])
bkg_rej_sk = array.array('f',[ (1-rate) for rate in fpr_sk])
sig_eff_tmva = array.array('f', [rate for rate in tpr_tmva])
bkg_rej_tmva = array.array('f',[ (1-rate) for rate in fpr_tmva])

# Stack for keeping plots
#plots = []

c2 = ROOT.TCanvas("c2","A Simple Graph Example",200,10,700,500)
c2.cd()

# Draw ROC-curve for sklearn
g1 = ROOT.TGraph(len(sig_eff_sk), sig_eff_sk, bkg_rej_sk)
g1.GetXaxis().SetRangeUser(0.0,1.0)
g1.GetYaxis().SetRangeUser(0.0,1.0)
g1.SetName("g1")
g1.SetTitle("ROC curve")

g1.SetLineStyle(3)
g1.SetLineColor(ROOT.kBlue) 
g1.Draw("AL") # draw TGraph with no marker dots

# Draw ROC-curve for skTMVA
g2 = ROOT.TGraph(len(fpr_tmva), sig_eff_tmva, bkg_rej_tmva)
g2.GetXaxis().SetRangeUser(0.0,1.0)
g2.GetYaxis().SetRangeUser(0.0,1.0)
g2.SetName("g2")
g2.SetTitle("ROC curve")

g2.SetLineStyle(7)
g2.SetLineColor(ROOT.kRed)
g2.Draw("SAME") # draw TGraph with no marker dots

leg = ROOT.TLegend(0.4,0.35,0.7,0.2)
#leg.SetHeader("ROC curve")
leg.AddEntry("g1","sklearn","l")
leg.AddEntry("g2","skTMVA","l")
leg.Draw()

c2.Update()
c2.Modified()

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




