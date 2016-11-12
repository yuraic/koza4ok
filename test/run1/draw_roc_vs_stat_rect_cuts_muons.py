import ROOT

from ROOT import TGraphErrors
from array import array

from mva_tools.build_roc_simple import build_roc 


if __name__ == "__main__":

    path = "/Users/musthero/Documents/Yura/Applications/tmva_local/BDT_score_distributions_muons.root"
    hsig_path = "histo_tmva_sig"
    hbkg_path = "histo_tmva_bkg"

    rootfile = ROOT.TFile.Open(path)

    if rootfile.IsZombie():
        print "Root file is corrupt"

    hSig = rootfile.Get(hsig_path)
    hBkg = rootfile.Get(hbkg_path)

    g = build_roc(hSig, hBkg, 1)
    ll = [g]

    g.SetLineColor(ROOT.kBlue)
    g.Draw("AL") # draw TGraph with no marker dots


    # Draw rectangular cuts


    eff_rej = (0.905108,0.987200,0.000272,0.000172)
    sig_eff_val = array('f', [eff_rej[0]])
    sig_eff_err = array('f', [eff_rej[1]])
    bkg_rej_val = array('f', [eff_rej[2]])
    bkg_rej_err = array('f', [eff_rej[3]])


    n = 1
    #gr = TGraphErrors(n, sig_eff_val, sig_eff_err, bkg_rej_val, bkg_rej_err)
    #gr = TGraphErrors(n, sig_eff_val, sig_eff_err, bkg_rej_val, bkg_rej_err)
    gr = TGraphErrors(n, sig_eff_val, sig_eff_err, bkg_rej_val, bkg_rej_err)
    print sig_eff_val, sig_eff_err, bkg_rej_val, bkg_rej_err
    #gr.Draw("AC*")
    gr.SetMarkerColor(2)
    gr.SetLineColor(2)
    gr.SetLineWidth(2)
     
    gr.Draw("psame")





