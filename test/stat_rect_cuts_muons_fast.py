import ROOT
import sys

from math import *
from array import *

#filelist = [ "/Users/musthero/Documents/Yura/Applications/tmva_local/output_muons_0.root" ] 
#filelist = [ "/Users/musthero/Documents/Yura/Applications/tmva_local/output_muons_test.root" ] 
filelist = [ "/Users/musthero/Documents/Yura/Applications/TMVA-v4.2.0/test/output_muons_fullsim_v5_20per.root" ]


profile = ROOT.TProfile("RECTCuts", "RECTCuts", 100, 0, 1, "s");

for filename in filelist:

    # Get TTree
    file = ROOT.TFile.Open(filename)
    tree = file.JINRTree_3

    # Declare counting variables
    prompt_all = 0; prompt_pass = 0;
    nonprompt_all = 0; nonprompt_pass = 0; nonprompt_rej = 0;
    
    # Declare variables of interest
    m_mu_ptcone20Dpt = array('f',[0])
    m_mu_etcone20Dpt = array('f',[0])
    m_mu_isprompt = array('i', [0])
    m_mu_Tight = array('i',[0])
    m_mu_screwed_isprompt = array('i',[0])
    m_mu_MuIso = array('i',[0])
    m_mu_Z0SinTheta = array('i',[0])
    m_mu_Sigd0PV = array('i',[0])

    # Link variables of interest to the tree
    tree.SetBranchAddress( "m_mu_ptcone20Dpt", m_mu_ptcone20Dpt )
    tree.SetBranchAddress( "m_mu_etcone20Dpt", m_mu_etcone20Dpt )
    tree.SetBranchAddress( "m_mu_Tight", m_mu_Tight )
    tree.SetBranchAddress( "m_mu_isprompt", m_mu_isprompt )
    tree.SetBranchAddress( "m_mu_screwed_isprompt", m_mu_screwed_isprompt )
    tree.SetBranchAddress( "m_mu_MuIso", m_mu_MuIso )
    tree.SetBranchAddress( "m_mu_Z0SinTheta", m_mu_Z0SinTheta )
    tree.SetBranchAddress( "m_mu_Sigd0PV", m_mu_Sigd0PV )

    c = 0
    #for e in file.JINRTree:
    while tree.GetEntry(c):
        c = c + 1

        if (c % 100000 == 0):
            print "Event number %i" % c
            sys.stdout.flush()

        # Preselection cuts
        #if m_mu_isprompt[0] == 1 and m_mu_Tight[0] == 1 and m_mu_screwed_isprompt[0] == 0:    # Signal (take from TCut in TMVAMuon.C for signal):
        if m_mu_isprompt[0] == 1 and m_mu_Tight[0] == 1:    # Signal (take from TCut in TMVAMuon.C for signal):
            prompt_all += 1
        #elif m_mu_isprompt[0] == 0 and m_mu_Tight[0] == 1 and m_mu_screwed_isprompt[0] == 0:  # Background (take from TCut in TMVAMuon.C for background):
        elif m_mu_isprompt[0] == 0 and m_mu_Tight[0] == 1:  # Background (take from TCut in TMVAMuon.C for background):
            nonprompt_all += 1
        else:
            continue

        # Standard selection cuts
        if m_mu_Tight[0] == 1 and m_mu_MuIso[0] == 1 and m_mu_Z0SinTheta[0] == 1 and m_mu_Sigd0PV[0] == 1:
            if m_mu_isprompt[0] == 1:
                prompt_pass += 1
            elif m_mu_isprompt[0] == 0:
                nonprompt_pass += 1
            else:
                print "Unable to figure out lepton type (prompt/non-prompt)"
                ROOT.gApplication.Terminate()

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

