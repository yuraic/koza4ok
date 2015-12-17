# Author: Yuriy Ilchenko (ilchenko@physics.utexas.edu)
# Compare skTMVA and scikit-learn ROC-curves

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

from sklearn import datasets
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.metrics import classification_report, roc_auc_score, roc_curve

from sklearn import tree
import cPickle

from mva_tools.build_roc_simple import build_roc 

histo_sk_sig=TH1F('histo_sk_sig', 'Electrons: scikit-learn BDT score for signal', 200, -1.0, 1.0)
histo_sk_bkg=TH1F('histo_sk_bkg', 'Electrons: scikit-learn BDT score for background', 200, -1, 1)
histo_tmva_sig=TH1F('histo_tmva_sig', 'Electrons: TMVA/TskMVA BDT score for signal', 200, -1, 1)
histo_tmva_bkg=TH1F('histo_tmva_bkg', 'Electrons: TMVA/TskMVA BDT score for background', 200, -1, 1)

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

# sklearn
fid = open('/Users/musthero/Documents/Yura/Applications/tmva_local/electrons_v5_VeryTightLH_20per.pkl', 'rb') 
bdt = cPickle.load(fid)

# Get a handle to the tree
t = file.JINRTree_3

X_test = None
_X_test =[]
y_test = None
_y_test = []

c = 0
for event in t:
    c = c + 1
    if (c % 10000 == 0):
        print "Event number %i" % c
        sys.stdout.flush()

    if c == 200000: break

    if not event.m_el_VeryTightLH == 1 : continue

    m_el_pt[0] = event.m_el_pt 
    m_el_eta[0] = event.m_el_eta
    m_el_etcone20Dpt[0] = event.m_el_etcone20Dpt
    m_el_ptcone20Dpt[0] = event.m_el_ptcone20Dpt
    m_el_sigd0PV[0] = event.m_el_sigd0PV
    m_el_z0SinTheta[0] = event.m_el_z0SinTheta
    m_el_isprompt = event.m_el_isprompt


    # Most straight-forward way to get roc-curve
    # Commented out to use an alternative method by deriving tpr and tnr
    #score = bdt.decision_function([m_el_pt[0], m_el_eta[0], m_el_sigd0PV[0], m_el_z0SinTheta[0], 
    #    m_el_etcone20Dpt[0], m_el_ptcone20Dpt[0]]).item(0)

    _X_test.append([m_el_pt[0], m_el_eta[0], m_el_sigd0PV[0], m_el_z0SinTheta[0], m_el_etcone20Dpt[0], m_el_ptcone20Dpt[0]])
    _y_test.append([m_el_isprompt])
    

    # calculate the value of the classifier with TMVA/TskMVA
    bdtOutput = reader.EvaluateMVA("BDT")


    if m_el_isprompt == 0:
        histo_tmva_bkg.Fill(bdtOutput)
    elif m_el_isprompt == 1:
        histo_tmva_sig.Fill(bdtOutput)
    else:
        print "Warning: m_mu_isprompt is not 0 or 1!!!"

file.Close()

X_test = np.array(_X_test)
y_test = np.array(_y_test)

# sklearn tpr and tpr
sk_y_predicted = bdt.predict_proba(X_test)[:, 1]
fpr, tpr, _ = roc_curve(y_test, sk_y_predicted)

sig_eff = array.array('f', [rate for rate in tpr])
bkg_rej = array.array('f',[ (1-rate) for rate in fpr])

# roc_curve_sk() - skTMVA version of roc_curve
from mva_tools.build_roc_simple import roc_curve_sk
fpr_comp, tpr_comp, _ = roc_curve_sk(y_test, sk_y_predicted)


sig_eff_comp = array.array('f', [rate for rate in tpr_comp])
bkg_rej_comp = array.array('f',[ (1-rate) for rate in fpr_comp])


# Stack for keeping plots
plots = []

# Getting ROC-curve for skTMVA
g1 = build_roc(histo_tmva_sig, histo_tmva_bkg)
g1.SetName("g1")
g1.SetTitle("skTMVA ROC curve [electrons]")
plots.append(g1)

g1.SetLineColor(8) # Green color
g1.Draw("AL") # draw TGraph with no marker dots

# Getting ROC-curve for sklearn
g2 = ROOT.TGraph(len(tpr), sig_eff, bkg_rej)
g2.GetXaxis().SetRangeUser(0.0,1.0)
g2.GetYaxis().SetRangeUser(0.0,1.0)
g2.SetName("g2")
g2.SetTitle("scikitlearn ROC curve [electrons]")
plots.append(g2)

g2.SetLineStyle(7)
g2.SetLineColor(ROOT.kRed)
g2.Draw("SAME") # draw TGraph with no marker dots

# Getting ROC curve from roc_curve_sk (skTMVA implementation of scikitlearn roc_curve method)
g3 = ROOT.TGraph(len(tpr_comp), sig_eff_comp, bkg_rej_comp)
g3.GetXaxis().SetRangeUser(0.0,1.0)
g3.GetYaxis().SetRangeUser(0.0,1.0)
g3.SetName("g3")
g3.SetTitle("skTMVA version of ROC curve [electrons]")
plots.append(g3)

g3.SetLineStyle(3)
g3.SetLineColor(ROOT.kBlue) 
g3.Draw("SAME") # draw TGraph with no marker dots



# Draw rectangular cuts

eff_rej = (0.889199,0.898912,0.000337,0.001671)
sig_eff_val = array.array('f', [eff_rej[0]])
sig_eff_err = array.array('f', [eff_rej[1]])
bkg_rej_val = array.array('f', [eff_rej[2]])
bkg_rej_err = array.array('f', [eff_rej[3]])


n = 1
#gr = TGraphErrors(n, sig_eff_val, sig_eff_err, bkg_rej_val, bkg_rej_err)
#gr = TGraphErrors(n, sig_eff_val, sig_eff_err, bkg_rej_val, bkg_rej_err)
gr = ROOT.TGraphErrors(n, sig_eff_val, sig_eff_err, bkg_rej_val, bkg_rej_err)
print sig_eff_val, sig_eff_err, bkg_rej_val, bkg_rej_err
#gr.Draw("AC*")
gr.SetMarkerColor(2)
gr.SetLineColor(2)
gr.SetLineWidth(2)
 
gr.Draw("psame")
