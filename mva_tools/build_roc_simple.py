import sys
from array import array
import numpy as np

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
    #g.SetLineColor(ROOT.kRed)
    g.SetTitle("ROC curve")
    

    return g
    
    #print nbins_bkg

def column_or_1d(y):
    shape = np.shape(y)
    if len(shape) == 1:
        return np.ravely(y)
    if len(shape) == 2 and shape[1] == 1:
        return np.ravel(y)


def roc_curve_sk(y_test, sk_y_predicted, step = 0.001):

    pos_label = 1 # prompt lepton
    neg_label = 0 # non-prompt lepton

    y_test = column_or_1d(y_test)

    assert y_test.size == sk_y_predicted.size, "Error: len(y_test) != len(sk_y_predicted)"
    assert np.unique(y_test).size == 2, "Error: number of classes is %i. Expected 2 classes only." % np.unique(y_test).size

    # calculate number of prompt and non-prompt leptons
    num_prompts = np.sum(y_test == pos_label)
    num_nonprompts = y_test.size - num_prompts

    # array of probability cut values 
    # minimum probability is 0, maximum is one, 
    # and step is defind above
    cuts = np.arange(0, 1, step)

    tpr = []
    fpr = []

    for cut in cuts:
        prompts_passed = 0
        nonprompts_passed = 0

        indxs = np.where(sk_y_predicted >= cut)
        y_test_passed = np.take(y_test, indxs)
        prompts_passed = np.sum(y_test_passed == pos_label)
        nonprompts_passed = np.sum(y_test_passed == neg_label)
        
        tpr.append(float(prompts_passed)/num_prompts)
        fpr.append(float(nonprompts_passed)/num_nonprompts)

    return np.array(fpr), np.array(tpr), 0


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



