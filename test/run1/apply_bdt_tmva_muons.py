# Author: Yuriy Ilchenko (ilchenko@physics.utexas.edu)
# Apply TMVA BDT to an event to get a score 

import os
import sys

if os.environ['TERM'] == 'xterm':
    os.environ['TERM'] = 'vt100'
# Now it's OK to import readline :)
# Import ROOT libraries

import ROOT
from ROOT import TH1F
import array

from sklearn import datasets
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.metrics import classification_report, roc_auc_score, roc_curve

from sklearn import tree
import cPickle

histo_sk_sig=TH1F('histo_sk_sig', 'Muons: scikit-learn BDT score for signal', 200, -1.0, 1.0)
histo_sk_bkg=TH1F('histo_sk_bkg', 'Muons: scikit-learn BDT score for background', 200, -1, 1)
histo_tmva_sig=TH1F('histo_tmva_sig', 'Muons: TMVA/TskMVA BDT score for signal', 200, -1, 1)
histo_tmva_bkg=TH1F('histo_tmva_bkg', 'Muons: TMVA/TskMVA BDT score for background', 200, -1, 1)

reader = ROOT.TMVA.Reader()

m_mu_pt = array.array('f',[0])
reader.AddVariable("m_mu_pt", m_mu_pt)
m_mu_eta = array.array('f',[0])
reader.AddVariable("m_mu_eta", m_mu_eta)
m_mu_sigd0PV = array.array('f',[0])
reader.AddVariable("m_mu_sigd0PV", m_mu_sigd0PV)
m_mu_z0SinTheta = array.array('f', [0])
reader.AddVariable("m_mu_z0SinTheta", m_mu_z0SinTheta)
m_mu_etcone20Dpt = array.array('f',[0])
reader.AddVariable("m_mu_etcone20Dpt", m_mu_etcone20Dpt)
m_mu_ptcone20Dpt = array.array('f',[0])
reader.AddVariable("m_mu_ptcone20Dpt", m_mu_ptcone20Dpt)

# Download BDT weights
#reader.BookMVA("BDT","MVAnalysis_BDT.weights.xml")
reader.BookMVA("BDT",
    "/Users/musthero/Documents/Yura/Applications/koza4ok/test/ttH_Run1_LeptonID/weights/SKLearn_BDT_muons.weights.xml")

# Read ROOT file with the events to classify
input_filename = "/Users/musthero/Documents/Yura/Applications/TMVA-v4.2.0/test/output_muons_fullsim_v5_20per.root"
file = ROOT.TFile.Open(input_filename)
if file.IsZombie():
    print "Root file is corrupt"

# sklearn
fid = open('/Users/musthero/Documents/Yura/Applications/tmva_local/muons_v5_Tight_20per.pkl', 'rb') 
bdt = cPickle.load(fid)

# Get a handle to the tree
t = file.JINRTree_3

c = 0
for event in t:
    c = c + 1
    if (c % 10000 == 0):
        print "Event number %i" % c
        sys.stdout.flush()

    if c == 200000: break

    if not event.m_mu_Tight == 1 : continue

    m_mu_pt[0] = event.m_mu_pt 
    m_mu_eta[0] = event.m_mu_eta
    m_mu_etcone20Dpt[0] = event.m_mu_etcone20Dpt
    m_mu_ptcone20Dpt[0] = event.m_mu_ptcone20Dpt
    m_mu_sigd0PV[0] = event.m_mu_sigd0PV
    m_mu_z0SinTheta[0] = event.m_mu_z0SinTheta
    m_mu_isprompt = event.m_mu_isprompt


    # sklearn score
    #score = bdt.predict([m_mu_pt[0], m_mu_eta[0], m_mu_sigd0PV[0], m_mu_z0SinTheta[0], 
    #    m_mu_etcone20Dpt[0], m_mu_ptcone20Dpt[0]]).item(0)

    score = bdt.decision_function([m_mu_pt[0], m_mu_eta[0], m_mu_sigd0PV[0], m_mu_z0SinTheta[0], 
        m_mu_etcone20Dpt[0], m_mu_ptcone20Dpt[0]]).item(0)

    # calculate the value of the classifier with TMVA/TskMVA
    bdtOutput = reader.EvaluateMVA("BDT")

    if m_mu_isprompt == 0:
        histo_sk_bkg.Fill(score)
        histo_tmva_bkg.Fill(bdtOutput)
    elif m_mu_isprompt == 1:
        histo_sk_sig.Fill(score)
        histo_tmva_sig.Fill(bdtOutput)
    else:
        print "Warning: m_mu_isprompt is not 0 or 1!!!"

file.Close()


# Save histograms to file
output_filename = "/Users/musthero/Documents/Yura/Applications/tmva_local/BDT_score_distributions_muons.root"
output_file = ROOT.TFile(output_filename,"RECREATE")
histo_sk_sig.Write()
histo_sk_bkg.Write()
histo_tmva_sig.Write()
histo_tmva_bkg.Write()
output_file.Close()

