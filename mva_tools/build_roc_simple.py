import sys
from array import array

import ROOT

from ROOT import TH1F

xrange_bins = lambda nbins: xrange(1, nbins+1)

def build_roc(h_sig, h_bkg, verbose=0):

    nbins_sig = h_sig.GetXaxis().GetNbins()
    nbins_bkg = h_bkg.GetXaxis().GetNbins()
    nbins = nbins_sig if nbins_sig == nbins_bkg else -1
    #print nbins
    if nbins < 0.0:
        sys.exit("Error: nbins_sig != nbins_bkg")

    min_val = h_sig.GetXaxis().GetXmin()
    max_val = h_sig.GetXaxis().GetXmax()

    step = float(max_val - min_val)/(nbins-1)
    sig_eff = array('f', [])
    bkg_rej = array('f', [])

    total_sig = h_sig.Integral()
    total_bkg = h_bkg.Integral()
    print total_sig
    print total_bkg

    sig_rejected = 0.0
    bkg_rejected = 0.0
    for i in xrange_bins(nbins):
        sig_rejected += h_sig.GetBinContent(i)
        #print sig_rejected
        bkg_rejected += h_bkg.GetBinContent(i)
        #print bkg_rejected

        seff = float(total_sig-sig_rejected)/total_sig
        brej = float(bkg_rejected)/total_bkg
        #print seff, brej
        sig_eff.append(seff)
        bkg_rej.append(brej) 

        if verbose == 1:
            bdt_score = min_val + i * step
            print "bdt score =", bdt_score, "sig_eff =", seff 
        
        #bin_sig = h_sig.GetBinContent()
    print "Overflow =", h_sig.GetBinContent(nbins_sig+1)
    print "Underflow =", h_sig.GetBinContent(0)

    g = ROOT.TGraph(nbins, sig_eff, bkg_rej)
    g.GetXaxis().SetRangeUser(0.0,1.0)
    g.GetYaxis().SetRangeUser(0.0,1.0)
    #g.Draw("AC")
    g.SetLineColor(ROOT.kRed)
    g.SetTitle("ROC curve")
    

    return g
    
    #print nbins_bkg


if __name__ == "__main__":
    path = "/Users/musthero/Documents/Yura/Applications/tmva_local/BDT_score_distributions_electrons.root"
    histo_sk_sig = "histo_sk_sig"
    histo_sk_bkg = "histo_sk_bkg"

    rootfile = ROOT.TFile.Open(path)

    if rootfile.IsZombie():
        print "Root file is corrupt"

    h_sig = rootfile.Get(histo_sk_sig)
    h_bkg = rootfile.Get(histo_sk_bkg)

    g = build_roc(h_sig, h_bkg)
    ll = [g]

    g.Draw("AL") # draw TGraph with no marker dots



