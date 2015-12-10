# Author: Yuriy Ilchenko (ilchenko@physics.utexas.edu)
# TProfile2D plot for BDT output scores

import os
import sys

if os.environ['TERM'] == 'xterm':
    os.environ['TERM'] = 'vt100'
# Now it's OK to import readline :)
# Import ROOT libraries

import ROOT
import array

reader = ROOT.TMVA.Reader()
m_el_pt = array.array('f',[0]); reader.AddVariable("m_el_pt", m_el_pt)
m_el_eta = array.array('f',[0]); reader.AddVariable("m_el_eta", m_el_eta)
m_el_phi = array.array('f',[0]); reader.AddVariable("m_el_phi", m_el_phi)
m_el_ptcone20_D_m_el_pt = array.array('f',[0]); reader.AddVariable("m_el_ptcone20/m_el_pt", m_el_ptcone20_D_m_el_pt)
m_el_etcone20_D_m_el_E = array.array('f',[0]); reader.AddVariable("m_el_etcone20/m_el_E", m_el_etcone20_D_m_el_E)
m_el_sigd0PV = array.array('f',[0]); reader.AddVariable("m_el_sigd0PV", m_el_sigd0PV)

# Download BDT weights
reader.BookMVA("BDT","MVAnalysis_BDT.weights.xml")

# create a new 2D profile
#profile2D = ROOT.TProfile2D("profile2d", "Electron BDT output in ptcone20 vs pt (prompt electrons)", 250, 0, 250, 100, 0, 10)
profile2D = ROOT.TProfile2D("profile2d", "Electron BDT output in ptcone20/pt vs pt (non-prompt electrons)", 250, 0, 250, 100, 0, 1)
profile2D.SetXTitle("Electron pt")
profile2D.SetYTitle("ptcone20")
#profile2D.SetYTitle("ptcone20/pt")
profile2D.SetErrorOption("s")

# Read ROOT file with the events to classify
input_filename = "output_electrons_0.root"
file = ROOT.TFile.Open(input_filename)
if file.IsZombie():
    print "Root file is corrupt"

# Get a handle to the tree
t = file.JINRTree

c = 0
for event in t:
    c = c + 1
    if (c % 10000 == 0):
        print "Event number %i" % c
        sys.stdout.flush()

    if not event.m_el_VeryTightLH == 1 : continue
    # Choose: signal or background
    #if not event.m_el_isprompt == 1 : continue
    if event.m_el_isprompt == 1 : continue

    m_el_pt[0] = event.m_el_pt 
    m_el_eta[0] = event.m_el_eta
    m_el_phi[0] = event.m_el_phi
    m_el_ptcone20_D_m_el_pt[0] = event.m_el_ptcone20/event.m_el_pt
    m_el_etcone20_D_m_el_E[0] = event.m_el_etcone20/event.m_el_E
    m_el_sigd0PV[0] = event.m_el_sigd0PV

    # calculate the value of the classifier
    bdtOutput = reader.EvaluateMVA("BDT")
    #profile2D.Fill(m_el_pt[0], event.m_el_etcone20, bdtOutput, 1)
    profile2D.Fill(m_el_pt[0], event.m_el_etcone20/m_el_pt[0], bdtOutput, 1)
         

#profile2D.Draw("colz")

file.Close()

# Save profile2D to root file
output_filename = "bdt_score_profile2d.root"
out_file = ROOT.TFile.Open(output_filename, "RECREATE")
profile2D.Write()
out_file.Close()


