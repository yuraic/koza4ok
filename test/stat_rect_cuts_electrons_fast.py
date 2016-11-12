import ROOT
import sys

from math import *
from array import *

filename = "/Users/musthero/Documents/Yura/Applications/TMVA-v4.2.0/test/output_electrons_v2_25per.root"

profile = ROOT.TProfile("RECTCuts", "RECTCuts", 100, 0, 1, "s");

# Get TTree
file = ROOT.TFile.Open(filename)
tree = file.JINRTree2_el2

# Declare variables of interest
m_el_pass_Loose_Triggers = array('i', [0])
m_el_pt = array('f',[0])
m_el_eta = array('f',[0])
m_el_sigd0PV = array('f',[0])
m_el_z0SinTheta = array('f',[0])
m_el_topoetcone20_pt = array('f',[0])
m_el_ptvarcone20_pt = array('f',[0])
m_el_isTightLH = array('i',[0])
m_el_truthOrigin = array('i', [0])
m_el_isolationFixedCutTight = array('i', [0])

# Training

# Link variables of interest to the tree
tree.SetBranchAddress( "m_el_pt", m_el_pt )
tree.SetBranchAddress( "m_el_eta", m_el_eta )
tree.SetBranchAddress( "m_el_sigd0PV", m_el_sigd0PV )
tree.SetBranchAddress( "m_el_z0SinTheta", m_el_z0SinTheta )
tree.SetBranchAddress( "m_el_topoetcone20_pt", m_el_topoetcone20_pt )
tree.SetBranchAddress( "m_el_ptvarcone20_pt", m_el_ptvarcone20_pt )
tree.SetBranchAddress( "m_el_isTightLH", m_el_isTightLH )
tree.SetBranchAddress( "m_el_truthOrigin", m_el_truthOrigin )
tree.SetBranchAddress( "m_el_pass_Loose_Triggers", m_el_pass_Loose_Triggers )
tree.SetBranchAddress( "m_el_isolationFixedCutTight", m_el_isolationFixedCutTight )

# Declare counting variables
prompt_all = 0; prompt_pass = 0;
nonprompt_all = 0; nonprompt_pass = 0; nonprompt_rej = 0;

c = 0
#for e in file.JINRTree:
while tree.GetEntry(c):
    c = c + 1

    if (c % 100000 == 0):
        print "Event number %i" % c
        sys.stdout.flush()

    if not (m_el_isTightLH[0]==1 and m_el_pass_Loose_Triggers[0]==1): 
        continue


    isprompt = 1 if m_el_truthOrigin[0] in (12, ) else 0
    # if m_el_truthOrigin[0] in (12, ):    # WBoson        = 12
    #    isprompt = 1
    # elif m_el_truthOrigin[0] in (26, ):  # BottomMeson   = 26
    #    isprompt = 0
    # else:
    #    isprompt = -1
    # if isprompt < 0: continue

    prompt_all += 1 if isprompt == 1 else 0
    nonprompt_all += 1 if isprompt == 0 else 0


    # Apply standard cuts
    if m_el_z0SinTheta[0] < 0.5 and m_el_sigd0PV[0] < 5 and m_el_isolationFixedCutTight[0] == 1:
        prompt_pass += 1 if isprompt == 1 else 0
        nonprompt_pass += 1 if isprompt == 0 else 0


    #print "Unable to figure out lepton type (prompt/non-prompt)"
    #ROOT.gApplication.Terminate()

nonprompt_rej = nonprompt_all - nonprompt_pass
sig_eff_val = float(prompt_pass)/prompt_all
sig_eff_err = (1/float(prompt_all))*sqrt(prompt_pass*(1-float(prompt_pass)/prompt_all))
bkg_rej_val = float(nonprompt_rej)/nonprompt_all
bkg_rej_err = (1/float(nonprompt_all))*sqrt(nonprompt_rej*(1-float(nonprompt_rej)/nonprompt_all))

print filename,":"
print "    Sig eff:", sig_eff_val
print "    Sig eff error:", sig_eff_err
print "    Bkg rej:", bkg_rej_val
print "    Bkg rej error:", bkg_rej_err
print "    Prompt all,pass:", prompt_all,prompt_pass
print "    Non-prompt all,rej:", nonprompt_all,nonprompt_rej

print "(%f,%f,%f,%f)" % (sig_eff_val, bkg_rej_val, sig_eff_err, bkg_rej_err)

profile.Fill(sig_eff_val, bkg_rej_val, 1)
file.Close()

profile.SetLineColor(2)
profile.SetLineWidth(6)
profile.Draw()

