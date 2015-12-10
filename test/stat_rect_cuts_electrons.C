{
    using namespace std;


    //TFile *f = new TFile("/Users/musthero/Documents/Yura/Applications/tmva_local/output_muons_test.root");
    //TTree *tree = (TTree*)f->Get("JINRTree");
    
    /*
    TFile *f = new TFile("/Users/musthero/Documents/Yura/Applications/TMVA-v4.2.0/test/output_muon_fullsim_10per.root");
    TTree *tree = (TTree*)f->Get("JINRTree_testing");
    */

    TFile *f = new TFile("/Users/musthero/Documents/Yura/Applications/TMVA-v4.2.0/test/user.yuraic.total.tthNTUP.root");
    TTree *tree = (TTree*)f->Get("JINRTree");

    // Declare variables of interest
    Int_t m_el_isprompt;
    Int_t m_el_VeryTightLH, m_el_screwed_isprompt;
    Int_t m_el_EleIso, m_el_Z0SinTheta, m_el_Sigd0PV;
    Float_t m_el_ptcone20Dpt, m_el_etcone20Dpt;

    // Link variables of interest to the tree
    tree->SetBranchAddress("m_el_isprompt",&m_el_isprompt);
    tree->SetBranchAddress("m_el_VeryTightLH",&m_el_VeryTightLH);
    tree->SetBranchAddress("m_el_screwed_isprompt",&m_el_screwed_isprompt);
    tree->SetBranchAddress("m_el_EleIso",&m_el_EleIso);
    tree->SetBranchAddress("m_el_Z0SinTheta",&m_el_Z0SinTheta);
    tree->SetBranchAddress("m_el_Sigd0PV",&m_el_Sigd0PV);
    tree->SetBranchAddress("m_el_ptcone20Dpt",&m_el_ptcone20Dpt);
    tree->SetBranchAddress("m_el_etcone20Dpt",&m_el_etcone20Dpt);

    Double_t prompt_all = 0;
    Double_t prompt_pass = 0;
    Double_t nonprompt_all = 0;
    Double_t nonprompt_rej = 0;
    Double_t nonprompt_pass = 0;
   
    //create two histograms
    TH1F *hpx   = new TH1F("hpx","px distribution",100,-3,3);
   
    //read all entries and fill the histograms
    Long64_t counter = 0;
    Long64_t total = 0;
    Long64_t nentries = tree->GetEntries();
    for (Long64_t i=0;i<nentries;i++) {
        tree->GetEntry(i);

        counter++;
        if (counter % 100000 == 0)
            cout << "Event number " << counter << endl;

        //if (total == 120000)
        //    break;

        // Preselection cuts
        if (m_el_isprompt==1&&m_el_VeryTightLH==1&&m_el_screwed_isprompt==0) { // Signal (take from TCut in TMVAMuon.C for signal):
            prompt_all++;
        } 
        else if (m_el_isprompt==0&&m_el_VeryTightLH==1&&m_el_screwed_isprompt==0) { // Background (take from TCut in TMVAMuon.C for background):
            nonprompt_all++;
        } else {
            continue;
        }

        // Standard selection cuts
        if (m_el_VeryTightLH == 1 && m_el_EleIso == 1 && m_el_Z0SinTheta==1 && m_el_Sigd0PV==1) {
            if (m_el_isprompt==1) 
                prompt_pass++; 
            else if (m_el_isprompt==0) 
                nonprompt_pass++;
            else
                gApplication->Terminate();
        }
        
    }

    nonprompt_rej = nonprompt_all - nonprompt_pass;

    Double_t sig_eff_val = prompt_pass/prompt_all;
    Double_t bkg_rej_val = nonprompt_rej/nonprompt_all;
    Double_t sig_eff_err = (1/prompt_all) * sqrt( prompt_pass * (1 - prompt_pass/prompt_all) );
    Double_t bkg_rej_err = (1/nonprompt_all) * sqrt( nonprompt_rej * (1 - nonprompt_rej/nonprompt_all) );

    cout << "    Sig eff: " << sig_eff_val << endl;
    cout << "    Sig eff error: " << sig_eff_err << endl;
    cout << "    Bkg rej: " << bkg_rej_val << endl;
    cout << "    Bkg rej error: " << bkg_rej_err << endl;
    //cout << "    Total Entries: " << total << endl;
    cout << "    Prompt all,pass:" << prompt_all <<", "<< prompt_pass << endl;    
    cout << "    Non-prompt all,rej:" << nonprompt_all <<", "<< nonprompt_rej << endl;


     Double_t x[1], y[1], ex[1], ey[1];
     x[0] = sig_eff_val;
     y[0] = bkg_rej_val; 
     ex[0] = sig_eff_err;
     ey[0] = bkg_rej_err;


     Int_t n = 1;
     TGraphErrors* gr = new TGraphErrors(n,x,y,ex,ey);
     //gr->Draw("AC*");
     gr->SetMarkerColor(2);
     gr->SetLineColor(2);
     gr->SetLineWidth(2);
     //gr->SetMarkerStyle(20);
     //gr->SetMarkerSize(0.4);
     //gr->Draw("AC*");
     //gr->Draw();
     gr->Draw("psame");

}