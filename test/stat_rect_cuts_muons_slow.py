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

    c = 0
    for e in file.JINRTree:
        c = c + 1

        if (c % 100000 == 0):
            print "Event number %i" % c
            sys.stdout.flush()

        m_mu_isprompt = e.m_mu_isprompt
        m_mu_Tight = e.m_mu_Tight
        m_mu_screwed_isprompt = e.m_mu_screwed_isprompt        
        m_mu_MuIso = e.m_mu_MuIso
        m_mu_Z0SinTheta = e.m_mu_Z0SinTheta
        m_mu_Sigd0PV = e.m_mu_Sigd0PV

        # Preselection cuts
        #if m_mu_isprompt == 1 and m_mu_Tight == 1 and m_mu_screwed_isprompt == 0:    # Signal (take from TCut in TMVAMuon.C for signal):
        if m_mu_isprompt == 1 and m_mu_Tight == 1:    # Signal (take from TCut in TMVAMuon.C for signal):
            prompt_all += 1
        #elif m_mu_isprompt == 0 and m_mu_Tight == 1 and m_mu_screwed_isprompt == 0:  # Background (take from TCut in TMVAMuon.C for background):
        elif m_mu_isprompt == 0 and m_mu_Tight == 1:  # Background (take from TCut in TMVAMuon.C for background):            
            nonprompt_all += 1
        else:
            continue

        # Standard selection cuts
        if m_mu_Tight == 1 and m_mu_MuIso == 1 and m_mu_Z0SinTheta == 1 and m_mu_Sigd0PV == 1:
            if m_mu_isprompt == 1:
                prompt_pass += 1
            elif m_mu_isprompt == 0:
                nonprompt_pass += 1
            else:
                print "Unable to figure out lepton type (prompt/non-prompt)"
                ROOT.gApplication.Terminate()

    nonprompt_rej = nonprompt_all - nonprompt_pass
    sig_eff = float(prompt_pass)/prompt_all
    bkg_rej = float(nonprompt_rej)/nonprompt_all
    print filename,":"
    print "    Sig eff:", sig_eff
    print "    Sig eff error:", (1/float(prompt_all))*sqrt(prompt_pass*(1-float(prompt_pass)/prompt_all))
    print "    Bkg rej:", bkg_rej
    print "    Bkg rej error:", (1/float(nonprompt_all))*sqrt(nonprompt_rej*(1-float(nonprompt_rej)/nonprompt_all))
    print "    Prompt all,pass:", prompt_all,prompt_pass
    print "    Non-prompt all,rej:", nonprompt_all,nonprompt_rej
    
    profile.Fill(sig_eff, bkg_rej, 1)
    file.Close()

profile.SetLineColor(2)
profile.SetLineWidth(6)
profile.Draw()

