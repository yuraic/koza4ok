import ROOT

from ROOT import TGraphErrors
from array import array

from mva_tools.build_roc_simple import build_roc 


if __name__ == "__main__":

    path = "/Users/musthero/Documents/Yura/Applications/tmva_local/BDT_score_distributions_muons.root"
    hsig_skTMVA_path = "histo_tmva_sig"
    hbkg_skTMVA_path = "histo_tmva_bkg"
    hsig_sklearn_path = "histo_sk_sig"
    hbkg_sklearn_path = "histo_sk_bkg"

    rootfile = ROOT.TFile.Open(path)

    if rootfile.IsZombie():
        print "Root file is corrupt"

    hSig_skTMVA = rootfile.Get(hsig_skTMVA_path)
    hBkg_skTMVA = rootfile.Get(hbkg_skTMVA_path)
    hSig_sklearn = rootfile.Get(hsig_sklearn_path)
    hBkg_sklearn = rootfile.Get(hbkg_sklearn_path)



    # Stack for keeping plots
    plots = []

    # Getting ROC-curve for skTMVA
    g1 = build_roc(hSig_skTMVA, hBkg_skTMVA)
    g1.SetName("g1")
    g1.SetTitle("ROC curve [muons]")
    plots.append(g1)

    g1.SetLineColor(ROOT.kBlue)
    g1.Draw("AL") # draw TGraph with no marker dots

    # Getting ROC-curve for sklearn
    g2 = build_roc(hSig_sklearn, hBkg_sklearn)
    g2.SetName("g2")
    g2.SetTitle("ROC curve [muons]")
    plots.append(g2)

    g2.SetLineStyle(7)
    g2.SetLineColor(ROOT.kRed)
    g2.Draw("SAME") # draw TGraph with no marker dots

    leg = ROOT.TLegend(0.1,0.5,0.3,0.4)
    #leg.SetHeader("ROC curve")
    leg.AddEntry("g1","skTMVA","l")
    leg.AddEntry("g2","sklearn","l")
    leg.Draw()





